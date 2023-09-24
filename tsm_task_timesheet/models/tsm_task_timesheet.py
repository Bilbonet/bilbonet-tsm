# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class TsmTaskTimesheet(models.Model):
    _name = 'tsm.task.timesheet'
    _description = 'Spent time in tasks'
    _order = 'date_time desc, id desc'

    def _get_default_tag_id(self):
        """ Assign Default Tag if exists """
        tag_id = self.env['tsm.task.timesheet.tags'].search([
            ('default', '=', True)], limit=1)
        if not tag_id:
            return False
        return tag_id.id

    company_id = fields.Many2one(
        comodel_name='res.company', 
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    active = fields.Boolean(string='Active', default=True,
        help="If the active field is set to False, it will allow "
             "you to hide the account without removing it.",
    )
    date_time = fields.Datetime(string='Date', default=fields.Datetime.now)
    name = fields.Char(string='Timesheet Title', default="/", required=True)
    amount = fields.Float(string='Quantity', default=0.0)
    task_id = fields.Many2one(
        comodel_name='tsm.task', 
        string='Task', 
        index=True,
    )
    project_id = fields.Many2one(
        comodel_name='tsm.project', 
        string='Project'
    )
    user_id = fields.Many2one(
        comodel_name="res.users", 
        string='Assigned to',
        index=True,
        default=lambda self: self.env.user, 
        required=True,
        tracking=20,
    )
    closed = fields.Boolean(related='task_id.stage_id.closed', readonly=True)
    date_time_stop = fields.Datetime(compute='_get_stop_date_time',
        string='End date time for calendar view', store=True, readonly=True)
    task_partner_id = fields.Many2one(related='task_id.partner_id',
        store=True, string='Customer')
    tag_ids = fields.Many2one(
        comodel_name='tsm.task.timesheet.tags', 
        string='Timesheet Tags',
        default=_get_default_tag_id,
    )

    @api.model_create_multi
    def create(self, values):
        # Assign project_id
        project_id = self.env['tsm.task'].browse(
                                            values['task_id']).project_id.id
        if project_id:
            values['project_id'] = project_id

        return super(TsmTaskTimesheet, self).create(values)

    @api.depends('date_time', 'amount')
    def _get_stop_date_time(self):
        for line in self:
            line.date_time_stop = datetime.strptime(
                str(line.date_time), "%Y-%m-%d %H:%M:%S"
                ) + timedelta(seconds=line.amount*3600)


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

    def button_end_work(self):
        end_date = datetime.now()
        for line in self:
            date = fields.Datetime.from_string(line.date_time)
            line.amount = (end_date - date).total_seconds() / 3600
        return True

    def button_open_task(self):
        for line in self.filtered('task_id'):
            stage = self.env['tsm.task.type'].search(
                    [('closed', '=', False)], limit=1)
            if stage:
                line.task_id.write({'stage_id': stage.id})

    def button_close_task(self):
        for line in self.filtered('task_id'):
            stage = self.env['tsm.task.type'].search(
                [('closed', '=', True)], limit=1,
            )
            if not stage:  # pragma: no cover
                raise ValidationError(
                    _("There isn't any stage with closed check. Please "
                      "mark any.")
                )
            for t in line.task_id.timesheet_ids:
                if t.amount == 0:
                    raise ValidationError(_(
                    "There are any timesheet with 00:00 hours in this task.\n"
                    "That is not allowed in stages marked as closed."))

            line.task_id.write({'stage_id': stage.id})

    def toggle_closed(self):
        self.ensure_one()
        if self.closed:
            self.button_open_task()
        else:
            self.button_close_task()
