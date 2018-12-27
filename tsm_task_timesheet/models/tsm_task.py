# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from odoo import models, fields, api, _
from odoo.exceptions import UserError

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
                            help="Computed as: Time Spent + Remaining Time.")
    timesheet_ids = fields.One2many('tsm.task.timesheet',
                                    'task_id', 'Timesheets')

    @api.onchange('project_id')
    def _onchange_project_timesheet(self):
        for t in self.timesheet_ids:
            t.project_id = self.project_id.id

