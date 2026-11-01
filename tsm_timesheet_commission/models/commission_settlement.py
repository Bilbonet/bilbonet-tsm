# Copyright 2024 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class CommissionSettlement(models.Model):
    _inherit = "commission.settlement"

    settlement_type = fields.Selection(
        selection_add=[("timesheet", "Timesheet")],
        ondelete={"timesheet": "set default"},
    )
    timesheet_line_ids = fields.One2many(
        comodel_name="tsm.task.timesheet",
        inverse_name="settlement_id",
        string="Generated timesheet lines",
        readonly=True,
    )
    task_id = fields.Many2one(
        string="Generated Task",
        store=True,
        comodel_name="tsm.task",
        compute="_compute_task_id",
    )

    @api.depends("timesheet_line_ids")
    def _compute_task_id(self):
        for record in self:
            record.task_id = record.timesheet_line_ids.filtered(
                lambda x: x.task_id.stage_id.closed
            )[:1].task_id


class SettlementLine(models.Model):
    _inherit = "commission.settlement.line"

    timesheet_agent_line_id = fields.Many2one(
        comodel_name="tsm.task.timesheet.agent", index=True
    )
    partner_id = fields.Many2one(related="timesheet_line_id.task_partner_id")
    task_id = fields.Many2one(
        related="timesheet_line_id.task_id",
    )
    timesheet_line_id = fields.Many2one(
        comodel_name="tsm.task.timesheet",
        store=True,
        related="timesheet_agent_line_id.object_id",
        string="Source timesheet line",
    )

    @api.depends("timesheet_agent_line_id")
    def _compute_date(self):
        timesheet_lines = self.filtered("timesheet_agent_line_id")
        res = super(SettlementLine, self - timesheet_lines)._compute_date()
        for record in timesheet_lines:
            record.date = record.timesheet_agent_line_id.invoice_date
        return res

    @api.depends("timesheet_agent_line_id")
    def _compute_commission_id(self):
        timesheet_lines = self.filtered("timesheet_agent_line_id")
        res = super(SettlementLine, self - timesheet_lines)._compute_commission_id()
        for record in timesheet_lines:
            record.commission_id = record.timesheet_agent_line_id.commission_id
        return res

    @api.depends("timesheet_agent_line_id")
    def _compute_settled_amount(self):
        timesheet_lines = self.filtered("timesheet_agent_line_id")
        res = super(SettlementLine, self - timesheet_lines)._compute_settled_amount()
        for record in timesheet_lines:
            record.settled_amount = record.timesheet_agent_line_id.amount
        return res
