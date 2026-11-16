"""Remove one batch and semester's course allocation, so it can be allocated again.

Fusion's allocation writes three things:

* ``FinalRegistration``: the allocation's own record of each allotted course.
* ``course_registration``: the same courses published for students and every
  academic screen to read.
* ``course_replacement``: for a Backlog or Improvement re-take, the link to the
  registration it replaces.

Deleting removes exactly those rows for one batch, semester and programme.
A published registration counts as the allocation's only when it matches an
allocation row (student, course, semester, registration type). Pre-registration
(``InitialRegistration``) is never touched, so the batch can be allocated
again straight away.

It refuses when the allocation is already in use: a grade exists for one of the
allotted courses, or a later record points at one of these registrations as the
one it replaces.
"""
import logging

from django.db import transaction

from ..models.erp import (
    CourseAddRequest,
    CourseRegistration,
    CourseReplacement,
    FinalRegistration,
    InitialRegistration,
    StudentGrade,
)

logger = logging.getLogger(__name__)

PROGRAMMES = ("UG", "PG", "PHD")


class ServiceError(Exception):
    def __init__(self, payload, status=400):
        super().__init__(payload.get("message", "Service error"))
        self.payload = payload
        self.status = status


def _parse(batch, semester, programme):
    try:
        batch, semester = int(batch), int(semester)
    except (TypeError, ValueError):
        raise ServiceError({"success": False, "message": "Batch and semester must be numbers."})
    programme = (programme or "").upper()
    if programme not in PROGRAMMES:
        raise ServiceError({"success": False, "message": "Programme must be UG, PG or PHD."})
    return batch, semester, programme


def _student_scope(batch, semester, programme, semester_field):
    """Filter kwargs for one batch, semester and programme."""
    return {
        "student_id__batch": batch,
        f"{semester_field}__semester_no": semester,
        "student_id__batch_id__curriculum__programme__category": programme,
    }


def _collect(batch, semester, programme):
    """The allocation rows, the registrations they published, and what depends on them."""
    allocations = FinalRegistration.objects.filter(
        **_student_scope(batch, semester, programme, "semester_id"))
    keys = set(allocations.values_list(
        "student_id_id", "course_id_id", "semester_id_id", "registration_type"))
    registrations = [
        row[0] for row in CourseRegistration.objects.filter(
            **_student_scope(batch, semester, programme, "semester"),
        ).values_list("id", "student_id_id", "course_id_id", "semester_id", "registration_type")
        if row[1:] in keys
    ]
    students = {key[0] for key in keys}
    courses = {key[1] for key in keys}

    graded = StudentGrade.objects.filter(
        batch=batch, semester=semester, roll_no__in=students, course_id__in=courses,
    ).count() if keys else 0
    later = (
        FinalRegistration.objects.filter(old_course_registration_id__in=registrations).count()
        + InitialRegistration.objects.filter(old_course_registration_id__in=registrations).count()
        + CourseAddRequest.objects.filter(old_course_registration_id__in=registrations).count()
        + CourseReplacement.objects.filter(old_course_registration_id__in=registrations).count()
    ) if registrations else 0

    return {
        "allocations": allocations,
        "registration_ids": registrations,
        "summary": {
            "batch": batch,
            "semester": semester,
            "programme": programme,
            "students": len(students),
            "allotted_courses": len(keys),
            "registrations": len(registrations),
            "replacement_links": CourseReplacement.objects.filter(
                new_course_registration_id__in=registrations).count() if registrations else 0,
            "pre_registrations": InitialRegistration.objects.filter(
                **_student_scope(batch, semester, programme, "semester_id")).count(),
            "graded": graded,
            "later_records": later,
        },
    }


def _refusal(summary):
    label = f"Batch {summary['batch']}, semester {summary['semester']} ({summary['programme']})"
    if not summary["allotted_courses"]:
        return f"{label} has no allocation to delete.", 404
    if summary["graded"]:
        return (f"{label} already has {summary['graded']} grade(s) for its allotted courses, "
                "so its allocation is in use and cannot be deleted."), 409
    if summary["later_records"]:
        return (f"{summary['later_records']} later record(s) point at {label}'s registrations "
                "as the ones they replace, so its allocation cannot be deleted."), 409
    return None, None


def summarize(batch, semester, programme):
    """What deleting would remove, and whether it is allowed."""
    batch, semester, programme = _parse(batch, semester, programme)
    summary = _collect(batch, semester, programme)["summary"]
    message, _ = _refusal(summary)
    return {"success": True, **summary, "can_delete": message is None, "reason": message or ""}


def delete_allocation(batch, semester, programme, operator):
    batch, semester, programme = _parse(batch, semester, programme)
    with transaction.atomic(using="default"):
        found = _collect(batch, semester, programme)
        summary = found["summary"]
        message, status = _refusal(summary)
        if message:
            raise ServiceError({"success": False, "message": message, **summary}, status)

        ids = found["registration_ids"]
        CourseReplacement.objects.filter(new_course_registration_id__in=ids).delete()
        CourseRegistration.objects.filter(id__in=ids).delete()
        found["allocations"].delete()

    logger.warning(
        "Allocation deleted by %s: batch %s semester %s %s, %s allotted courses, "
        "%s registrations, %s replacement links",
        operator or "unknown", batch, semester, programme,
        summary["allotted_courses"], summary["registrations"], summary["replacement_links"])
    return {
        "success": True,
        "message": (f"Deleted the allocation of Batch {batch}, semester {semester} ({programme}): "
                    f"{summary['allotted_courses']} allotted courses for {summary['students']} "
                    f"students. Pre-registration is kept; the batch can be allocated again."),
        **summary,
    }
