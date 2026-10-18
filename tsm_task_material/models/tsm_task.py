# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError


class TsmTask(models.Model):
    _inherit = "tsm.task"

    material_ids = fields.One2many(
        comodel_name="tsm.task.material", inverse_name="task_id", string="Material used"
    )
    sale_id = fields.Many2one(
        comodel_name="sale.order", string="Sale Order", copy=False
    )
    create_sale_order = fields.Boolean(
        related="stage_id.create_sale_order",
        readonly=True,
    )
    sale_autoconfirm = fields.Boolean(
        string="Sale autoconfirm",
        default=True,
        help="If it is checked the sale order will be created "
        "and confirmed automatically",
    )
    company_currency = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
        help="Utility field to express amount currency",
    )
    sale_amount = fields.Monetary(
        compute="_compute_sale_amount",
        string="Amount of The Order",
        currency_field="company_currency",
        help="Untaxed Total of The Order",
    )

    @api.depends(
        "sale_id.amount_untaxed",
        "sale_id.currency_id",
        "sale_id.date_order",
        "company_currency",
        "company_id",
    )
    def _compute_sale_amount(self):
        for task in self:
            if task.sale_id:
                sale = task.sudo().sale_id
                company = task.company_id or task.env.company
                currency = task.company_currency or company.currency_id
                task.sale_amount = sale.currency_id._convert(
                    sale.amount_untaxed,
                    currency,
                    company,
                    fields.Date.to_date(sale.date_order)
                    or fields.Date.context_today(task),
                )
            else:
                task.sale_amount = 0

    def action_view_order(self):
        """
        This function returns an action that display the order
        given sale order id.
        """

        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "views": [[False, "form"]],
            "res_id": self.sale_id.id,
            "context": {"create": False, "show_sale": True},
        }

    def _prepare_sale(self):
        self.ensure_one()
        if not self.partner_id or not self.material_ids:
            raise ValidationError(
                self.env._(
                    "You must first select a Customer and materials for Task: %s!",
                    self.name,
                )
            )

        return {
            "partner_id": self.partner_id.id,
            "origin": self.code,
            "client_order_ref": f"[{self.code}] {self.name}",
            "company_id": (self.company_id or self.env.company).id,
            "user_id": self.user_id.id,
        }

    def create_sale(self):
        """
        Create Sale order from task
        :return: Sale Order created
        """
        self.ensure_one()
        self.check_access("write")
        if not self.env.user.has_group("sales_team.group_sale_manager"):
            raise AccessError(
                self.env._("Only sales managers can create a sale order from a task.")
            )
        if self.sale_id:
            raise UserError(self.env._("This task already has a sale order."))
        if not self.create_sale_order:
            raise UserError(
                self.env._("The task stage does not allow creating a sale order.")
            )
        task = self.with_company(self.company_id or self.env.company)
        sale_vals = task._prepare_sale()
        sale = task.env["sale.order"].create(sale_vals)
        sale.write(
            {
                "order_line": [
                    Command.create(line._prepare_sale_line(sale))
                    for line in task.material_ids
                ]
            }
        )
        sale.message_post_with_source(
            "mail.message_origin_link",
            render_values={"self": sale, "origin": task},
            subtype_xmlid="mail.mt_note",
        )

        # Update Task with the values from the sale order
        vals = {"sale_id": sale.id}
        task.update(vals)
        # Autoconfirm sale order if it's checked
        if task.sale_autoconfirm:
            sale.action_confirm()

        return sale

    @api.ondelete(at_uninstall=False)
    def _unlink_except_sale_order(self):
        for task in self:
            if task.sale_id:
                raise UserError(
                    self.env._(
                        "You cannot delete a task with sale order.\n"
                        "You can either delete the task's sale order and then "
                        "delete the task or simply deactivate the task."
                    )
                )

    @api.constrains("company_id", "sale_id")
    def _check_sale_company(self):
        for task in self:
            if (
                task.sale_id
                and task.company_id
                and task.sale_id.company_id != task.company_id
            ):
                raise ValidationError(
                    self.env._(
                        "The task and its sale order must belong to the same company."
                    )
                )

    @api.constrains("active")
    def _check_archiving_restrictions(self):
        # Only sales manager can archive a task with materials and no sale order
        if not self.env.user.has_group("sales_team.group_sale_manager"):
            for task in self.filtered(lambda t: not t.active):
                if task.material_ids and not task.sale_id:
                    raise ValidationError(
                        self.env._(
                            "Only sales manager can archive tasks "
                            "with materials and no sale order.\n"
                            "Ask for manager to archive the task.\n\n"
                            "Task:[%(task_code)s] - %(task_name)s",
                            task_code=task.code,
                            task_name=task.name,
                        )
                    )
        return super()._check_archiving_restrictions()
