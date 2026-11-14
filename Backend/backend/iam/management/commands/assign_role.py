"""Grant or revoke one designation on one ERP-user account.

    manage.py assign_role --user u1001 --designation "Leave Approver"
    manage.py assign_role --user u1001 --designation "Leave Approver" --remove

The grant is written to the ERP's globals_holdsdesignation, exactly as the
operator console's update-user-roles does, and the IAM's projection is then
re-read from it. Writing the projection alone did not last: login re-reads a
stale projection from the ERP and sync_identity rebuilds it, so the grant was
gone within half an hour.

--user accepts a username or an erp_user_id. --designation is free text: a
name the ERP does not have yet is created in globals_designation, with an
all-false globals_moduleaccess row as the console's create-role adds, so a
module's own invented role needs no setup first. It does not have to be in the
IamRole catalogue (iam/rbac.py) either.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction

from api.models.erp import GlobalsDesignation, GlobalsHoldsdesignation, GlobalsModuleaccess
from iam import services, sync
from iam.models import IamUser

#: The shape most designations in the ERP have; an invented role is an office post.
NEW_DESIGNATION = {"type": "administrative", "basic": False}


class Command(BaseCommand):
    help = "Grant or revoke a designation on one ERP-user account, in the ERP itself"

    def add_arguments(self, parser):
        parser.add_argument("--user", required=True,
                            help="Username or erp_user_id")
        parser.add_argument("--designation", required=True,
                            help="Designation name, e.g. 'Leave Approver'")
        parser.add_argument("--remove", action="store_true",
                            help="Revoke instead of grant")

    def _resolve_user(self, value):
        user = (IamUser.objects.filter(erp_user_id=value).first()
                if value.isdigit() else None)
        if user is None:
            user = IamUser.objects.filter(username__iexact=value).first()
        if user is None:
            raise CommandError(f"No ERP user matches {value!r}")
        return user

    def _designation(self, name):
        found = GlobalsDesignation.objects.filter(name=name).first()
        if found is not None:
            return found, False
        made = GlobalsDesignation.objects.create(name=name, full_name=name, **NEW_DESIGNATION)
        if not GlobalsModuleaccess.objects.filter(designation=name).exists():
            GlobalsModuleaccess.objects.create(designation=name, **{
                field.name: False for field in GlobalsModuleaccess._meta.fields
                if isinstance(field, models.BooleanField)})
        return made, True

    def handle(self, *args, **opts):
        user = self._resolve_user(opts["user"])
        name = opts["designation"].strip()
        if not name:
            raise CommandError("--designation cannot be empty")
        limit = GlobalsDesignation._meta.get_field("name").max_length
        if len(name) > limit:
            raise CommandError(f"--designation is longer than the ERP allows ({limit})")

        with transaction.atomic(using="default"):
            if opts["remove"]:
                removed, _ = GlobalsHoldsdesignation.objects.filter(
                    working_id=user.erp_user_id, designation__name=name).delete()
                verb, created_name = ("Revoked" if removed else "Was not held:"), False
            else:
                designation, created_name = self._designation(name)
                _, created = GlobalsHoldsdesignation.objects.get_or_create(
                    designation=designation, user_id=user.erp_user_id,
                    working_id=user.erp_user_id)
                verb = "Granted" if created else "Already held:"

        if sync.refresh_designations(user.erp_user_id) is None:
            raise CommandError("Written to the ERP, but the IAM could not re-read it; "
                               "run sync_identity before signing in.")

        self.stdout.write(self.style.SUCCESS(f"{verb} {name!r} on {user.username}"))
        if created_name:
            self.stdout.write(f"  {name!r} was new, so it was added to the ERP's designations")
        held = services.designations_for(user.erp_user_id)
        if not opts["remove"] and name not in held:
            self.stdout.write(self.style.WARNING(
                f"  {name!r} is in the ERP, but the role policy keeps it off a {user.kind}'s "
                "session (IAM_ENFORCE_ROLE_POLICY)"))
        self.stdout.write(f"  now holds: {', '.join([user.kind, *held])}")
