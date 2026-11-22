import logging

from django.db import transaction
from django.db.models import Q

from ..models import ArchiveLog, AuthUser, GlobalsExtrainfo, GlobalsFaculty, Student

logger = logging.getLogger(__name__)

ACTIVE_STATUS = "PRESENT"
STATUS_FOR_ACTION = {"archive": "ARCHIVED", "alumni": "ALUMNI"}
ARCHIVED_STATUSES = {"ARCHIVED", "ALUMNI", "LEFT", "WITHDRAWN"}
# Withdrawn and re-admitted on Fusion's Student Status page, which keeps the
# history; nothing here overwrites it.
FUSION_OWNED_STATUSES = {"WITHDRAWN"}


class ServiceError(Exception):
    def __init__(self, payload, status=400):
        super().__init__(payload.get("message", "Service error"))
        self.payload = payload
        self.status = status


def _is_archived(user, extra):
    return (not user.is_active) or (extra.user_status in ARCHIVED_STATUSES)


def _designations(user):
    return sorted({hd.designation.name for hd in user.holds_designations.all()})


def _serialize_student(student):
    extra = student.id
    user = extra.user
    batch = student.batch_id
    return {
        "username": user.username,
        "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
        "email": user.email,
        "programme": student.programme,
        "discipline": batch.discipline.name if batch and batch.discipline else (extra.department.name if extra.department else ""),
        "batch": student.batch,
        "category": student.category,
        "gender": extra.sex,
        "curr_semester_no": student.curr_semester_no,
        "user_status": extra.user_status,
        "is_active": user.is_active,
        "archived": _is_archived(user, extra),
    }


def _serialize_faculty(faculty):
    extra = faculty.id
    user = extra.user
    return {
        "username": user.username,
        "full_name": f"{user.first_name} {user.last_name}".strip() or user.username,
        "email": user.email,
        "department": extra.department.name if extra.department else "",
        "designation": ", ".join(_designations(user)),
        "gender": extra.sex,
        "user_status": extra.user_status,
        "is_active": user.is_active,
        "archived": _is_archived(user, extra),
    }


def _status_filter(archived):
    archived_q = Q(id__user__is_active=False) | Q(id__user_status__in=ARCHIVED_STATUSES)
    return archived_q if archived else ~archived_q


def list_people(user_type, archived=False, filters=None):
    filters = filters or {}
    archived = bool(archived)

    if user_type == "faculty":
        qs = (
            GlobalsFaculty.objects.select_related("id", "id__user", "id__department")
            .prefetch_related("id__user__holds_designations__designation")
            .filter(_status_filter(archived))
        )
        if filters.get("department"):
            qs = qs.filter(id__department__name__iexact=filters["department"])
        if filters.get("gender"):
            qs = qs.filter(id__sex__iexact=filters["gender"])
        if filters.get("designation"):
            qs = qs.filter(
                id__user__holds_designations__designation__name__iexact=filters["designation"]
            ).distinct()
        rows = [_serialize_faculty(f) for f in qs]
    else:
        qs = (
            Student.objects.select_related("id", "id__user", "id__department", "batch_id", "batch_id__discipline")
            .filter(_status_filter(archived))
        )
        if filters.get("programme"):
            qs = qs.filter(programme__iexact=filters["programme"])
        if filters.get("batch"):
            qs = qs.filter(batch=filters["batch"])
        if filters.get("discipline"):
            qs = qs.filter(batch_id__discipline__name__iexact=filters["discipline"])
        if filters.get("category"):
            qs = qs.filter(category__iexact=filters["category"])
        if filters.get("gender"):
            qs = qs.filter(id__sex__iexact=filters["gender"])
        rows = [_serialize_student(s) for s in qs]

    return {"success": True, "results": rows, "count": len(rows)}


def _apply(usernames, user_type, action, new_status, active, operator):
    if not usernames:
        raise ServiceError({"success": False, "message": "No users selected."})

    done, failed, skipped = [], [], []
    with transaction.atomic():
        for uname in usernames:
            user = AuthUser.objects.filter(username__iexact=uname).first()
            extra = GlobalsExtrainfo.objects.filter(user=user).first() if user else None
            if not user or not extra:
                failed.append(uname)
                continue
            if (extra.user_status or "").strip().upper() in FUSION_OWNED_STATUSES:
                skipped.append(user.username)
                continue
            previous = extra.user_status
            extra.user_status = new_status
            extra.save(update_fields=["user_status"])
            user.is_active = active
            user.save(update_fields=["is_active"])
            ArchiveLog.objects.create(
                username=user.username,
                user_type=user_type,
                action=action,
                previous_status=previous,
                new_status=new_status,
                performed_by=operator or "",
            )
            done.append(user.username)
    return done, failed, skipped


def _skipped_note(skipped, restoring=False):
    if not skipped:
        return ""
    if restoring:
        return (f" {len(skipped)} student(s) skipped: withdrawn; re-admit them in Fusion "
                "(Student Status) instead.")
    return f" {len(skipped)} student(s) skipped: withdrawn in Fusion."


def archive_users(usernames, user_type, action, operator=""):
    if action not in STATUS_FOR_ACTION:
        raise ServiceError({"success": False, "message": "Invalid action. Use 'archive' or 'alumni'."})
    if user_type not in ("student", "faculty"):
        raise ServiceError({"success": False, "message": "Invalid user type."})

    new_status = STATUS_FOR_ACTION[action]
    # Student alumni keep their login: Fusion shows them a read-only Alumni
    # page and refuses any change to their records. That lock covers students
    # only, so faculty moved to alumni, and anyone archived, are deactivated.
    keeps_login = action == "alumni" and user_type == "student"
    done, failed, skipped = _apply(usernames, user_type, action, new_status, active=keeps_login, operator=operator)
    if keeps_login:
        outcome = "moved to alumni. They keep their login, read-only."
    elif action == "alumni":
        outcome = "moved to alumni and deactivated."
    else:
        outcome = "archived and deactivated."
    return {
        "success": True,
        "processed": done,
        "failed": failed,
        "skipped": skipped,
        "message": f"{len(done)} {user_type}(s) {outcome}" + (f" {len(failed)} not found." if failed else "")
        + _skipped_note(skipped),
    }


def restore_users(usernames, user_type, operator=""):
    if user_type not in ("student", "faculty"):
        raise ServiceError({"success": False, "message": "Invalid user type."})

    done, failed, skipped = _apply(usernames, user_type, "restore", ACTIVE_STATUS, active=True, operator=operator)
    return {
        "success": True,
        "processed": done,
        "failed": failed,
        "skipped": skipped,
        "message": f"{len(done)} {user_type}(s) restored and reactivated." + (f" {len(failed)} not found." if failed else "")
        + _skipped_note(skipped, restoring=True),
    }
