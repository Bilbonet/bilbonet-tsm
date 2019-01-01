# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class TsmTimePack(models.Model):
    _name = "tsm.time.pack"
    _description = "Packs of time to spent in tasks timesheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide"
        " the time pack without removing it.")
    name = fields.Char(string='Time Pack Title', track_visibility='always',
                       required=True, index=True)
    description = fields.Html(
        string='Time Pack Description', sanitize=True,
        strip_style=False, translate=False,
        help="Details, notes and aclarations about the time pack.")
    timesheet_ids = fields.One2many('tsm.task.timesheet',
                                    'timepack_id', 'Timesheets')
    user_id = fields.Many2one('res.users',
                              string='Assigned to',
                              default=lambda self: self.env.uid,
                              required=True,
                              index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner',
                                 string='Customer',
                                 required=True)
    date_start = fields.Date('Start Date', required=True,
                             default=fields.Date.today,
                             help="Start date of the time pack.")
    date_end = fields.Date(string='Ending Date', index=True, copy=False)
    privacy_visibility = fields.Selection([
        ('followers', 'On invitation only'),
        ('employees', 'Visible by all employees'),
    ],
        string='Privacy', required=True,
        default='followers',
        help="Holds visibility of the time packs "
             "that belong to the current time pack:\n"
             "- On invitation only: Employees may only "
             "see the followed time packs\n"
             "- Visible by all employees: Employees "
             "may see all time packs\n")
    contrated_hours = fields.Float(
        string='Contrated Hours',
        help='Time contracted by the client for support and it can be '
             'consumed in tasks and timesheet.')
    consumed_hours = fields.Float(compute='_hours_get',
        store=True, string='Hours Consumed',
        help="Computed as: The sum of the timesheet checked "
             "to discount time.")
    remaining_hours = fields.Float(compute='_hours_get',
        store=True, string='Remaining Hours',
        help="Computed as: Contrated hours - Cosumed hours")
    total_hours_spent = fields.Float(compute='_hours_get',
        store=True, string='Total Hours Spent',
        help="Computed as: Time Spent in tasks.")
    complimentary_hours = fields.Float(compute='_hours_get',
        store=True, string='Complimentari Hours.',
        help="Hours spent but not discounted in time pack.")
    progress = fields.Float(compute='_hours_get',
        store=True, string='Progress', group_operator="avg")

    @api.depends('timesheet_ids.amount', 'timesheet_ids.discount_time',
                 'contrated_hours', 'consumed_hours')
    @api.onchange('timesheet_ids.amount', 'timesheet_ids.discount_time')
    def _hours_get(self):
        for time in self.sorted(key='id', reverse=True):
            '''use "sudo" here to allow task user (without timesheet 
            user right) to create task'''
            time.total_hours_spent = sum(
                                    time.sudo().timesheet_ids.mapped('amount')
            )
            '''Filter time line checked to discount time'''
            timesheet_consu = time.sudo().mapped('timesheet_ids').filtered(
                     lambda x: x.discount_time)
            time.consumed_hours = sum(timesheet_consu.mapped('amount'))
            time.complimentary_hours = time.total_hours_spent - time.consumed_hours
            time.remaining_hours = time.contrated_hours - time.consumed_hours


            # task.total_hours = max(task.planned_hours, task.effective_hours)
            # task.total_hours_spent = task.effective_hours + task.children_hours


            if time.contrated_hours > 0.0:
                time.progress = round(
                    (100.0 * time.consumed_hours) / time.contrated_hours, 2
                )
            else:
                time.progress = 0.0
