# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, _
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
        string='Project Manager',
        default=lambda self: self.env.user, 
        required=True, tracking=True)
    # use auto_join to speed up name_search call
    partner_id = fields.Many2one('res.partner',
        string='Customer', required=True, auto_join=True, tracking=True)
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

    def action_project_send(self):
        '''
        This function opens a window to compose an email,
        with the project template message loaded by default
        '''
        self.ensure_one()
        lang = self.env.context.get('lang')
        mail_template = self.env.ref('tsm_base.tsm_project_email_template', raise_if_not_found=False)
        if mail_template and mail_template.lang:
            lang = mail_template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'tsm.project',
            'default_res_id': self.id,
            'default_use_template': bool(mail_template),
            'default_template_id': mail_template.id if mail_template else None,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'force_email': True,
            'model_description': 'TSM Project',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    # ------------------
    # CRUD overrides
    # ------------------
    def write(self, vals):
        # archiving/unarchiving a project does it on its tasks, too
        # if 'active' in vals:
        #     self.with_context(active_test=False).mapped('task_ids').write(
        #                                         {'active': vals['active']})

        # First all tasks of the project must be archived
        if 'active' in vals and vals['active'] == False:
            actives = self.browse(self.task_ids)
            if actives:
                raise UserError(
                    _("You cannot archive a project with active tasks. "
                      "You need to archive all tasks of the project first.")
                )
            else:
                # if project is archived reset some values
                vals['priority'] = 0

        res = super().write(vals) if vals else True
        return res

    def unlink(self):
        for project in self:
            if project.task_ids:
                raise UserError(_("You cannot delete a project with tasks. "
                "You can either delete the project's task and then delete the "
                "project or simply deactivate the project."))
        return super().unlink()
