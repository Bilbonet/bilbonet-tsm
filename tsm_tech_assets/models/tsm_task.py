# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TsmTask(models.Model):
    _inherit = "tsm.task"

    asset_ids = fields.Many2many('tsm.tech.asset', string='Tech Asset',
                                 domain=['|', ('active', '=', False),
                                         ('active', '=', True)])
