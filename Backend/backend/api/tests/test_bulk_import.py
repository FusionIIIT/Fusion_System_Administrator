"""Tests for the bulk student CSV import (bulk_import_users).

Each row needs four writes (login account, profile, role, student record).
A row that fails part-way must leave nothing behind, must be reported with a
reason, and must be importable again once the CSV is corrected. All data below
is synthetic.
"""
import csv
from io import StringIO
from unittest import mock

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import (
    AuthUser,
    GlobalsDepartmentinfo,
    GlobalsDesignation,
    GlobalsExtrainfo,
    GlobalsHoldsdesignation,
    Student,
)

HEADER = [
    "username", "first_name", "last_name", "sex", "category", "father_name",
    "mother_name", "batch", "programme", "title", "dob", "address", "phone_no",
    "department",
]


def make_row(username="B24001", **overrides):
    values = {
        "username": username, "first_name": "Asha", "last_name": "Rao", "sex": "F",
        "category": "GEN", "father_name": "Ram", "mother_name": "Sita",
        "batch": "2024", "programme": "B.Tech.", "title": "", "dob": "01-01-2005",
        "address": "Test Street", "phone_no": "9876543210", "department": "CSE",
    }
    values.update(overrides)
    return [values[name] for name in HEADER]


def csv_upload(rows):
    out = StringIO()
    writer = csv.writer(out)
    writer.writerow(HEADER)
    writer.writerows(rows)
    return SimpleUploadedFile(
        "students.csv", out.getvalue().encode("utf-8"), content_type="text/csv"
    )


@mock.patch("api.views.users.mail_to_user")
class BulkImportStudentsTests(APITestCase):
    # `default` holds the ERP shadow tables, `system_db` the operator accounts.
    databases = {"default", "system_db"}

    def setUp(self):
        operator = User.objects.create_user(
            username="operator", password="console-test-password", is_staff=True
        )
        self.client.force_authenticate(user=operator)
        GlobalsDepartmentinfo.objects.create(name="CSE")
        GlobalsDesignation.objects.create(
            name="student", full_name="Student", type="academic"
        )

    def upload(self, rows):
        return self.client.post(
            reverse("bulk-import-users"), {"file": csv_upload(rows)}, format="multipart"
        )

    def row_counts(self):
        return (
            AuthUser.objects.count(),
            GlobalsExtrainfo.objects.count(),
            GlobalsHoldsdesignation.objects.count(),
            Student.objects.count(),
        )

    @staticmethod
    def skipped(response):
        """Return {username: reason} read from the skipped-rows CSV."""
        rows = list(csv.reader(StringIO(response.data.get("skipped_users_csv", ""))))
        return {r[0]: r[-1] for r in rows[1:] if r}

    def test_good_row_is_created(self, mail):
        before = self.row_counts()
        response = self.upload([make_row()])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["created_users"]), 1)
        self.assertEqual(response.data["skipped_users_count"], 0)
        self.assertEqual(self.row_counts(), tuple(n + 1 for n in before))
        mail.assert_called_once()

    def test_short_row_fails_cleanly_and_can_be_retried(self, mail):
        before = self.row_counts()
        response = self.upload([make_row()[:9]])
        self.assertEqual(response.data["skipped_users_count"], 1)
        self.assertEqual(self.row_counts(), before)
        self.assertFalse(AuthUser.objects.filter(username="B24001").exists())
        self.assertIn("columns", self.skipped(response)["B24001"])
        mail.assert_not_called()

        retry = self.upload([make_row()])
        self.assertEqual(len(retry.data["created_users"]), 1)
        self.assertEqual(self.row_counts(), tuple(n + 1 for n in before))

    def test_unknown_department_is_reported_and_creates_nothing(self, mail):
        before = self.row_counts()
        response = self.upload([make_row(department="NOPE")])
        self.assertEqual(response.data["skipped_users_count"], 1)
        self.assertEqual(self.row_counts(), before)
        self.assertIn("unknown department", self.skipped(response)["B24001"])

    def test_invalid_student_data_rolls_everything_back(self, mail):
        # Student.category is a plain CharField(max_length=10), so an
        # 11-character value is what makes the student serializer reject a row.
        before = self.row_counts()
        response = self.upload([make_row(category="X" * 11)])
        self.assertEqual(response.data["skipped_users_count"], 1)
        self.assertEqual(self.row_counts(), before)
        self.assertIn("invalid student data", self.skipped(response)["B24001"])

    def test_duplicate_username_is_reported(self, mail):
        self.upload([make_row()])
        after_first = self.row_counts()
        response = self.upload([make_row()])
        self.assertEqual(response.data["skipped_users_count"], 1)
        self.assertEqual(self.row_counts(), after_first)
        self.assertIn("already exists", self.skipped(response)["B24001"])

    def test_every_row_is_reported_exactly_once(self, mail):
        rows = [
            make_row("B24010"),
            make_row("B24011")[:9],
            make_row("B24012", department="NOPE"),
            make_row("B24013", category="X" * 11),
            [],  # a blank line is not a data row
            make_row("B24014"),
        ]
        response = self.upload(rows)
        created = {u["username"] for u in response.data["created_users"]}
        skipped = self.skipped(response)
        self.assertEqual(created, {"B24010", "B24014"})
        self.assertEqual(set(skipped), {"B24011", "B24012", "B24013"})
        self.assertEqual(len(created) + len(skipped), 5)
        self.assertEqual(response.data["skipped_users_count"], 3)
        self.assertTrue(all(skipped.values()))

    def test_mail_is_sent_only_for_created_users(self, mail):
        self.upload([make_row("B24020"), make_row("B24021", department="NOPE")])
        mail.assert_called_once()
        sent = mail.call_args[0][0]
        self.assertEqual([u["username"] for u in sent], ["B24020"])
