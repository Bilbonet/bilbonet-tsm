# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TsmTask(models.Model):
    _inherit = "tsm.task"

    @api.depends('timesheet_ids.amount')
    def _hours_get(self):
        for task in self.sorted(key='id', reverse=True):
            '''use 'sudo' here to allow project 
            user (without timesheet user right) to create task'''
            task.total_hours = sum(task.sudo().timesheet_ids.mapped('amount'))

    total_hours = fields.Float(compute='_hours_get', store=True,
                            string='Total Spent Hours',
                            help="Computed as: Sum Time Spent in tasks.")
    timesheet_ids = fields.One2many('tsm.task.timesheet',
                                    'task_id', 'Timesheets')

    @api.multi
    def unlink(self):
        for task in self:
            if task.timesheet_ids:
                raise UserError(_("You cannot delete a task containing "
                "timesheets. You can either delete all the task's timesheet "
                "and then delete the task or simply deactivate the task."))
        res = super(TsmTask, self).unlink()
        return res

    @api.onchange('project_id')
    def _onchange_project_timesheet(self):
        for t in self.timesheet_ids:
            t.project_id = self.project_id.id

    @api.onchange('stage_id')
    def _onchange_task_stage(self):
        if self.stage_id.closed:
            for t in self.timesheet_ids:
                if t.amount == 0:
                    raise ValidationError(_(
                    "There are any timesheet with 00:00 hours in this task.\n"
                    "That is not allowed in stages marked as closed."))
