# Copyright 2024 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class Commission(models.Model):
    _inherit = "commission"

    task_stage = fields.Selection(
        selection=[("open", "Task Based"), ("closed", "Task Closed")],
        string="Task Status",
        default="open",
        help="""
        Select the task status for settling the commissions:\n
        * 'Task Based': Commissions are settled when the task is in
                        any stage.\n
        * 'Task Closed': Commissions are settled when the task is in
                        a closedstage.
        """,
    )
    timesheet_product_id = fields.Many2one(
        comodel_name="product.product",
        string="TimeSheet Product",
        domain="[('commission_free', '=', False)]",
        help="""
        Product used to set commissions when there is not time pack in
        the timesheet line""",
    )
