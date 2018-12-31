# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    create_sale_order = fields.Boolean(related='stage_id.create_sale_order')
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
        sale = self.sale_id
        currency = (
                self.partner_id.property_product_pricelist.currency_id or
                self.company_currency)
        self.sale_amount = sale.currency_id.compute(
                                sale.amount_untaxed, currency)

    @api.multi
    def action_view_order(self):
        '''
        This function returns an action that display the order
        given sale order id.
        '''
        action = self.env.ref('sale.action_orders').read()[0]
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        action['res_id'] = self.sale_id.id
        return action

    @api.model
    def _prepare_sale_line(self, line, sale_id):
        sale_line = self.env['sale.order.line'].new({
            'order_id': sale_id,
            'product_id': line.product_id.id,
            'name': line.name,
            'price_unit': line.price_unit,
            'product_uom_qty': line.quantity,
            'product_uom': line.product_uom_id.id,
            'discount': line.discount,
            'tsm_task_id': line.task_id.id,
            'tsm_task_material_id': line.id,
        })

        '''Get other sale line values from product onchange'''
        sale_line.product_id_change()
        sale_line_vals = sale_line._convert_to_write(sale_line._cache)

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

        sale = self.env['sale.order'].new({
            'partner_id': self.partner_id,
            'currency_id': currency.id,
            'date_order': fields.Date.today(),
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'origin': self.code + ' - ' + self.name,
            'tsm_task_id': self.id,
        })

        '''Get other sale values from partner onchange'''
        sale.onchange_partner_id()
        return sale._convert_to_write(sale._cache)

    @api.multi
    def create_sale(self):
        """
        Create Sale order from task
        :return: Sele Order created
        """
        self.ensure_one()
        sale_vals = self._prepare_sale()
        sale = self.env['sale.order'].create(sale_vals)

        for line in self.material_ids:
            sale_line_vals = self._prepare_sale_line(line, sale.id)
            if sale_line_vals:
                sale_line_id = \
                    self.env['sale.order.line'].create(sale_line_vals)

        '''Update Task with the values from the sale order'''
        vals = {'sale_id': sale.id}
        self.update(vals)

        ''' Autoconfirm sale order if it's checked'''
        if self.sale_autoconfirm:
            sale.action_confirm()

        return sale
