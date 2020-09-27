# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class TsmProject(models.Model):
    _name = "tsm.project"
    _description = "Tech Support Management Project"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "priority desc, sequence, date_start"

    def _compute_task_count(self):
        task_data = self.env['tsm.task'].read_group(
            [('project_id', 'in', self.ids),
            '|',('active', '=', True), ('active', '=', False)],
            ['project_id'], ['project_id']
        )

        result = dict(
            (data['project_id'][0], data['project_id_count'])
            for data in task_data
        )
        for project in self:
            project.task_count = result.get(project.id, 0)

    name = fields.Char(string='Project Name', index=True, required=True)
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide"
             " the project without removing it.")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
    ], default='0', index=True, string="Priority")
    sequence = fields.Integer(default=10,
        help="Gives the sequence order when displaying a list of Projects.")
    color = fields.Integer(string='Color Index')
    user_id = fields.Many2one('res.users',
        string='Project Manager', required=True,
        default=lambda self: self.env.user, track_visibility="onchange")
    # use auto_join to speed up name_search call
    partner_id = fields.Many2one('res.partner',
        string='Customer', required=True, auto_join=True, track_visibility='onchange')
    privacy_visibility = fields.Selection([
        ('followers', 'On invitation only'),
        ('employees', 'Visible by all employees'),
        ],
        string='Privacy', required=True,
        default='followers',
        help="Holds visibility of the tasks "
             "that belong to the current project:\n"
             "- On invitation only: Employees may only "
             "see the followed project, tasks\n"
             "- Visible by all employees: Employees "
             "may see all project, tasks\n")
    description = fields.Html(string='Project Description', sanitize=True,
        strip_style=False, translate=False,
        help="Details, notes and aclarations about the project.")
    date_start = fields.Datetime(string='Starting Date',
        default=fields.Datetime.now, index=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    task_ids = fields.One2many('tsm.task', 'project_id', string='Tasks Related')
    task_count = fields.Integer(compute='_compute_task_count', string="Amount Tasks")

    @api.multi
    def action_project_send(self):
        '''
        This function opens a window to compose an email,
        with the project template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('tsm_base', 'tsm_project_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'tsm.project', self.ids[0])
        ctx = {
            'default_model': 'tsm.project',
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

    # ------------------
    # CRUD overrides
    # ------------------
    @api.multi
    def write(self, vals):
        res = super(TsmProject, self).write(vals) if vals else True

        # archiving/unarchiving a project does it on its tasks, too
        # if 'active' in vals:
        #     self.with_context(active_test=False).mapped('task_ids').write(
        #                                         {'active': vals['active']})

        # First all tasks of the project must be archived
        if 'active' in vals and False == vals['active']:
            actives = self.browse(self.task_ids)
            if actives:
                raise UserError(
                    _("You cannot archive a project with active tasks. "
                      "You need to archive all tasks of the project first.")
                )

        return res

    @api.multi
    def unlink(self):
        for project in self:
            if project.task_ids:
                raise UserError(_("You cannot delete a project with tasks. "
                "You can either delete the project's task and then delete the "
                "project or simply deactivate the project."))
        res = super(TsmProject, self).unlink()
        return res
