"""Whose address a request is, for the login throttle and the attempt log.

Only a trusted proxy may say who it is forwarding for. The IAM listens on
127.0.0.1, so in production every request arrives from nginx or from a Fusion
service on the same host; nginx appends the real client to X-Forwarded-For
after whatever the client wrote there itself.
"""
from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from backend.urls import LoginView as ConsoleLoginView
from iam.models import LoginAttempt
from iam.network import ClientAddressThrottle, client_address
from iam.views.auth import LoginView

NGINX = "127.0.0.1"
CLIENT = "198.51.100.7"


def request(peer, forwarded=None):
    meta = {"REMOTE_ADDR": peer}
    if forwarded is not None:
        meta["HTTP_X_FORWARDED_FOR"] = forwarded
    return RequestFactory().post("/api/iam/v1/auth/login", **meta)


class ClientAddressTests(SimpleTestCase):
    def test_a_direct_caller_cannot_claim_another_address(self):
        self.assertEqual(client_address(request("203.0.113.5", "1.2.3.4")), "203.0.113.5")

    def test_through_nginx_what_the_client_wrote_is_ignored(self):
        forwarded = f"1.2.3.4, 5.6.7.8, {CLIENT}"
        self.assertEqual(client_address(request(NGINX, forwarded)), CLIENT)

    def test_a_service_on_this_host_can_say_who_it_signs_in_for(self):
        self.assertEqual(client_address(request(NGINX, CLIENT)), CLIENT)

    def test_with_no_header_it_is_the_peer(self):
        self.assertEqual(client_address(request("203.0.113.5")), "203.0.113.5")

    @override_settings(IAM_TRUSTED_PROXIES=["127.0.0.1", "10.0.0.0/8"])
    def test_a_chain_of_trusted_proxies_is_walked_back(self):
        forwarded = f"1.2.3.4, {CLIENT}, 10.0.0.5"
        self.assertEqual(client_address(request("10.0.0.9", forwarded)), CLIENT)

    def test_only_trusted_hops_means_the_earliest_one(self):
        self.assertEqual(client_address(request(NGINX, "127.0.0.1, ::1")), "127.0.0.1")

    def test_a_malformed_hop_is_not_trusted_past(self):
        forwarded = f"{CLIENT}, not-an-address"
        self.assertEqual(client_address(request(NGINX, forwarded)), NGINX)

    def test_ipv6_is_written_one_way(self):
        self.assertEqual(client_address(request(NGINX, "2001:DB8::0001")), "2001:db8::1")

    def test_both_login_views_use_it(self):
        self.assertIn(ClientAddressThrottle, LoginView.throttle_classes)
        self.assertIn(ClientAddressThrottle, ConsoleLoginView.throttle_classes)


class LoginThrottleTests(TestCase):
    databases = {"default", "system_db"}

    def setUp(self):
        cache.clear()

    def login(self, n, forwarded):
        return APIClient(REMOTE_ADDR=NGINX).post(
            "/api/iam/v1/auth/login", {"username": f"nobody{n}", "password": "x"},
            format="json", HTTP_X_FORWARDED_FOR=forwarded)

    def test_a_fresh_fake_address_each_time_no_longer_dodges_the_limit(self):
        codes = [self.login(n, f"10.9.8.{n}, {CLIENT}").status_code for n in range(6)]
        self.assertEqual(codes[:5], [401] * 5)
        self.assertEqual(codes[5], 429)

    def test_two_real_clients_behind_nginx_keep_their_own_limits(self):
        for n in range(5):
            self.login(n, CLIENT)
        self.assertEqual(self.login(9, "203.0.113.20").status_code, 401)

    def test_the_attempt_log_records_the_real_address(self):
        self.login(1, f"1.2.3.4, {CLIENT}")
        self.assertEqual(LoginAttempt.objects.get().ip, CLIENT)
