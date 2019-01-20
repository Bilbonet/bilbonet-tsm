# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TsmTechAsset(models.Model):
    _name = "tsm.tech.asset"
    _description = "Cliente Technical Assets Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "priority desc, sequence, id desc"

    def _compute_task_count(self):
        tasks = self.env['tsm.task'].search([
            ('asset_ids', 'in', self.id)], count=True)
        self.task_count = tasks

    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide"
        " the asset without removing it.")
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of assets.")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
    ], default='0', index=True, string="Priority")
    date = fields.Datetime(string='Date',
                           default=fields.Datetime.now,
                           index=True, copy=False)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    name = fields.Char(string='Asset Title', track_visibility='always',
                       required=True, index=True)
    tech_notes = fields.Html(
        string='Technical Notes', sanitize=True,
        strip_style=False, translate=False,
        help="Details, notes and aclarations about the asset.")
    config_notes = fields.Html(
        string='Configuration Notes', sanitize=True,
        strip_style=False, translate=False,
        help="Configurations, notes about the assets.")
    user_id = fields.Many2one('res.users',
                              string='Responsible',
                              default=lambda self: self.env.uid,
                              required=True,
                              index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner',
                                 string='Customer',
                                 required=True)
    type_id = fields.Many2one('tsm.tech.asset.type',
                                 string='Type',
                                 required=True,
                                 index=True,
                                 track_visibility='onchange',
                                 change_default=True)
    task_count = fields.Integer(compute='_compute_task_count', string="Tasks")

class TsmTechAssetType(models.Model):
    _name = "tsm.tech.asset.type"
    _description = "Types of assets"

    name = fields.Char(string='Type of asset', required=True)
