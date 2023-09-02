# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


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
    kanban_state = fields.Selection(selection=[
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
        string='Project', index=True, tracking=True)
    manager_id = fields.Many2one('res.users',
        string='Project Manager', related='project_id.user_id',
        readonly=True, related_sudo=False)
    user_id = fields.Many2one('res.users',
        string='Assigned to', default=lambda self: self.env.uid,
        required=True, index=True, tracking=True)
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

    @api.constrains('active')
    def _check_archiving_restrictions(self):
        # constraint should be tested just after archiving a task, but shouldn't be raised when unarchiving a task
        for task in self.filtered(lambda t: not t.active):
            if task.closed == False:
                raise ValidationError(_("You can not archive a task in a stage not considered closed.\n"
                                        "You can archive tasks in closed stages."))
            # if task is archived reset some values
            task.update({
                'priority': 0,
                'kanban_state': 'normal',
            })

    def action_task_send(self):
        '''
        This function opens a window to compose an email,
        with the task template message loaded by default
        '''
        self.ensure_one()
        lang = self.env.context.get('lang')
        mail_template = self.env.ref('tsm_base.tsm_task_email_template', raise_if_not_found=False)
        if mail_template and mail_template.lang:
            lang = mail_template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'tsm.task',
            'default_res_id': self.id,
            'default_use_template': bool(mail_template),
            'default_template_id': mail_template.id if mail_template else None,
            'default_composition_mode': 'comment',
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'force_email': True,
            'model_description': 'TSM Task',
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
    @api.model
    def default_get(self, fields):
        result = super(TsmTask, self).default_get(fields)
        active_model = self._context.get('active_model')
        if active_model == 'tsm.project':
            active_id = self._context.get('active_id')
            project = self.env['tsm.project'].browse(active_id)
            result['partner_id'] = project.partner_id.id

        return result

    @api.model_create_multi
    def create(self, vals_list):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # Assign new code
        for vals in vals_list:
            if vals.get('code', '/') == '/':
                vals['code'] = self.env['ir.sequence'].next_by_code('tsm.task')

        return super(TsmTask, self.with_context(context)).create(vals_list)

    def write(self, vals):
        now = fields.Datetime.now()
        # user_id change: update date_assign
        if vals.get('user_id') and 'date_assign' not in vals:
            vals['date_assign'] = now

        return super().write(vals)
    
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default['code'] = self.env['ir.sequence'].next_by_code('tsm.task')
        return super().copy(default)
