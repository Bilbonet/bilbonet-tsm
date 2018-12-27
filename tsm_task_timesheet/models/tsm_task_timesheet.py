# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models
from datetime import datetime


class TsmTaskTimesheet(models.Model):
    _name = 'tsm.task.timesheet'
    _description = 'Spent time in tasks'
    _order = 'date_time desc, id desc'

    date_time = fields.Datetime(default=fields.Datetime.now, string='Date')
    name = fields.Char(string='Brief description', required=True)
    amount = fields.Float('Quantity', default=0.0)
    task_id = fields.Many2one('tsm.task', 'Task', index=True)
    project_id = fields.Many2one('tsm.project', 'Project',
                                 domain=[('allow_timesheets', '=', True)])
    user_id = fields.Many2one('res.users',
                              string='Assigned to',
                              default=lambda self: self.env.uid,
                              required=True,
                              index=True, track_visibility='always')
    closed = fields.Boolean(related='task_id.stage_id.closed', readonly=True)

    @api.multi
    def button_end_work(self):
        end_date = datetime.now()
        for line in self:
            date = fields.Datetime.from_string(line.date_time)
            line.amount = (end_date - date).total_seconds() / 3600
        return True
