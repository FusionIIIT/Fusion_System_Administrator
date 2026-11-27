from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from ..services import batches as service


class EnsureUniqueStudentTests(SimpleTestCase):
    def check(self, values, existing, exclude_id=None):
        with patch.object(service.StudentBatchUpload.objects, "filter") as lookup:
            clash = lookup.return_value
            clash.exclude.return_value.first.return_value = existing
            clash.first.return_value = existing
            service.ensure_unique_student(values, exclude_id=exclude_id)
            return lookup

    def test_duplicate_roll_number_is_a_clean_error(self):
        with self.assertRaises(service.ServiceError) as ctx:
            self.check({"roll_number": "25BCS001"}, SimpleNamespace(name="A"))
        self.assertEqual(ctx.exception.payload["validation_error"], "duplicate_student")
        self.assertEqual(ctx.exception.status, 400)

    def test_duplicate_institute_email_is_rejected(self):
        with self.assertRaises(service.ServiceError):
            self.check({"institute_email": "a@iiitdmj.ac.in"}, SimpleNamespace(name="A"))

    def test_unique_values_and_blanks_pass(self):
        self.check({"roll_number": "25BCS002", "institute_email": "", "jee_app_no": None}, None)

    def test_update_excludes_the_student_being_edited(self):
        lookup = self.check({"roll_number": "25BCS001"}, None, exclude_id=7)
        lookup.return_value.exclude.assert_called_once_with(id=7)


class RequireStudentBatchTests(SimpleTestCase):
    def test_no_batch_for_programme_is_rejected(self):
        with patch.object(service, "find_discipline", return_value=SimpleNamespace(name="CSE")), \
                patch.object(service.Batch.objects, "filter") as lookup:
            lookup.return_value.first.return_value = None
            with self.assertRaises(service.ServiceError) as ctx:
                service.require_student_batch("Computer Science and Engineering", "", "pg", 2025)
        self.assertEqual(ctx.exception.payload["validation_error"], "missing_batch")

    def test_unknown_discipline_is_rejected(self):
        with patch.object(service, "find_discipline", return_value=None):
            with self.assertRaises(service.ServiceError):
                service.require_student_batch("CSE-typo", "", "ug", 2025)

    def test_matching_batch_is_returned(self):
        batch = SimpleNamespace(id=1)
        with patch.object(service, "find_discipline", return_value=SimpleNamespace(name="CSE")), \
                patch.object(service.Batch.objects, "filter") as lookup:
            lookup.return_value.first.return_value = batch
            self.assertIs(service.require_student_batch("Computer Science and Engineering", "", "ug", 2025), batch)
