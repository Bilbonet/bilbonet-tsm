# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TsmTaskType(models.Model):
    _inherit = 'tsm.task.type'

    create_sale_order = fields.Boolean(
        help="If you mark this check, when a task is in this state, "
             "it will be able to create sale order",)


class TsmTask(models.Model):
    _inherit = "tsm.task"

    material_ids = fields.One2many(comodel_name='tsm.task.material',
        inverse_name='task_id', string='Material used')
    sale_id = fields.Many2one(comodel_name='sale.order',
        string='Sale Order', copy=False)
    create_sale_order = fields.Boolean(related='stage_id.create_sale_order',
        readonly="true",)
    sale_autoconfirm = fields.Boolean(string='Sale autoconfirm', default=True,
        help='If it is checked the sale order will be created '
             'and confirmed automatically')
    company_currency = fields.Many2one('res.currency',
        related='company_id.currency_id', readonly=True,
        help='Utility field to express amount currency')
    sale_amount = fields.Monetary(compute='_compute_sale_amount',
        string="Amount of The Order", currency_field='company_currency',
        help="Untaxed Total of The Order")

    @api.depends('sale_id')
    def _compute_sale_amount(self):
        if self.sale_id:
            sale = self.sudo().sale_id
            currency = (
                self.company_currency or
                self.partner_id.property_product_pricelist.currency_id or
                self.env.user.company_id.currency_id)
            self.sale_amount = sale.currency_id._convert(
                sale.amount_untaxed, currency,
                self.company_id, self.date_start or fields.Date.today())

    def action_view_order(self):
        '''
        This function returns an action that display the order
        given sale order id.
        '''

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
            raise ValidationError(_("You must first select a Customer "
                                    "and materials for Task: %s!") % self.name)

        currency = (
            self.company_currency or
            self.partner_id.property_product_pricelist.currency_id or
            self.env.user.company_id.currency_id)

        sale = self.env['sale.order'].with_context(
            force_company=self.company_id.id,
        ).new({
            'company_id': self.company_id.id,
            'partner_id': self.partner_id,
        })

        # Get partner extra fields
        sale.onchange_partner_id()
        # Write the resulting virtual record modifications made by the onchange call
        sale_vals = sale._convert_to_write(sale._cache)

        sale_vals.update({
            'client_order_ref': '[' + self.code + '] ' + self.name,
            'currency_id': currency.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'user_id': self.user_id.id,
            'pricelist_id': self.partner_id.property_product_pricelist.id,
        })
        return sale_vals

    def create_sale(self):
        """
        Create Sale order from task
        :return: Sale Order created
        """
        self.ensure_one()
        sale_vals = self._prepare_sale()

        for line in self.material_ids:
            sale_vals.setdefault('order_line', [])
            sale_line_vals = line._prepare_sale_line()
            if sale_line_vals:
                sale_vals['order_line'].append(
                    (0, 0, sale_line_vals)
                )
        sale = self.env['sale.order'].create(sale_vals)
        sale.message_post_with_view('mail.message_origin_link',
            values={'self': sale, 'origin': self},
            subtype_id=self.env.ref('mail.mt_note').id)

        # Update Task with the values from the sale order
        vals = {'sale_id': sale.id}
        self.update(vals)
        # Autoconfirm sale order if it's checked
        if self.sale_autoconfirm:
            sale.action_confirm()

        return sale

    def unlink(self):
        for task in self:
            if task.sale_id:
                raise UserError(_("You cannot delete a task with sale order. "
                "You can either delete the task's sale order and then delete "
                "the task or simply deactivate the task."))
        res = super(TsmTask, self).unlink()
        return res
