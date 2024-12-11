# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from datetime import datetime
import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TsmTask(models.Model):
    _inherit = "tsm.task"

    @api.depends("timesheet_ids.amount")
    def _hours_get(self):
        for task in self.sorted(key="id", reverse=True):
            """use 'sudo' here to allow project
            user (without timesheet user right) to create task"""
            task.total_hours = sum(task.sudo().timesheet_ids.mapped("amount"))

    total_hours = fields.Float(
        string="Total Spent Hours",
        compute="_hours_get",
        store=True,
        help="Computed as: Sum Time Spent in tasks.",
    )
    timesheet_ids = fields.One2many(
        comodel_name="tsm.task.timesheet", inverse_name="task_id", string="Timesheets"
    )

    def unlink(self):
        for task in self:
            if task.timesheet_ids:
                raise UserError(
                    _(
                        "You cannot delete a task containing "
                        "timesheets. You can either delete all the task's timesheet "
                        "and then delete the task or simply deactivate the task."
                    )
                )
        res = super(TsmTask, self).unlink()
        return res

    @api.onchange("project_id")
    def _onchange_project_timesheet(self):
        for t in self.timesheet_ids:
            t.project_id = self.project_id.id

    @api.onchange("stage_id")
    def _onchange_task_stage(self):
        if self.stage_id.closed:
            for t in self.timesheet_ids:
                if t.amount == 0:
                    raise ValidationError(
                        _(
                            "There are any timesheet with 00:00 hours in this task.\n"
                            "That is not allowed in stages marked as closed."
                        )
                    )

    def create_and_start(self):
        """
        Create Task and start timesheet
        """
        self.ensure_one()
        tz = self.env.context.get("tz", self.env.user.partner_id.tz)
        description = ("<p><b>[%s]</b><br><br></p>") % (
            datetime.now(pytz.timezone(tz)).strftime("%d/%m/%Y %H:%M:%S")
        )
        self.update({"description": description})

        # Create timesheet
        ts = self.env["tsm.task.timesheet"].new(
            {
                "task_id": self.id,
                "name": "/",
            }
        )
        ts = ts._convert_to_write(ts._cache)
        self.env["tsm.task.timesheet"].create(ts)

        return {
            "type": "ir.actions.act_window",
            "res_model": "tsm.task",
            "res_id": self.id,
            "view_type": "form",
            "target": "current",
            "view_mode": "form",
            "context": {
                "form_view_initial_mode": "edit",
            },
        }
