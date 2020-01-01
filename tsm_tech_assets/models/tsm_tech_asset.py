# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class TsmTechAsset(models.Model):
    _name = "tsm.tech.asset"
    _description = "Cliente Technical Assets Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "priority desc, sequence, id desc"

    def _compute_task_count(self):
        for asset in self:
            asset.task_count = self.env['tsm.task'].search([
                ('asset_ids', 'in', asset.id),
                '|', ('active', '=', True), ('active', '=', False)
            ], count=True)

    def _compute_can_edit(self):
        if self.env.user.has_group('tsm_base.group_tsm_manager')\
                or self.env.user.id == self.user_id.id:
            self.can_edit = True

    # For the Report Detailed
    def _compute_task_ids(self):
        for asset in self:
            task_ids = self.env['tsm.task'].search([
                ('asset_ids', 'in', asset.id),
                '|', ('active', '=', True), ('active', '=', False)
            ], order='date_start')
        return task_ids

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide"
        " the asset without removing it.")
    code = fields.Char(string='Tech Asset Code',
        default="/", required=True, copy=False)
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of assets.")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
    ], default='0', index=True, string="Priority")
    date = fields.Datetime(string='Date',
        default=fields.Datetime.now, index=True, copy=False)
    name = fields.Char(string='Asset Title', track_visibility='always',
        required=True, index=True)
    tech_notes = fields.Html(string='Technical Notes',
        sanitize=True, strip_style=False, translate=False,
        help="Details, notes and aclarations about the asset.")
    config_notes = fields.Html(string='Configuration Notes',
        sanitize=True, strip_style=False, translate=False,
        help="Configurations, notes about the assets.")
    user_id = fields.Many2one('res.users',
        string='Responsible', required=True,
        default=lambda self: self.env.uid, index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner',
        string='Customer', required=True)
    type_id = fields.Many2one('tsm.tech.asset.type',
        string='Type', required=True, index=True,
        track_visibility='onchange', change_default=True)
    task_ids = fields.One2many('tsm.task', 'asset_ids',
        string='Tasks', context={'active_test': False})
    task_count = fields.Integer(compute='_compute_task_count', string="Amount Tasks")
    privacy_visibility = fields.Selection([
        ('followers', 'On invitation only'),
        ('employees', 'Visible by all employees'),
    ],
        string='Privacy', required=True,
        default='followers',
        help="Holds visibility of the tech asset:\n"
             "- On invitation only: Employees may only "
             "see the followed tech asset\n"
             "- Visible by all employees: All employees "
             "may see tech asset\n")
    can_edit = fields.Boolean(compute='_compute_can_edit',
        string='Security: only managers can edit', default=True,
        help='This field is for security purpose. '
        'Only members of managers group can modify some fields.')

    _sql_constraints = [
        ('tsm_tech_asset_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = \
                self.env['ir.sequence'].next_by_code('tsm.tech.asset')
        return super(TsmTechAsset, self).create(vals)

    @api.multi
    def action_tech_asset_send(self):
        '''
        This function opens a window to compose an email,
        with the tech asset template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'tsm_tech_assets', 'tsm_tech_asset_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'tsm.tech.asset', self.ids[0])
        ctx = {
            'default_model': 'tsm.tech.asset',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'model_description': self.with_context(lang=lang).name,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

class TsmTechAssetType(models.Model):
    _name = "tsm.tech.asset.type"
    _description = "Types of assets"

    name = fields.Char(string='Type of asset', required=True)
