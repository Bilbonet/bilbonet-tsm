# Copyright 2026 Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime

from freezegun import freeze_time

from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase, new_test_user


class TsmTimesheetCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user = new_test_user(
            cls.env,
            login="tsm_timesheet_user",
            groups="tsm_base.group_tsm_user",
            context={"no_reset_password": True},
            company_id=cls.env.company.id,
            company_ids=[Command.set(cls.env.company.ids)],
            tz=False,
        )
        cls.partner = cls.env["res.partner"].create({"name": "Timesheet customer"})
        cls.project = cls.env["tsm.project"].create(
            {
                "name": "Timesheet project",
                "partner_id": cls.partner.id,
                "privacy_visibility": "employees",
            }
        )
        cls.open_stage = cls.env["tsm.task.type"].create({"name": "Open"})
        cls.closed_stage = cls.env["tsm.task.type"].create(
            {"name": "Closed", "closed": True}
        )
        cls.task = cls.env["tsm.task"].create(
            {
                "name": "Timesheet task",
                "project_id": cls.project.id,
                "partner_id": cls.partner.id,
                "stage_id": cls.open_stage.id,
                "user_id": cls.user.id,
                "privacy_visibility": "employees",
            }
        )
        cls.timesheets = cls.env["tsm.task.timesheet"]
        cls.tags = cls.env["tsm.task.timesheet.tags"]
        cls.other_partner = cls.env["res.partner"].create({"name": "Other customer"})
        cls.other_project = cls.env["tsm.project"].create(
            {
                "name": "Other project",
                "partner_id": cls.other_partner.id,
                "privacy_visibility": "employees",
            }
        )
        cls.other_task = cls.env["tsm.task"].create(
            {
                "name": "Other task",
                "project_id": cls.other_project.id,
                "partner_id": cls.other_partner.id,
                "stage_id": cls.open_stage.id,
                "user_id": cls.user.id,
                "privacy_visibility": "employees",
            }
        )

    def _create_line(self, **values):
        return self.timesheets.create(
            {"task_id": self.task.id, "name": "Work", **values}
        )


