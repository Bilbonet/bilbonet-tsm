# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, _


class TsmTaskType(models.Model):
    _inherit = 'tsm.task.type'

    create_sale_order = fields.Boolean(
        help="If you mark this check, when a task is in this state, "
             "it will be able to create sale order",)
