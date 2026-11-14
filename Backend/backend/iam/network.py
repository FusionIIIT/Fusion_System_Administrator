"""Whose address a request is, for the login throttle and the attempt log.

Only a trusted proxy may say who it is forwarding for. In production the IAM
listens on 127.0.0.1 and every request comes from nginx or from a Fusion service
on the same host. nginx appends the real client to X-Forwarded-For after whatever
the client wrote there itself, so the header is read from the right, past the
trusted hops, and the first address that is not one of them is the client. A
request from anywhere else ignores the header altogether.

IAM_TRUSTED_PROXIES lists the proxies' addresses or networks (loopback by
default). Add nginx's address there if it ever runs on another host.
"""
from __future__ import annotations

import ipaddress
from functools import lru_cache

from django.conf import settings
from rest_framework.throttling import ScopedRateThrottle

Address = ipaddress.IPv4Address | ipaddress.IPv6Address


@lru_cache(maxsize=8)
def _networks(entries: tuple[str, ...]) -> tuple[ipaddress._BaseNetwork, ...]:
    return tuple(ipaddress.ip_network(e.strip(), strict=False) for e in entries if e.strip())


def _parse(value: str | None) -> Address | None:
    try:
        return ipaddress.ip_address((value or "").strip())
    except ValueError:
        return None


def _trusted(address: Address) -> bool:
    proxies = getattr(settings, "IAM_TRUSTED_PROXIES", ("127.0.0.1", "::1"))
    return any(address in network for network in _networks(tuple(proxies)))


def client_address(request) -> str | None:
    meta = getattr(request, "META", request)
    peer = _parse(meta.get("REMOTE_ADDR"))
    if peer is None or not _trusted(peer):
        return str(peer) if peer else meta.get("REMOTE_ADDR")

    hops = [h for h in meta.get("HTTP_X_FORWARDED_FOR", "").split(",") if h.strip()]
    earliest = peer
    for hop in reversed(hops):
        address = _parse(hop)
        if address is None:
            return str(peer)                # never trust past a hop that is not an address
        if not _trusted(address):
            return str(address)
        earliest = address
    return str(earliest)


class ClientAddressThrottle(ScopedRateThrottle):
    """ScopedRateThrottle keyed by client_address, not by the raw header."""

    def get_ident(self, request):
        return client_address(request) or ""
