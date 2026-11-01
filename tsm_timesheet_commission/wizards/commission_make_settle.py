# Copyright 2024 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class CommissionMakeSettle(models.TransientModel):
    _inherit = "commission.make.settle"

    settlement_type = fields.Selection(
        selection_add=[("timesheet", "Timesheet")],
        ondelete={"timesheet": "cascade"},
    )

    def _get_agent_lines(self, agent, date_to_agent):
        """Filter sales invoice agent lines for this type of settlement."""
        if self.settlement_type != "timesheet":
            return super()._get_agent_lines(agent, date_to_agent)
        return self.env["tsm.task.timesheet.agent"].search(
            [
                ("invoice_date", "<", date_to_agent),
                ("agent_id", "=", agent.id),
                ("settled", "=", False),
            ],
            order="invoice_date",
        )

    def _prepare_settlement_line_vals(self, settlement, line):
        """Prepare extra settlement values when the source is a timesheet agent
        line.
        """
        res = super()._prepare_settlement_line_vals(settlement, line)
        if self.settlement_type == "timesheet":
            res.update(
                {
                    "timesheet_agent_line_id": line.id,
                    "date": line.invoice_date,
                    "commission_id": line.commission_id.id,
                    "settled_amount": line.amount,
                }
            )
        return res
