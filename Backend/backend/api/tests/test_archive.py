"""Moving students to alumni keeps their login; archiving switches it off.
All data is synthetic."""
from django.test import TestCase

from iam.tests.erp_fixture import ErpFactory

from ..models import ArchiveLog
from ..models.erp import AuthUser, Batch, Curriculum, Discipline, GlobalsExtrainfo, Programme, Student
from ..services import archive


class ArchiveTests(TestCase):
    databases = {"default", "system_db"}

    def setUp(self):
        factory = ErpFactory(seed=3)
        ug = Programme.objects.create(category="UG", name="B.Tech", programme_begin_year=2021)
        curriculum = Curriculum.objects.create(programme=ug, name="B.Tech CSE", no_of_semester=8)
        discipline = Discipline.objects.create(name="Computer Science", acronym="CSE")
        batch = Batch.objects.create(name="B.Tech", discipline=discipline, year=2021,
                                     curriculum=curriculum)
        for roll in ("21BCS001", "21BCS002"):
            factory.student(roll_no=roll)
            Student.objects.create(id=GlobalsExtrainfo.objects.get(id=roll), programme="B.Tech",
                                   batch=2021, batch_id=batch, category="GEN")

    def state(self, roll):
        user = AuthUser.objects.get(username=roll)
        return GlobalsExtrainfo.objects.get(user=user).user_status, user.is_active

    def test_alumni_keeps_login(self):
        result = archive.archive_users(["21BCS001"], "student", "alumni", "operator")
        self.assertEqual(self.state("21BCS001"), ("ALUMNI", True))
        self.assertEqual(result["message"],
                         "1 student(s) moved to alumni. They keep their login, read-only.")
        log = ArchiveLog.objects.get(username="21BCS001")
        self.assertEqual((log.action, log.previous_status, log.new_status),
                         ("alumni", "PRESENT", "ALUMNI"))

    def test_archive_deactivates(self):
        result = archive.archive_users(["21BCS001"], "student", "archive", "operator")
        self.assertEqual(self.state("21BCS001"), ("ARCHIVED", False))
        self.assertEqual(result["message"], "1 student(s) archived and deactivated.")

    def test_alumni_listed_under_the_archived_tab(self):
        archive.archive_users(["21BCS001"], "student", "alumni", "operator")
        archived = [r["username"] for r in archive.list_people("student", True)["results"]]
        active = [r["username"] for r in archive.list_people("student", False)["results"]]
        self.assertEqual((archived, active), (["21BCS001"], ["21BCS002"]))

    def test_restore_sets_present(self):
        archive.archive_users(["21BCS001"], "student", "alumni", "operator")
        archive.restore_users(["21BCS001"], "student", "operator")
        self.assertEqual(self.state("21BCS001"), ("PRESENT", True))
