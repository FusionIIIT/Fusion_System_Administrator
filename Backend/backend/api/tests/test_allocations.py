"""Deleting one batch and semester's course allocation. All data is synthetic."""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from iam.tests.erp_fixture import ErpFactory

from ..models.erp import (
    Batch,
    Course,
    CourseAddRequest,
    CourseRegistration,
    CourseReplacement,
    Curriculum,
    Discipline,
    FinalRegistration,
    GlobalsExtrainfo,
    InitialRegistration,
    Programme,
    Semester,
    Student,
    StudentGrade,
)


class AllocationTests(APITestCase):
    databases = {"default", "system_db"}

    def setUp(self):
        operator = User.objects.create_user(username="operator", password="console-test", is_staff=True)
        self.client.force_authenticate(user=operator)

        factory = ErpFactory(seed=1)
        ug = Programme.objects.create(category="UG", name="B.Tech", programme_begin_year=2024)
        curriculum = Curriculum.objects.create(programme=ug, name="B.Tech CSE", no_of_semester=8)
        discipline = Discipline.objects.create(name="Computer Science", acronym="CSE")
        batch = Batch.objects.create(name="B.Tech", discipline=discipline, year=2024, curriculum=curriculum)
        self.sem6 = Semester.objects.create(curriculum=curriculum, semester_no=6)
        self.sem4 = Semester.objects.create(curriculum=curriculum, semester_no=4)
        self.core = Course.objects.create(code="CS3001", name="Compilers", credit=4)
        self.elective = Course.objects.create(code="CS3002", name="Graphics", credit=3)
        self.students = []
        for roll in ("24BCS001", "24BCS002"):
            factory.student(roll_no=roll)
            self.students.append(Student.objects.create(
                id=GlobalsExtrainfo.objects.get(id=roll), programme="B.Tech", batch=2024,
                batch_id=batch, category="GEN"))
        for student in self.students:
            InitialRegistration.objects.create(student_id=student, semester_id=self.sem6)
            for course in (self.core, self.elective):
                self.allot(student, course)
        # A re-take of a semester 4 course, allotted in semester 6.
        first, _ = self.students
        self.earlier = CourseRegistration.objects.create(
            student_id=first, course_id=self.elective, semester=self.sem4,
            registration_type="Regular", session="2025-26", semester_type="Even Semester")
        FinalRegistration.objects.create(
            student_id=first, semester_id=self.sem6, course_id=self.core,
            registration_type="Backlog", old_course_registration=self.earlier)
        self.retake = CourseRegistration.objects.create(
            student_id=first, course_id=self.core, semester=self.sem6,
            registration_type="Backlog", session="2026-27", semester_type="Even Semester")
        CourseReplacement.objects.create(old_course_registration=self.earlier,
                                         new_course_registration=self.retake)

    def allot(self, student, course):
        FinalRegistration.objects.create(student_id=student, semester_id=self.sem6, course_id=course)
        return CourseRegistration.objects.create(
            student_id=student, course_id=course, semester=self.sem6,
            registration_type="Regular", session="2026-27", semester_type="Even Semester")

    def summary(self, **params):
        query = {"batch": 2024, "semester": 6, "programme": "UG", **params}
        return self.client.get(reverse("allocation-summary"), query).json()

    def delete(self, **params):
        body = {"batch": 2024, "semester": 6, "programme": "UG", **params}
        return self.client.post(reverse("allocation-delete"), body, format="json")

    def test_the_summary_counts_what_would_be_removed(self):
        summary = self.summary()
        self.assertEqual(
            {k: summary[k] for k in ("students", "allotted_courses", "registrations",
                                     "replacement_links", "pre_registrations", "can_delete")},
            {"students": 2, "allotted_courses": 5, "registrations": 5,
             "replacement_links": 1, "pre_registrations": 2, "can_delete": True})

    def test_delete_removes_the_allocation_and_keeps_pre_registration(self):
        response = self.delete()
        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(FinalRegistration.objects.filter(semester_id=self.sem6).exists())
        self.assertFalse(CourseRegistration.objects.filter(semester=self.sem6).exists())
        self.assertFalse(CourseReplacement.objects.exists())
        self.assertEqual(InitialRegistration.objects.filter(semester_id=self.sem6).count(), 2)

    def test_delete_leaves_other_semesters_alone(self):
        self.delete()
        self.assertTrue(CourseRegistration.objects.filter(pk=self.earlier.pk).exists())

    def test_a_registration_the_allocation_did_not_make_is_kept(self):
        added = CourseRegistration.objects.create(
            student_id=self.students[1], course_id=self.core, semester=self.sem6,
            registration_type="Extra Credits", session="2026-27", semester_type="Even Semester")
        self.delete()
        self.assertTrue(CourseRegistration.objects.filter(pk=added.pk).exists())

    def test_a_grade_for_an_allotted_course_blocks_the_delete(self):
        StudentGrade.objects.create(course_id=self.core, semester=6, year=2027,
                                    roll_no="24BCS001", grade="A", batch=2024)
        response = self.delete()
        self.assertEqual(response.status_code, 409)
        self.assertIn("grade", response.json()["message"])
        self.assertEqual(FinalRegistration.objects.filter(semester_id=self.sem6).count(), 5)

    def test_a_later_record_pointing_here_blocks_the_delete(self):
        published = CourseRegistration.objects.filter(semester=self.sem6, registration_type="Regular").first()
        CourseAddRequest.objects.create(old_course_registration=published)
        response = self.delete()
        self.assertEqual(response.status_code, 409)
        self.assertTrue(CourseRegistration.objects.filter(pk=published.pk).exists())

    def test_nothing_allotted_is_not_found(self):
        self.delete()
        response = self.delete()
        self.assertEqual(response.status_code, 404)
        self.assertIn("no allocation", response.json()["message"])

    def test_bad_input_is_refused(self):
        self.assertEqual(self.delete(programme="BTECH").status_code, 400)
        self.assertEqual(self.delete(batch="twenty").status_code, 400)

    def test_only_a_staff_operator_may_delete(self):
        plain = User.objects.create_user(username="viewer", password="console-test")
        self.client.force_authenticate(user=plain)
        self.assertEqual(self.delete().status_code, 403)
        self.assertEqual(FinalRegistration.objects.filter(semester_id=self.sem6).count(), 5)
