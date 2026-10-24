# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class TsmTask(models.Model):
    _inherit = "tsm.task"

    @api.depends("timesheet_ids.amount")
    def _compute_hours(self):
        """
        use 'sudo' here to allow project
        user (without timesheet user right) to create task
        """
        for task in self.sorted(key="id", reverse=True):
            task.total_hours = sum(task.sudo().timesheet_ids.mapped("amount"))

    total_hours = fields.Float(
        string="Total Spent Hours",
        compute="_compute_hours",
        store=True,
        help="Computed as: Sum Time Spent in tasks.",
    )
    timesheet_ids = fields.One2many(
        comodel_name="tsm.task.timesheet",
        inverse_name="task_id",
        string="Timesheets",
    )

    @api.ondelete(at_uninstall=False)
    def _unlink_except_timesheets(self):
        for task in self:
            if task.timesheet_ids:
                raise UserError(
                    self.env._(
                        "You cannot delete a task containing "
                        "timesheets. You can either delete all the task's timesheet "
                        "and then delete the task or simply deactivate the task."
                    )
                )

    @api.onchange("stage_id")
    def _onchange_task_stage(self):
        if self.stage_id.closed:
            for t in self.timesheet_ids:
                if t.amount == 0:
                    raise ValidationError(
                        self.env._(
                            "There are any timesheet with 00:00 hours in this task.\n"
                            "That is not allowed in stages marked as closed."
                        )
                    )

    def create_and_start(self):
        """Start a timesheet on the saved task and reopen its form."""
        if not self:
            raise UserError(
                self.env._(
                    "Save a task with a title and a customer before starting work."
                )
            )
        self.ensure_one()
        if not self.name or not self.partner_id:
            raise UserError(
                self.env._("Enter a task title and a customer before starting work.")
            )
        timestamp = fields.Datetime.context_timestamp(self, fields.Datetime.now())
        description = f"<p><b>[{timestamp:%d/%m/%Y %H:%M:%S}]</b><br><br></p>"
        self.write({"description": description})

        self.env["tsm.task.timesheet"].create(
            {
                "task_id": self.id,
                "name": "/",
            }
        )

        return {
            "type": "ir.actions.act_window",
            "res_model": "tsm.task",
            "res_id": self.id,
            "target": "current",
            "view_mode": "form",
            "context": {
                "form_view_initial_mode": "edit",
            },
        }

    @api.constrains("active")
    def _check_archiving_restrictions(self):
        """
        Not archive task with some time sheet with no time spent.
        Constraint should be tested just after archiving a task,
        but shouldn't be raised when unarchiving a task.
        """
        for task in self.filtered(lambda t: not t.active):
            if any(not ts.amount for ts in task.timesheet_ids):
                raise ValidationError(
                    self.env._(
                        "You can not archive a task with timesheets "
                        "that have no time spent."
                    )
                )
        return super()._check_archiving_restrictions()
