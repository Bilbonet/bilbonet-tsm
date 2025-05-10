# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TsmTaskTimesheet(models.Model):
    _name = "tsm.task.timesheet"
    _description = "Spent time in tasks"
    _order = "date_time desc, id desc"

    @api.depends("tag_ids")
    def _compute_default_name(self):
        for ts in self:
            if self.user_has_groups("tsm_task_timesheet.group_tsm_timesheet_title"):
                ts.name = "/"
            if self.user_has_groups("tsm_task_timesheet.group_tsm_timesheet_tag"):
                if ts.tag_ids:
                    ts.name = ts.tag_ids.name

    def _get_default_tag_id(self):
        if self.user_has_groups("tsm_task_timesheet.group_tsm_timesheet_tag"):
            tag_id = self.env["tsm.task.timesheet.tags"].search(
                [("default", "=", True)], limit=1
            )
            if tag_id:
                return tag_id.id
        return False

    name = fields.Char(
        string="Timesheet Title",
        compute=_compute_default_name,
        readonly=False,
        store=True,
        required=True,
    )
    tag_ids = fields.Many2one(
        comodel_name="tsm.task.timesheet.tags",
        string="Timesheet Tags",
        default=_get_default_tag_id,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    date_time = fields.Datetime(string="Date", default=fields.Datetime.now)
    amount = fields.Float(string="Quantity", default=0.0)
    task_id = fields.Many2one(
        comodel_name="tsm.task",
        string="Task",
        index=True,
    )
    project_id = fields.Many2one(
        comodel_name="tsm.project",
        string="Project",
        related="task_id.project_id",
        store=True,
        index="btree_not_null",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        index=True,
        default=lambda self: self.env.user,
        required=True,
    )
    closed = fields.Boolean(related="task_id.stage_id.closed", readonly=True)
    date_time_stop = fields.Datetime(
        compute="_compute_stop_date_time",
        string="End date time for calendar view",
        store=True,
        readonly=True,
    )
    task_partner_id = fields.Many2one(
        related="task_id.partner_id", store=True, string="Customer"
    )

    @api.depends("date_time", "amount")
    def _compute_stop_date_time(self):
        for line in self:
            line.date_time_stop = datetime.strptime(
                str(line.date_time), "%Y-%m-%d %H:%M:%S"
            ) + timedelta(seconds=line.amount * 3600)

    def button_end_work(self):
        end_date = fields.Datetime.now()
        for line in self:
            line.amount = (end_date - line.date_time).total_seconds() / 3600
        return True

    def button_open_task(self):
        for line in self.filtered("task_id"):
            stage = self.env["tsm.task.type"].search([("closed", "=", False)], limit=1)
            if stage:
                line.task_id.write({"stage_id": stage.id})

    def button_close_task(self):
        for line in self.filtered("task_id"):
            stage = self.env["tsm.task.type"].search(
                [("closed", "=", True)],
                limit=1,
            )
            if not stage:  # pragma: no cover
                raise ValidationError(
                    _("There isn't any stage with closed check. Please " "mark any.")
                )
            for t in line.task_id.timesheet_ids:
                if t.amount == 0:
                    raise ValidationError(
                        _(
                            "There are any timesheet with 00:00 hours in this task.\n"
                            "That is not allowed in stages marked as closed."
                        )
                    )

            line.task_id.write({"stage_id": stage.id})

    def toggle_closed(self):
        self.ensure_one()
        if self.closed:
            self.button_open_task()
        else:
            self.button_close_task()
