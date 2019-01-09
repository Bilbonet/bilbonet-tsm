# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_time_pack = fields.Boolean(default=False,
        string='Use in Time Packs',
        help="If set true, it will allow you to use it in Time Packs")

    @api.onchange('type')
    def _onchange_type_timepack(self):
        if self.type != 'service':
            self.service_time_pack = False
