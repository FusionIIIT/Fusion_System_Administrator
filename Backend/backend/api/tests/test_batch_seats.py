from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from ..services import batches as service


def make_batch(total_seats):
    return SimpleNamespace(id=1, name="B.Tech", year=2025, total_seats=total_seats,
                           discipline=SimpleNamespace(name="Computer Science and Engineering", acronym="CSE"))


class ReserveSeatTests(SimpleTestCase):
    def reserve(self, total_seats, filled):
        batch = make_batch(total_seats)
        with patch.object(service.Batch.objects, "select_for_update") as lock, \
                patch.object(service, "filled_seats", return_value=filled):
            lock.return_value.select_related.return_value.get.return_value = batch
            service.reserve_seat(batch)

    def test_rejects_once_seats_are_filled(self):
        with self.assertRaises(service.ServiceError) as ctx:
            self.reserve(total_seats=60, filled=60)
        self.assertEqual(ctx.exception.payload["validation_error"], "batch_full")

    def test_allows_while_seats_remain(self):
        self.reserve(total_seats=60, filled=59)

    def test_unset_seat_count_is_unlimited(self):
        self.reserve(total_seats=0, filled=500)


class FilledSeatsTests(SimpleTestCase):
    def test_counts_staged_admissions_not_registered_students(self):
        batch = make_batch(60)
        with patch.object(service, "batch_roster") as roster:
            roster.return_value.count.return_value = 150
            self.assertEqual(service.filled_seats(batch), 150)
