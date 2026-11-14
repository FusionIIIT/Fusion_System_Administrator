"""Let one locked-out person sign in now, instead of waiting out the lock.

    manage.py unlock_login --user stu00001

--user is the username as they type it; case does not matter. The unlock is
recorded in the login-attempt log like any other outcome, so it is audited,
and failures after it are counted afresh.
"""
from django.core.management.base import BaseCommand, CommandError

from iam import services


class Command(BaseCommand):
    help = "Clear one username's failed sign-ins so a locked-out person can sign in now"

    def add_arguments(self, parser):
        parser.add_argument("--user", required=True, help="The username they sign in with")

    def handle(self, *args, **opts):
        key = services.login_key(opts["user"])
        if not key:
            raise CommandError("--user cannot be empty")
        cleared = services.unlock(key)
        if cleared:
            self.stdout.write(self.style.SUCCESS(
                f"Cleared {cleared} recent failed sign-in(s) for {key}; they can sign in now."))
        else:
            self.stdout.write(f"{key} has no recent failed sign-ins; nothing to clear.")
