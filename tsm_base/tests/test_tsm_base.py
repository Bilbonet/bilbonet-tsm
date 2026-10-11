# Copyright 2026 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user


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
        cls.project_user = new_test_user(
            cls.env,
            login="tsm_project_user",
            groups="tsm_base.group_tsm_user",
            context={"no_reset_password": True},
            company_id=cls.env.company.id,
            company_ids=[Command.set(cls.env.company.ids)],
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

    def test_task_archive_requires_closed_stage_and_resets_status(self):
        project = self._create_project()
        task = self._create_task(project)
        task.write({"priority": "1", "task_status": "done"})
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            task.action_inactive()

        self.assertTrue(task.active)
        self.assertEqual(task.task_status, "done")
        self.assertEqual(task.priority, "1")
        task.stage_id = self.closed_stage
        task.action_inactive()
        self.assertFalse(task.active)
        self.assertEqual(task.priority, "0")
        self.assertEqual(task.task_status, "to_define")

        task.stage_id = self.open_stage
        task.action_active()
        self.assertTrue(task.active)
        self.assertEqual(task.task_status, "to_define")

    def test_task_status_does_not_change_workflow_or_dates(self):
        task = self._create_task(self._create_project())
        self.assertEqual(task.task_status, "to_define")
        task.write(
            {
                "priority": "1",
                "date_start": "2026-01-01",
                "date_assign": "2026-01-02",
                "date_deadline": "2026-01-10",
                "date_end": "2026-01-09",
            }
        )
        unchanged_fields = [
            "stage_id",
            "closed",
            "active",
            "priority",
            "date_start",
            "date_assign",
            "date_deadline",
            "date_end",
        ]
        original = task.read(unchanged_fields)
        for status in ("on_track", "at_risk", "off_track", "done", "on_hold"):
            task.write({"task_status": status})
            self.assertEqual(task.read(unchanged_fields), original)
            self.assertEqual(task.task_status, status)

    def test_batch_archive_preserves_all_tasks_when_a_stage_is_open(self):
        project = self._create_project()
        closed_task = self._create_task(project, stage=self.closed_stage)
        open_task = self._create_task(project, name="Open task")
        tasks = closed_task | open_task
        tasks.write({"priority": "1", "task_status": "done"})

        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            tasks.action_inactive()

        self.assertTrue(all(tasks.mapped("active")))
        self.assertEqual(tasks.mapped("task_status"), ["done", "done"])
        self.assertEqual(tasks.mapped("priority"), ["1", "1"])

        open_task.stage_id = self.closed_stage
        tasks.action_inactive()
        self.assertFalse(any(tasks.mapped("active")))
        self.assertEqual(tasks.mapped("task_status"), ["to_define", "to_define"])
        self.assertEqual(tasks.mapped("priority"), ["0", "0"])
        tasks.action_active()
        self.assertTrue(all(tasks.mapped("active")))
        self.assertEqual(tasks.mapped("task_status"), ["to_define", "to_define"])

    def test_task_status_tracking_includes_archive_reset(self):
        task = self._create_task(self._create_project(), stage=self.closed_stage)
        labels = dict(task._fields["task_status"]._description_selection(self.env))
        self.env.flush_all()
        self.env.cr.precommit.run()
        original_messages = task.message_ids

        task.write({"task_status": "done"})
        self.env.flush_all()
        self.env.cr.precommit.run()
        messages = task.message_ids - original_messages
        self.assertEqual(len(messages), 1)
        tracking = messages.tracking_value_ids.filtered(
            lambda value: value.field_id.name == "task_status"
        )
        self.assertEqual(len(tracking), 1)
        self.assertEqual(tracking.old_value_char, labels["to_define"])
        self.assertEqual(tracking.new_value_char, labels["done"])

        original_messages = task.message_ids
        task.write({"task_status": "done"})
        self.env.flush_all()
        self.env.cr.precommit.run()
        self.assertFalse(task.message_ids - original_messages)

        task.action_inactive()
        self.env.flush_all()
        self.env.cr.precommit.run()
        messages = task.message_ids - original_messages
        self.assertEqual(len(messages), 1)
        tracking = messages.tracking_value_ids.filtered(
            lambda value: value.field_id.name == "task_status"
        )
        self.assertEqual(len(tracking), 1)
        self.assertEqual(tracking.old_value_char, labels["done"])
        self.assertEqual(tracking.new_value_char, labels["to_define"])

        original_messages = task.message_ids
        task.action_active()
        self.env.flush_all()
        self.env.cr.precommit.run()
        messages = task.message_ids - original_messages
        self.assertFalse(
            messages.tracking_value_ids.filtered(
                lambda value: value.field_id.name == "task_status"
            )
        )

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

    def test_project_safeguards_include_hidden_tasks(self):
        project = self._create_project()
        empty_project = self._create_project(name="Empty project")
        projects = project | empty_project
        projects.with_context(mail_auto_subscribe_no_notify=True).write(
            {
                "user_id": self.project_user.id,
                "privacy_visibility": "employees",
                "priority": "1",
            }
        )
        task = self._create_task(project, stage=self.closed_stage)
        task.write({"user_id": self.env.user.id, "privacy_visibility": "followers"})
        user_projects = projects.with_user(self.project_user)
        self.assertFalse(self.project_user.has_group("tsm_base.group_tsm_manager"))
        user_projects.check_access("write")
        user_projects.check_access("unlink")
        self.assertNotIn(self.project_user.partner_id, task.message_partner_ids)
        self.assertFalse(
            self.env["tsm.task"]
            .with_user(self.project_user)
            .with_context(active_test=False)
            .search([("id", "=", task.id)])
        )
        # Discard the relation cached during the administrator's fixture setup.
        projects.invalidate_recordset(["task_ids"])
        self.assertFalse(user_projects.task_ids)

        with self.assertRaises(UserError), self.env.cr.savepoint():
            user_projects.write({"active": False})
        self.assertTrue(all(projects.mapped("active")))
        self.assertEqual(projects.mapped("priority"), ["1", "1"])
        with self.assertRaises(UserError), self.env.cr.savepoint():
            user_projects.unlink()
        self.assertEqual(projects.exists(), projects)
        self.assertEqual(task.project_id, project)

        task.action_inactive()
        user_projects.with_context(active_test=False).write({"active": False})
        self.assertFalse(any(projects.mapped("active")))
        self.assertEqual(projects.mapped("priority"), ["0", "0"])
        with self.assertRaises(UserError), self.env.cr.savepoint():
            user_projects.with_context(active_test=False).unlink()
        self.assertEqual(task.project_id, project)

        task.unlink()
        user_projects.with_context(active_test=False).unlink()
        self.assertFalse(projects.exists())

    def test_project_safeguards_check_project_access_first(self):
        project = self._create_project()
        project.write({"user_id": self.env.user.id, "privacy_visibility": "employees"})
        task = self._create_task(project)
        task.write({"user_id": self.env.user.id, "privacy_visibility": "followers"})
        user_project = project.with_user(self.project_user)
        user_project.check_access("read")
        self.assertFalse(task.with_user(self.project_user).has_access("read"))
        # Reload the relation with the limited user's record rules.
        project.invalidate_recordset(["task_ids"])
        self.assertFalse(user_project.task_ids)

        with self.assertRaises(AccessError), self.env.cr.savepoint():
            user_project.write({"active": False})
        with self.assertRaises(AccessError), self.env.cr.savepoint():
            user_project.unlink()
        self.assertTrue(project.active)
        self.assertEqual(project.exists(), project)
        self.assertEqual(task.project_id, project)

    def test_batch_copy_assigns_unique_codes(self):
        project = self._create_project()
        tasks = self._create_task(project, name="First") | self._create_task(
            project, name="Second"
        )
        tasks.write({"task_status": "done"})

        copies = tasks.copy()

        self.assertEqual(len(copies), 2)
        self.assertEqual(len(set(copies.mapped("code"))), 2)
        self.assertTrue(all(name.endswith(" (copy)") for name in copies.mapped("name")))
        self.assertEqual(copies.mapped("task_status"), ["to_define", "to_define"])

    def test_settings_update_active_tasks_only(self):
        project = self._create_project()
        active_task = self._create_task(project, name="Active")
        archived_task = self._create_task(
            project, name="Archived", stage=self.closed_stage
        )
        # Do not inherit the tag default configured in the database.
        (active_task | archived_task).write({"tags_in_task": False})
        archived_task.action_inactive()

        settings = self.env["res.config.settings"].create(
            {"default_tags_in_task": True}
        )
        settings.set_values()

        self.assertTrue(active_task.tags_in_task)
        self.assertFalse(archived_task.tags_in_task)

        archived_task.write({"tags_in_task": True})
        settings.default_tags_in_task = False
        settings.set_values()

        self.assertFalse(active_task.tags_in_task)
        self.assertTrue(archived_task.tags_in_task)

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
