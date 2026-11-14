"""assign_role writes the grant where the IAM reads designations from, so it lasts.

It used to write the projection alone. Login re-reads a stale projection from
the ERP and sync_identity rebuilds it, so the grant vanished within half an hour.
"""
from io import StringIO

from django.core.management import call_command

from api.models.erp import GlobalsDesignation, GlobalsHoldsdesignation, GlobalsModuleaccess
from iam import services, sync
from iam.tests.erp_fixture import ErpFactory, ErpSchemaTestCase


def assign(*args: str) -> str:
    out = StringIO()
    call_command("assign_role", *args, stdout=out)
    return out.getvalue()


class AssignRoleTests(ErpSchemaTestCase):
    def setUp(self):
        self.erp = ErpFactory(seed=21)
        self.person = self.erp.employee(kind="staff")
        sync.sync_all()

    def held(self) -> set[str]:
        return set(services.designations_for(self.person.id))

    def grant(self, designation: str = "placement_officer") -> str:
        return assign("--user", self.person.username, "--designation", designation)

    def test_a_grant_is_live_at_once(self):
        self.grant()
        self.assertIn("placement_officer", self.held())

    def test_a_grant_outlasts_the_refresh_a_stale_login_runs(self):
        self.grant()
        sync.refresh_designations(self.person.id)
        self.assertIn("placement_officer", self.held())

    def test_a_grant_outlasts_a_full_sync(self):
        self.grant()
        sync.sync_all()
        self.assertIn("placement_officer", self.held())

    def test_a_new_name_is_created_in_the_erp_with_its_module_access_row(self):
        self.grant("Leave Approver")
        designation = GlobalsDesignation.objects.get(name="Leave Approver")
        self.assertEqual((designation.type, designation.basic), ("administrative", False))
        self.assertTrue(GlobalsModuleaccess.objects.filter(designation="Leave Approver").exists())

    def test_an_existing_designation_is_reused(self):
        self.erp.designation("Registrar")
        self.grant("Registrar")
        self.assertEqual(GlobalsDesignation.objects.filter(name="Registrar").count(), 1)
        self.assertFalse(GlobalsModuleaccess.objects.filter(designation="Registrar").exists())

    def test_granting_twice_writes_one_row(self):
        self.grant()
        self.assertIn("Already held", self.grant())
        self.assertEqual(GlobalsHoldsdesignation.objects.filter(
            working_id=self.person.id, designation__name="placement_officer").count(), 1)

    def test_removing_takes_it_out_of_the_erp_and_the_session(self):
        self.grant()
        out = assign("--user", self.person.username, "--designation", "placement_officer",
                     "--remove")
        self.assertIn("Revoked", out)
        self.assertNotIn("placement_officer", self.held())
        self.assertFalse(GlobalsHoldsdesignation.objects.filter(
            working_id=self.person.id, designation__name="placement_officer").exists())
        sync.refresh_designations(self.person.id)
        self.assertNotIn("placement_officer", self.held())
