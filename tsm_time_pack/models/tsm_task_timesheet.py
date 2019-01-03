# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields


class TsmTaskTimesheet(models.Model):
    _inherit = "tsm.task.timesheet"

    timepack_id = fields.Many2one('tsm.time.pack', 'Time Packs', index=True)
    discount_time = fields.Boolean(
        default="True",
        string="Discount Time",
        help="Indicate if discount the time from the time pack")

