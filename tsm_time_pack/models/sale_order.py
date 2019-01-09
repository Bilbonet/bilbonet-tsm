# Copyright 2019 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tsm_time_pack_id = fields.Many2one(comodel_name='tsm.time.pack',
                            string='TSM Time Pack related',
                            help="Time Pack related that generated this order")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tsm_time_pack_id = fields.Many2one(comodel_name='tsm.time.pack',
                string='TSM Time Pack related that generated this order line')
