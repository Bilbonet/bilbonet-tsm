# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class TsmTaskMaterial(models.Model):
    _name = "tsm.task.material"
    _description = "TSM Task Material Used"
    _order = "sequence,id"

    task_id = fields.Many2one(comodel_name='project.task',
                              string='Task', ondelete='cascade',
                              required=True)
    product_id = fields.Many2one(comodel_name='product.product',
                                 string='Product', required=True)
    name = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    product_uom_id = fields.Many2one(comodel_name='product.uom',
                                     string='Unit of Measure')
    price_unit = fields.Float(string='Unit Price', default=0.0, required=True)
    price_subtotal = fields.Float(compute='_compute_price_subtotal',
                                  digits=dp.get_precision('Account'),
                                  string='Sub Total')
    discount = fields.Float(string='Discount (%)',
                    digits=dp.get_precision('Discount'),
                    help='Discount that is applied in generated sale orders.'
                        ' It should be less or equal to 100')
    sequence = fields.Integer(string="Sequence", default=10,
                    help="Sequence of the line in the list of materials")
    company_currency = fields.Many2one('res.currency',
                            related='task_id.company_id.currency_id',
                            readonly=True,
                            help='Utility field to express amount currency')

    @api.multi
    @api.depends('quantity', 'price_unit', 'discount')
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            discount = line.discount / 100
            subtotal *= 1 - discount
            line.price_subtotal = subtotal

    @api.multi
    @api.constrains('quantity')
    def _check_quantity(self):
        for material in self:
            if not material.quantity > 0.0:
                raise ValidationError(
                    _('Quantity of material consumed must be greater than 0.'))

    @api.multi
    @api.constrains('discount')
    def _check_discount(self):
        for line in self:
            if line.discount > 100:
                raise ValidationError(
                    _("Discount should be less or equal to 100"))

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            return {'domain': {'product_uom_id': []}}

        vals = {}
        domain = {'product_uom_id': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom_id or (
                self.product_id.uom_id.category_id.id !=
                self.product_uom_id.category_id.id):
            vals['product_uom_id'] = self.product_id.uom_id

        partner = self.env.user.partner_id
        product = self.product_id.with_context(
            lang=partner.lang,
            partner=partner.id,
            uom=self.product_uom_id.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        vals['price_unit'] = product.list_price
        self.update(vals)
        return {'domain': domain}