@tagged("post_install", "-at_install")
class TestTsmProjectTaskSelection(TsmTimesheetCase):
    def test_select_project_before_task(self):
        with Form(
            self.timesheets.with_user(self.user),
            view="tsm_task_timesheet.tsm_task_timesheet_line_form",
        ) as line_form:
            line_form.project_id = self.other_project
            self.assertFalse(line_form.task_id)
            line_form.task_id = self.other_task
            self.assertEqual(line_form.project_id, self.other_project)
            self.assertEqual(line_form.task_partner_id, self.other_partner)
        self.assertEqual(line_form.record.project_id, self.other_project)

    def test_select_task_before_project_and_replace_selection(self):
        with Form(
            self.timesheets.with_user(self.user),
            view="tsm_task_timesheet.tsm_task_timesheet_line_form",
        ) as line_form:
            line_form.task_id = self.task
            self.assertEqual(line_form.project_id, self.project)
            self.assertEqual(line_form.task_partner_id, self.partner)
            line_form.task_id = self.env["tsm.task"]
            self.assertEqual(line_form.project_id, self.project)
            self.assertFalse(line_form.task_partner_id)
            line_form.project_id = self.other_project
            line_form.task_id = self.other_task
        self.assertEqual(line_form.record.task_id, self.other_task)
        self.assertEqual(self.task.project_id, self.project)

    def test_clearing_project_clears_incompatible_task_in_form(self):
        line = self._create_line()
        line_form = Form(
            line.with_user(self.user),
            view="tsm_task_timesheet.tsm_task_timesheet_line_form",
        )
        line_form.project_id = self.env["tsm.project"]
        self.assertFalse(line_form.task_id)
        self.assertFalse(line_form.task_partner_id)
        self.assertEqual(line.task_id, self.task)

    def test_project_defaults_in_batch(self):
        lines = self.timesheets.with_user(self.user).create(
            [
                {"task_id": self.task.id},
                {"task_id": self.other_task.id},
                {"project_id": self.other_project.id},
            ]
        )
        self.assertEqual(
            [line.project_id.id for line in lines],
            [self.project.id, self.other_project.id, self.other_project.id],
        )
        self.assertFalse(lines[2].task_id)

    def test_reject_incompatible_task_project(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.timesheets.with_user(self.user).create(
                {"task_id": self.task.id, "project_id": self.other_project.id}
            )
        line = self._create_line()
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            line.with_user(self.user).project_id = self.other_project
        self.assertEqual(line.project_id, self.project)
        self.assertEqual(self.task.project_id, self.project)
        line.with_user(self.user).task_id = self.other_task
        self.assertEqual(line.project_id, self.other_project)
        self.assertEqual(line.task_partner_id, self.other_partner)

    def test_task_project_change_updates_existing_lines(self):
        line = self._create_line(amount=1.5)
        self.task.with_user(self.user).project_id = self.other_project
        self.assertEqual(line.task_id, self.task)
        self.assertEqual(line.project_id, self.other_project)
        self.assertEqual(line.amount, 1.5)

    def test_task_form_project_change_preserves_lines(self):
        line = self._create_line(amount=1.5)
        with Form(self.task.with_user(self.user)) as task_form:
            task_form.project_id = self.other_project
        self.assertEqual(line.task_id, self.task)
        self.assertEqual(line.project_id, self.other_project)
        self.assertEqual(line.task_partner_id, self.other_partner)


@tagged("post_install", "-at_install")
class TestTsmTaskTimesheet(TsmTimesheetCase):
    def test_calendar_end_dates_in_batch(self):
        lines = self.timesheets.create(
            [
                {"name": "Work", "date_time": "2026-01-01 23:30:00", "amount": 1.5},
                {"name": "No start date", "date_time": False},
            ]
        )
        self.assertEqual(lines[0].date_time_stop, datetime(2026, 1, 2, 1))
        self.assertFalse(lines[1].date_time_stop)
        lines[0].amount = 0
        self.assertEqual(lines[0].date_time_stop, lines[0].date_time)

    def test_stop_work_and_task_total(self):
        line = self._create_line(date_time="2026-01-01 10:00:00")
        with freeze_time("2026-01-01 11:30:00"):
            line.button_end_work()
        self.assertEqual(line.amount, 1.5)
        self.assertEqual(self.task.total_hours, 1.5)

    def test_stop_batch_without_start_date(self):
        dated = self._create_line(date_time="2026-01-01 10:00:00")
        undated = self._create_line(date_time=False)
        with self.assertRaises(ValidationError):
            (dated + undated).button_end_work()
        self.assertEqual(dated.amount, 0)
        self.assertEqual(undated.amount, 0)

    def test_default_tag_batch_validation(self):
        self.tags.search([("default", "=", True)]).write({"default": False})
        tags = self.tags.create([{"name": "First"}, {"name": "Second"}])
        tags.write({"default": False})
        tags[0].default = True
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            tags.write({"default": True})
        tags.write({"default": False})
        self.assertFalse(any(tags.mapped("default")))

    def test_name_without_configuration_and_explicit_title(self):
        model = self.timesheets.with_user(self.user)
        line = model.create({})
        self.assertEqual(line.name, "/")
        titled = model.create({"name": "Manual title"})
        self.assertEqual(titled.name, "Manual title")
        titled.amount = 2
        self.assertEqual(titled.name, "Manual title")
        titled.tag_ids = self.tags.create({"name": "No title configuration"})
        self.assertEqual(titled.name, "Manual title")

    def test_task_form_timesheets_without_title_or_tags(self):
        self.assertFalse(
            self.user.has_group("tsm_task_timesheet.group_tsm_timesheet_title")
        )
        self.assertFalse(
            self.user.has_group("tsm_task_timesheet.group_tsm_timesheet_tag")
        )
        with Form(self.task.with_user(self.user)) as task_form:
            with task_form.timesheet_ids.new() as line_form:
                line_form.amount = 1.5
            with task_form.timesheet_ids.new() as line_form:
                line_form.amount = 0.5

        self.assertEqual(len(self.task.timesheet_ids), 2)
        self.assertEqual(self.task.timesheet_ids.mapped("name"), ["/", "/"])
        self.assertFalse(any(self.task.timesheet_ids.mapped("tag_ids")))
        self.assertEqual(self.task.total_hours, 2)

    def test_tag_name_and_default(self):
        self.user.groups_id |= self.env.ref(
            "tsm_task_timesheet.group_tsm_timesheet_tag"
        )
        self.tags.search([("default", "=", True)]).write({"default": False})
        tag = self.tags.create({"name": "Support", "default": True})
        model = self.timesheets.with_user(self.user)
        line = model.create({})
        self.assertEqual(line.tag_ids, tag)
        self.assertEqual(line.name, tag.name)
        line.tag_ids = False
        self.assertEqual(line.name, tag.name)

    def test_create_and_start_requires_saved_task(self):
        with self.assertRaises(UserError):
            self.env["tsm.task"].create_and_start()
        self.assertFalse(self.task.timesheet_ids)

    def test_create_and_start_requires_customer(self):
        self.task.partner_id = False
        description = self.task.description
        with self.assertRaises(UserError):
            self.task.with_user(self.user).create_and_start()
        self.assertEqual(self.task.description, description)
        self.assertFalse(self.task.timesheet_ids)

    def test_create_and_start_without_timezone(self):
        task = self.task.with_user(self.user).with_context(tz=False)
        with freeze_time("2026-01-01 10:00:00"):
            action = task.create_and_start()
        self.assertEqual(action["res_id"], task.id)
        self.assertEqual(len(task.timesheet_ids), 1)
        self.assertEqual(task.timesheet_ids.name, "/")
        self.assertEqual(task.timesheet_ids.date_time, datetime(2026, 1, 1, 10))
        self.assertEqual(task.timesheet_ids.amount, 0)
        self.assertEqual(task.timesheet_ids.user_id, self.user)
        self.assertEqual(task.timesheet_ids.company_id, self.user.company_id)
        self.assertEqual(task.timesheet_ids.project_id, task.project_id)
        self.assertEqual(task.timesheet_ids.task_partner_id, task.partner_id)
        self.assertIn("01/01/2026 10:00:00", task.description)

    def test_create_and_start_context_timezone(self):
        with freeze_time("2026-01-01 10:00:00"):
            self.task.with_context(tz="Europe/Madrid").create_and_start()
        self.assertIn("01/01/2026 11:00:00", self.task.description)

    def test_task_delete_with_timesheets(self):
        line = self._create_line(amount=1)
        with self.assertRaises(UserError), self.env.cr.savepoint():
            self.task.unlink()
        line.unlink()
        self.task.unlink()
        self.assertFalse(self.task.exists())

    def test_close_and_archive_require_duration(self):
        line = self._create_line()
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            line.button_close_task()
        self.task.stage_id = self.closed_stage
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.task.action_inactive()
        line.amount = 1
        self.task.action_inactive()
        self.assertFalse(self.task.active)
        self.task.action_active()
        self.assertTrue(self.task.active)
