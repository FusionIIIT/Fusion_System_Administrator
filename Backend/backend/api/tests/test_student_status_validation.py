from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from ..services import batches as service


class ReportedStatusTests(SimpleTestCase):
    def test_unknown_status_is_rejected(self):
        with self.assertRaises(service.ServiceError):
            service.validate_reported_status("anything-goes")

    def test_known_status_is_accepted(self):
        service.validate_reported_status("NOT_REPORTED")

    def test_general_update_cannot_bypass_the_status_check(self):
        student = SimpleNamespace(id=1)
        with patch.object(service.StudentBatchUpload.objects, "filter") as lookup:
            lookup.return_value.first.return_value = student
            with self.assertRaises(service.ServiceError):
                service.update_student(1, {"reportedStatus": "anything-goes"})
        self.assertFalse(hasattr(student, "reported_status"))


class SkipDuplicatesTests(SimpleTestCase):
    def upload(self, **extra):
        payload = {"students": [{"Name": "A", "Institute Roll Number": "25BCS001"}], "programme_type": "ug", **extra}
        with patch.object(service, "resolve_year", return_value=(2025, "2025-26")), \
                patch.object(service, "require_curriculum"), patch.object(service, "require_batches"), \
                patch.object(service, "is_duplicate", return_value=(True, "Roll Number 25BCS001 already exists for A")) as dup:
            return service.save_students(payload), dup

    def test_duplicates_are_skipped_by_default(self):
        result, dup = self.upload()
        dup.assert_called_once()
        self.assertEqual(result["data"]["skipped_duplicates"], 1)
        self.assertEqual(result["data"]["successful_uploads"], 0)

    def test_explicit_opt_out_still_works(self):
        with patch.object(service, "allocate", return_value=[]):
            result, dup = self.upload(skip_duplicates=False)
        dup.assert_not_called()
