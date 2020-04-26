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
                                   inverse_name='task_id',
                                   string='Material used',
                                   )
    sale_id = fields.Many2one(comodel_name='sale.order',
                              copy=False,
                              string='Sale Order',
                              )
    create_sale_order = fields.Boolean(related='stage_id.create_sale_order',
                                       readonly="true",)
    sale_autoconfirm = fields.Boolean(
                    string='Sale autoconfirm',
                    default=True,
                    help='If it is checked the sale order will be created '
                         'and confirmed automatically',
                    )
    company_currency = fields.Many2one('res.currency',
                            related='company_id.currency_id',
                            readonly=True,
                            help='Utility field to express amount currency')
    sale_amount = fields.Monetary(compute='_compute_sale_amount',
                                  string="Amount of The Order",
                                  help="Untaxed Total of The Order",
                                  currency_field='company_currency',
                                  )

    @api.depends('sale_id')
    def _compute_sale_amount(self):
        if self.sale_id:
            sale = self.sudo().sale_id
            currency = (
                    self.partner_id.property_product_pricelist.currency_id or
                    self.company_currency or
                    self.env.user.company_id.currency_id)
            self.sale_amount = sale.currency_id._convert(
                sale.amount_untaxed, currency,
                self.company_id, self.date_start or fields.Date.today())

    @api.multi
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

    @api.model
    def _prepare_sale_line(self, line, sale_id):
        sale_line = self.env['sale.order.line'].new({
            'order_id': sale_id,
            'product_id': line.product_id.id,
            'product_uom': line.product_uom_id.id,
        })

        # Get other sale line values from product onchange
        sale_line.product_id_change()
        sale_line_vals = sale_line._convert_to_write(sale_line._cache)

        sale_line_vals.update({
            'name': line.name,
            'price_unit': line.price_unit,
            'product_uom_qty': line.quantity,
            'discount': line.discount,
            'tsm_task_id': line.task_id.id,
            'tsm_task_material_id': line.id,
        })

        return sale_line_vals

    @api.multi
    def _prepare_sale(self):
        self.ensure_one()
        if not self.partner_id or not self.material_ids:
            raise ValidationError(_("You must first select a Customer "
                                    "and materials for Task: %s!") % self.name)

        currency = (
                self.partner_id.property_product_pricelist.currency_id or
                self.company_currency)

        sale = self.env['sale.order'].new({'partner_id': self.partner_id})
        # Get partner extra fields
        sale.onchange_partner_id()
        # Write the resulting virtual record modifications made by the onchange call
        sale_vals = sale._convert_to_write(sale._cache)

        sale_vals.update({
            'origin': self.code + ' - ' + self.name,
            'currency_id': currency.id,
            'payment_term_id': self.partner_id.property_payment_term_id.id,
            'payment_mode_id': self.partner_id.customer_payment_mode_id.id,
            'fiscal_position_id': self.partner_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'pricelist_id': self.partner_id.property_product_pricelist.id,
            'tsm_task_id': self.id,
        })

        return sale_vals

    @api.multi
    def create_sale(self):
        """
        Create Sale order from task
        :return: Sale Order created
        """
        self.ensure_one()
        sale_vals = self._prepare_sale()
        sale = self.env['sale.order'].create(sale_vals)

        for line in self.material_ids:
            sale_line_vals = self._prepare_sale_line(line, sale.id)
            if sale_line_vals:
                sale_line_id = \
                    self.env['sale.order.line'].create(sale_line_vals)

        # Update Task with the values from the sale order
        vals = {'sale_id': sale.id}
        self.update(vals)

        # Autoconfirm sale order if it's checked
        if self.sale_autoconfirm:
            sale.action_confirm()

        return sale

    @api.multi
    def unlink(self):
        for task in self:
            if task.sale_id:
                raise UserError(_("You cannot delete a task with sale order. "
                "You can either delete the task's sale order and then delete "
                "the task or simply deactivate the task."))
        res = super(TsmTask, self).unlink()
        return res
