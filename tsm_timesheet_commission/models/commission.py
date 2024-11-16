# Copyright 2024 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class Commission(models.Model):
    _inherit = "commission"

    task_stage = fields.Selection(
        [("open", "Task Based"), ("closed", "Task Closed")],
        string="Task Status",
        default="open",
        help="Select the task status for settling the commissions:\n"
        "* 'Task Based': Commissions are settled when the task is in any stage.\n"
        "* 'Task Closed': Commissions are settled when the task is in a closed stage.",
    )
