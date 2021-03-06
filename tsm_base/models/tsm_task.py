# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import datetime


class TsmTaskType(models.Model):
    _name = 'tsm.task.type'
    _description = 'Task Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    legend_priority = fields.Char(
        string='Starred Explanation', translate=True,
        help='Explanation text to help users using the '
             'star on tasks in this stage.')
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'),
        translate=True, required=True,
        help='Override the default value displayed for the blocked state for '
             'kanban selection, when the task is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready for Next Stage'),
        translate=True, required=True,
        help='Override the default value displayed for the done state for '
             'kanban selection, when the task is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'),
        translate=True, required=True,
        help='Override the default value displayed for the normal state for '
             'kanban selection, when the task is in that stage.')
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no '
             'records in that stage to display.')
    closed = fields.Boolean(
        help="Tasks in this stage are considered closed. "
             "You can only archive a task in a stage with state closed.",
        default=False,
    )


class TsmTask(models.Model):
    _name = "tsm.task"
    _description = "Tech Support Management Task"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "priority desc, sequence, date_start"

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        id = self.env['tsm.task.type'].search([], order='sequence', limit=1)
        if not id:
            return False

        return id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    code = fields.Char(string='Task Code',
        required=True, default="/", readonly=True)
    name = fields.Char(string='Task Title', required=True, index=True)
    active = fields.Boolean(default=True, copy=False,
        help="If the active field is set to False, it will allow you to hide"
        " the task without removing it.")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
    ], default='0', index=True, string="Priority")
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of tasks.")
    stage_id = fields.Many2one('tsm.task.type',
        string='Stage', index=True, copy=False,
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id)
    closed = fields.Boolean(related='stage_id.closed', readonly=True)
    tags_in_task = fields.Boolean(string="Use Tags in Tasks")
    tag_ids = fields.Many2many('tsm.task.tags', string='Tags',)
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')],
        string='Kanban State', copy=False, default='normal', required=True,
        help="A task's kanban state indicates special situations "
             "affecting it:\n"
             " * Grey is the default situation\n"
             " * Red indicates something is preventing "
             "the progress of this task\n"
             " * Green indicates the task is ready to be "
             "pulled to the next stage")
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label',
        string='Kanban State Label')
    color = fields.Integer(string='Color Index')
    date_start = fields.Datetime(string='Starting Date',
        default=fields.Datetime.now, index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date',
        default=fields.Datetime.now, index=True, copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    legend_blocked = fields.Char(related='stage_id.legend_blocked',
        string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done',
        string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal',
        string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    description = fields.Html(string='Task Description',
        sanitize=True, strip_style=False, translate=False,
        help="Details, notes and aclarations about the task.")
    project_id = fields.Many2one('tsm.project',
        string='Project', index=True, track_visibility='onchange')
    manager_id = fields.Many2one('res.users',
        string='Project Manager', related='project_id.user_id',
        readonly=True, related_sudo=False)
    user_id = fields.Many2one('res.users',
        string='Assigned to', default=lambda self: self.env.uid,
        required=True, index=True, track_visibility='always')
    partner_id = fields.Many2one('res.partner', string='Customer')
    contact_id = fields.Many2one('res.partner', string='Contact',
        domain="[('parent_id', '=', partner_id),"
                "('type', 'in', ('contact','invoice'))]",)
    privacy_visibility = fields.Selection([
        ('followers', 'On invitation only'),
        ('employees', 'Visible by all employees'),
        ],
        string='Privacy', required=True, default='followers',
        help="Holds visibility of the task:\n "
             "- On invitation only: Employees may only "
             "see the followed tasks\n"
             "- Visible by all employees: Employees "
             "may see all tasks\n")
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    _sql_constraints = [
        ('tsm_task_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.multi
    def name_get(self):
        result = super(TsmTask, self).name_get()
        new_result = []

        for task in result:
            rec = self.browse(task[0])
            name = '[%s] %s' % (rec.code, task[1])
            new_result.append((rec.id, name))
        return new_result

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            if self.project_id.partner_id:
                self.partner_id = self.project_id.partner_id

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.date_assign = fields.Datetime.now()

    @api.multi
    def action_task_send(self):
        '''
        This function opens a window to compose an email,
        with the task template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('tsm_base', 'tsm_task_email_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        lang = self.env.context.get('lang')
        template = template_id and self.env['mail.template'].browse(template_id)
        if template and template.lang:
            lang = template._render_template(template.lang, 'tsm.task', self.ids[0])
        ctx = {
            'default_model': 'tsm.task',
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
    @api.model
    def default_get(self, fields):
        result = super(TsmTask, self).default_get(fields)
        active_model = self._context.get('active_model')
        if active_model == 'tsm.project':
            active_id = self._context.get('active_id')
            project = self.env['tsm.project'].browse(active_id)
            result['partner_id'] = project.partner_id.id

        return result

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # Assign new code
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('tsm.task')

        task = super(TsmTask, self.with_context(context)).create(vals)
        return task

    @api.multi
    def write(self, vals):
        now = fields.Datetime.now()

        # user_id change: update date_assign
        if vals.get('user_id') and 'date_assign' not in vals:
            vals['date_assign'] = now

        # if task is archived reset some values
        if 'active' in vals and False == vals['active']:
            vals['priority'] = 0
            vals['kanban_state'] = 'normal'

        result = super(TsmTask, self).write(vals)
        return result

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code('tsm.task')
        return super(TsmTask, self).copy(default)


class TsmTaskTags(models.Model):
    """ Tags of tasks """
    _name = "tsm.task.tags"
    _description = "Tags in tasks"

    name = fields.Char(required=True)
    color = fields.Integer(string='Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
