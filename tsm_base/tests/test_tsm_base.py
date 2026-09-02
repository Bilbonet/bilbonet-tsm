# Copyright 2026 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestTsmBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "TSM Customer"})
        cls.child_partner = cls.env["res.partner"].create(
            {"name": "TSM Contact", "parent_id": cls.partner.id}
        )
        cls.open_stage = cls.env["tsm.task.type"].create(
            {"name": "Open", "closed": False}
        )
        cls.closed_stage = cls.env["tsm.task.type"].create(
            {"name": "Closed", "closed": True}
        )

    def _create_project(self, name="TSM Project"):
        return self.env["tsm.project"].create(
            {"name": name, "partner_id": self.partner.id}
        )

    def _create_task(self, project, name="TSM Task", stage=None, partner=None):
        return self.env["tsm.task"].create(
            {
                "name": name,
                "project_id": project.id,
                "partner_id": (partner or self.partner).id,
                "stage_id": (stage or self.open_stage).id,
            }
        )

    def test_project_count_includes_archived_tasks(self):
        project = self._create_project()
        active_task = self._create_task(project, name="Active")
        archived_task = self._create_task(
            project, name="Archived", stage=self.closed_stage
        )
        archived_task.action_inactive()

        project.invalidate_recordset(["task_count"])
        self.assertEqual(project.task_count, 2)
        self.assertTrue(active_task.active)

    def test_partner_count_includes_child_tasks(self):
        project = self._create_project()
        task = self._create_task(project, partner=self.child_partner)

        self.assertEqual(self.partner.tsm_task_count, 1)
        self.assertEqual(self.child_partner.tsm_task_count, 1)
        self.assertEqual(task.partner_id, self.child_partner)

    def test_task_archive_requires_closed_stage_and_resets_state(self):
        project = self._create_project()
        task = self._create_task(project)
        with self.assertRaises(ValidationError):
            task.action_inactive()

        task.stage_id = self.closed_stage
        task.write({"priority": "1", "kanban_state": "blocked"})
        task.action_inactive()
        self.assertFalse(task.active)
        self.assertEqual(task.priority, "0")
        self.assertEqual(task.kanban_state, "normal")

    def test_project_archive_and_delete_safeguards_include_archived_tasks(self):
        project = self._create_project()
        task = self._create_task(project, stage=self.closed_stage)
        with self.assertRaises(UserError):
            project.write({"active": False})

        task.action_inactive()
        project.write({"active": False})
        self.assertFalse(project.active)
        with self.assertRaises(UserError):
            project.unlink()

    def test_batch_copy_assigns_unique_codes(self):
        project = self._create_project()
        tasks = self._create_task(project, name="First") | self._create_task(
            project, name="Second"
        )

        copies = tasks.copy()

        self.assertEqual(len(copies), 2)
        self.assertEqual(len(set(copies.mapped("code"))), 2)
        self.assertTrue(all(name.endswith(" (copy)") for name in copies.mapped("name")))

    def test_settings_update_active_tasks_only(self):
        project = self._create_project()
        active_task = self._create_task(project, name="Active")
        archived_task = self._create_task(
            project, name="Archived", stage=self.closed_stage
        )
        archived_task.action_inactive()

        settings = self.env["res.config.settings"].create(
            {"default_tags_in_task": True}
        )
        settings.set_values()

        self.assertTrue(active_task.tags_in_task)
        self.assertFalse(archived_task.tags_in_task)

    def test_follower_assignment_uses_mail_thread_api_without_duplicates(self):
        project = self._create_project()
        follower = self.env["res.partner"].create({"name": "TSM Follower"})
        wizard = (
            self.env["follower.assignment.wizard"]
            .with_context(active_model="tsm.project", active_ids=project.ids)
            .create({"record_followers_ids": [Command.set([follower.id])]})
        )

        wizard.assign_followers()
        wizard.assign_followers()

        followers = project.message_follower_ids.filtered(
            lambda record: record.partner_id == follower
        )
        self.assertEqual(len(followers), 1)

        wizard.update_followers()
        self.assertFalse(
            project.message_follower_ids.filtered(
                lambda record: record.partner_id == follower
            )
        )

    def test_mail_actions_use_res_ids_context(self):
        project = self._create_project()
        task = self._create_task(project)

        project_context = project.action_project_send()["context"]
        task_context = task.action_task_send()["context"]

        self.assertNotIn("default_res_id", project_context)
        self.assertNotIn("default_res_id", task_context)
        self.assertEqual(project_context["default_res_ids"], [project.id])
        self.assertEqual(task_context["default_res_ids"], [task.id])
