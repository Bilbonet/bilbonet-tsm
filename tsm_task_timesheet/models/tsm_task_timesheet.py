# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, exceptions, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class TsmTaskTimesheet(models.Model):
    _name = 'tsm.task.timesheet'
    _description = 'Spent time in tasks'
    _order = 'date_time desc, id desc'

    company_id = fields.Many2one('res.company', string='Company',
                                 required=True,
                                 default=lambda self: self.env.user.company_id)
    active = fields.Boolean('Active',
                    help="If the active field is set to False, it will allow "
                         "you to hide the account without removing it.",
                    default=True)
    date_time = fields.Datetime(default=fields.Datetime.now, string='Date')
    name = fields.Char(string='Brief description', required=True)
    amount = fields.Float('Quantity', default=0.0)
    task_id = fields.Many2one('tsm.task', 'Task', index=True)
    project_id = fields.Many2one('tsm.project', 'Project')
    user_id = fields.Many2one('res.users',
                              string='Assigned to',
                              default=lambda self: self.env.uid,
                              required=True,
                              index=True, track_visibility='always')
    closed = fields.Boolean(related='task_id.stage_id.closed', readonly=True)
    date_time_stop = fields.Datetime(compute='_get_stop_date_time',
                                     string='End date time for calendar view',
                                     store=True,
                                     readonly=True)
    task_partner_id = fields.Many2one(related='task_id.partner_id',
                                       store=True, string='Customer')

    @api.one
    @api.depends('date_time')
    def _get_stop_date_time(self):
        for line in self:
            line.date_time_stop = \
                datetime.strptime(line.date_time,
                                  "%Y-%m-%d %H:%M:%S") + timedelta(
                    seconds=line.amount*3600)

    @api.onchange('project_id')
    def onchange_project_id(self):
        # reset task when changing project
        self.task_id = False
        # force domain on task when project is set
        if self.project_id:
            return {'domain': {
                'task_id': [('project_id', '=', self.project_id.id)]
            }}
        else:
            return {'domain': {
                'task_id': [('project_id', '=', False)]
            }}

    @api.multi
    def button_end_work(self):
        end_date = datetime.now()
        for line in self:
            date = fields.Datetime.from_string(line.date_time)
            line.amount = (end_date - date).total_seconds() / 3600
        return True

    @api.multi
    def button_open_task(self):
        for line in self.filtered('task_id'):
            stage = self.env['tsm.task.type'].search(
                    [('closed', '=', False)], limit=1)
            if stage:
                line.task_id.write({'stage_id': stage.id})

    @api.multi
    def button_close_task(self):
        for line in self.filtered('task_id'):
            stage = self.env['tsm.task.type'].search(
                [('closed', '=', True)], limit=1,
            )
            if not stage:  # pragma: no cover
                raise exceptions.UserError(
                    _("There isn't any stage with closed check. Please "
                      "mark any.")
                )
            for t in line.task_id.timesheet_ids:
                if t.amount == 0:
                    raise ValidationError(_(
                    "There are any timesheet with 00:00 hours in this task.\n"
                    "That is not allowed in stages marked as closed."))

            line.task_id.write({'stage_id': stage.id})

    @api.multi
    def toggle_closed(self):
        self.ensure_one()
        if self.closed:
            self.button_open_task()
        else:
            self.button_close_task()
