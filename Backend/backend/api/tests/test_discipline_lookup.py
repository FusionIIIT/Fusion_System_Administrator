from unittest.mock import patch

from django.test import SimpleTestCase

from ..services import batches as service


class FindDisciplineTests(SimpleTestCase):
    def test_blank_value_matches_nothing(self):
        with patch.object(service.Discipline.objects, "filter") as lookup:
            self.assertIsNone(service.find_discipline("  "))
            lookup.assert_not_called()

    def test_never_creates_a_discipline(self):
        with patch.object(service.Discipline.objects, "filter") as lookup, \
                patch.object(service.Discipline.objects, "create") as create:
            lookup.return_value.first.return_value = None
            self.assertIsNone(service.find_discipline("Mech"))
            create.assert_not_called()

    def test_full_name_is_normalised_before_lookup(self):
        with patch.object(service.Discipline.objects, "filter") as lookup:
            service.find_discipline("computer science and engineering")
            q = str(lookup.call_args.args[0])
            self.assertIn("Computer Science and Engineering", q)
