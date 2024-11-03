# Copyright 2024 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, api, fields, models

class CommissionSettlement(models.Model):
    _inherit = "commission.settlement"

    settlement_type = fields.Selection(
        selection_add=[("timepack", "Timepack")],
        ondelete={"timepack": "set default"},
    )
    timesheet_line_ids = fields.One2many(
        comodel_name="tsm.task.timesheet",
        inverse_name="settlement_id",
        string="Generated timepack lines",
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

    timepack_agent_line_id = fields.Many2one(
        comodel_name="time.pack.line.agent", index=True
    )
    timesheet_line_id = fields.Many2one(
        comodel_name="tsm.task.timesheet",
        store=True,
        related="timepack_agent_line_id.object_id",
        string="Source timesheet line",
    )
    
    @api.depends("timepack_agent_line_id")
    def _compute_date(self):
        for record in self.filtered("timepack_agent_line_id"):
            record.date = record.timepack_agent_line_id.invoice_date

    @api.depends("timepack_agent_line_id")
    def _compute_commission_id(self):
        for record in self.filtered("timepack_agent_line_id"):
            record.commission_id = record.timepack_agent_line_id.commission_id

    @api.depends("timepack_agent_line_id")
    def _compute_settled_amount(self):
        for record in self.filtered("timepack_agent_line_id"):
            record.settled_amount = record.timepack_agent_line_id.amount