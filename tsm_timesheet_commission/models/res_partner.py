# Copyright 2024 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    tsm_commission_id = fields.Many2one(
        string="TSM Commission",
        comodel_name="commission",
        help="This is the default commission used in the TSM timesheets where "
        "this agent is assigned. It can be changed on each operation if "
        "needed.",
    )
