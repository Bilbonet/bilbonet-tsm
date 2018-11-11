# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TsmProject(models.Model):
    _name = "tsm.project"
    _description = "Tech Support Management Project"
    _inherit = ['mail.thread']
    _order = "sequence, name, id"

    def _compute_task_count(self):
        task_data = self.env['tsm.task'].read_group(
            [('project_id', 'in', self.ids)],
            ['project_id'], ['project_id']
        )
        result = dict(
            (data['project_id'][0], data['project_id_count'])
            for data in task_data
        )
        for project in self:
            project.task_count = result.get(project.id, 0)

    def _compute_task_needaction_count(self):
        projects_data = self.env['tsm.task'].read_group([
            ('project_id', 'in', self.ids),
            ('message_needaction', '=', True)
        ], ['project_id'], ['project_id'])
        mapped_data = {
            project_data['project_id'][0]:
                int(project_data['project_id_count'])
                for project_data in projects_data
        }
        for project in self:
            project.task_needaction_count = mapped_data.get(project.id, 0)

    def _compute_is_favorite(self):
        for project in self:
            project.is_favorite = self.env.user in project.favorite_user_ids

    def _inverse_is_favorite(self):
        favorite_projects = not_fav_projects = self.env['tsm.project'].sudo()
        for project in self:
            if self.env.user in project.favorite_user_ids:
                favorite_projects |= project
            else:
                not_fav_projects |= project

        # Project User has no write access for project.
        not_fav_projects.write({'favorite_user_ids': [(4, self.env.uid)]})
        favorite_projects.write({'favorite_user_ids': [(3, self.env.uid)]})

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide"
             " the project without removing it.")
    sequence = fields.Integer(default=10,
        help="Gives the sequence order when displaying a list of Projects.")
    favorite_user_ids = fields.Many2many(
        'res.users', 'tsm_project_favorite_user_rel', 'project_id', 'user_id',
        default=_get_default_favorite_user_ids,
        string='Members')
    is_favorite = fields.Boolean(
        compute='_compute_is_favorite',
        inverse='_inverse_is_favorite',
        string='Show Project on dashboard',
        help="Whether this project should be displayed on the "
             "dashboard or not")
    color = fields.Integer(string='Color Index')
    name = fields.Char(string='Project Name', index=True, required=True)
    user_id = fields.Many2one('res.users', string='Project Manager',
                              default=lambda self: self.env.user,
                              track_visibility="onchange")
    # use auto_join to speed up name_search call
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 auto_join=True, track_visibility='onchange')
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
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get()
    )
    task_count = fields.Integer(compute='_compute_task_count', string="Tasks")
    task_needaction_count = fields.Integer(
        compute='_compute_task_needaction_count', string="Tasks")

