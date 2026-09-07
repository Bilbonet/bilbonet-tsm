# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError


class TsmTask(models.Model):
    _name = "tsm.task"
    _description = "Tech Support Management Task"
    _order = "date_start desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _get_default_stage_id(self):
        """Gives default stage_id"""
        stage_id = self.env["tsm.task.type"].search([], order="sequence", limit=1)
        if not stage_id:
            return False

        return stage_id

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """Read group customization in order to display all the stages in the
        kanban view, even if they are empty
        """
        return stages.with_user(SUPERUSER_ID).search([], order="sequence, id")

    code = fields.Char(string="Task Code", required=True, default="/", readonly=True)
    sequence = fields.Integer(
        default=10,
        copy=False,
        help="Sequence of the task when displaying tasks",
    )
    name = fields.Char(string="Task Title", required=True, index=True)
    active = fields.Boolean(
        default=True,
        copy=False,
        tracking=True,
        help="If the active field is set to False, it will allow you to hide"
        " the task without removing it.",
    )
    priority = fields.Selection(
        selection=[("0", "Low"), ("1", "Normal")],
        default="0",
        index=True,
        help="Important task order",
    )
    stage_id = fields.Many2one(
        comodel_name="tsm.task.type",
        string="Stage",
        index=True,
        copy=False,
        group_expand="_read_group_stage_ids",
        default=_get_default_stage_id,
    )
    closed = fields.Boolean(related="stage_id.closed", readonly=True)
    tags_in_task = fields.Boolean(string="Use Tags in Tasks")
    tag_ids = fields.Many2many(
        comodel_name="tsm.task.tags",
        string="Tags",
    )
    kanban_state = fields.Selection(
        selection=[("normal", "Grey"), ("done", "Green"), ("blocked", "Red")],
        copy=False,
        default="normal",
        required=True,
        help="A task's kanban state indicates special situations "
        "affecting it:\n"
        " * Grey is the default situation\n"
        " * Red indicates something is preventing "
        "the progress of this task\n"
        " * Green indicates the task is ready to be "
        "pulled to the next stage",
    )
    kanban_state_label = fields.Char(
        compute="_compute_kanban_state_label",
    )
    color = fields.Integer(string="Color Index")
    date_start = fields.Date(
        string="Starting Date",
        default=fields.Date.context_today,
        index=True,
        copy=False,
    )
    date_assign = fields.Date(
        string="Assigning Date",
        default=fields.Date.context_today,
        copy=False,
        tracking=True,
    )
    date_deadline = fields.Date(string="Deadline", index=True, copy=False)
    date_end = fields.Date(string="Ending Date", index=True, copy=False)
    legend_blocked = fields.Char(
        related="stage_id.legend_blocked",
        string="Kanban Blocked Explanation",
        readonly=True,
        related_sudo=False,
    )
    legend_done = fields.Char(
        related="stage_id.legend_done",
        string="Kanban Valid Explanation",
        readonly=True,
        related_sudo=False,
    )
    legend_normal = fields.Char(
        related="stage_id.legend_normal",
        string="Kanban Ongoing Explanation",
        readonly=True,
        related_sudo=False,
    )
    description = fields.Html(
        string="Task Description",
        sanitize=True,
        strip_style=False,
        translate=False,
        help="Details, notes and aclarations about the task.",
    )
    project_id = fields.Many2one(
        comodel_name="tsm.project", string="Project", index=True, tracking=True
    )
    manager_id = fields.Many2one(
        comodel_name="res.users",
        string="Project Manager",
        related="project_id.user_id",
        readonly=True,
        related_sudo=False,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        default=lambda self: self.env.uid,
        required=True,
        copy=False,
        index=True,
        tracking=True,
    )
    partner_id = fields.Many2one("res.partner", string="Customer")
    contact_id = fields.Many2one(
        comodel_name="res.partner",
        string="Contact",
        domain="[('parent_id', '=', partner_id),"
        "('type', 'in', ('contact','other'))]",
    )
    privacy_visibility = fields.Selection(
        selection=[
            ("followers", "On invitation only"),
            ("employees", "Visible by all employees"),
        ],
        string="Privacy",
        required=True,
        default="followers",
        help="Holds visibility of the task:\n "
        "- On invitation only: Employees may only "
        "see the followed tasks\n"
        "- Visible by all employees: Employees "
        "may see all tasks\n",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    _sql_constraints = [
        ("tsm_task_unique_code", "UNIQUE (code)", _("The code must be unique!")),
    ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        for task in self:
            task.display_name = f"[{task.code}] {task.name}"

    @api.depends("stage_id", "kanban_state")
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == "normal":
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == "blocked":
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    @api.onchange("project_id")
    def _onchange_project(self):
        if self.project_id:
            if self.project_id.partner_id != self.partner_id:
                self.partner_id = self.project_id.partner_id

    @api.onchange("user_id")
    def _onchange_user(self):
        if self.user_id:
            self.date_assign = fields.Datetime.now()

    @api.constrains("active")
    def _check_archiving_restrictions(self):
        """
        Only archive task in closed stages.
        Constraint should be tested just after archiving a task,
        but shouldn't be raised when unarchiving a task.
        """
        for task in self.filtered(lambda t: not t.active):
            if not task.closed:
                raise ValidationError(
                    _(
                        "You can not archive a task in a stage not considered closed.\n"
                        "You can archive tasks in closed stages."
                    )
                )
            # if task is archived reset some values
            task.update(
                {
                    "priority": "0",
                    "kanban_state": "normal",
                }
            )

    def action_task_send(self):
        """
        This function opens a wizard to compose an email,
        with the task template message loaded by default
        """
        self.ensure_one()
        template_id = self.env["ir.model.data"]._xmlid_to_res_id(
            "tsm_base.tsm_task_email_template",
            raise_if_not_found=False,
        )
        ctx = {
            "default_model": "tsm.task",
            "default_res_ids": [self.id],
            "active_model": "tsm.task",
            "active_id": self.id,
            "active_ids": [self.id],
            "default_use_template": bool(template_id),
            "default_template_id": template_id,
            "default_composition_mode": "comment",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }

    def action_inactive(self):
        return self.write({"active": False})

    def action_active(self):
        return self.write({"active": True})

    # ------------------
    # CRUD overrides
    # ------------------
    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        active_model = self._context.get("active_model")
        if active_model == "tsm.project":
            active_id = self._context.get("active_id")
            project = self.env["tsm.project"].browse(active_id)
            result["partner_id"] = project.partner_id.id

        return result

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("code", "/") == "/":
                vals["code"] = self.env["ir.sequence"].next_by_code("tsm.task")

        return super().create(vals_list)

    def copy(self, default=None):
        default = dict(default or {})
        copies = self.browse()
        for task in self:
            values = dict(
                default,
                code=self.env["ir.sequence"].next_by_code("tsm.task"),
                name=f"{task.name} (copy)",
            )
            copies |= super(TsmTask, task).copy(values)
        return copies
