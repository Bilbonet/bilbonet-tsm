# Copyright 2024 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class TsmTask(models.Model):
    _inherit = "tsm.task"
    
    @api.depends("timesheet_ids.agent_ids.amount")
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = sum(record.mapped("timesheet_ids.agent_ids.amount"))

    commission_total = fields.Float(
        string="Commissions",
        compute="_compute_commission_total",
        store=True,
    )

    partner_agent_ids = fields.Many2many(
        string="Agents",
        comodel_name="res.partner",
        compute="_compute_agents",
        search="_search_agents",
    )

    @api.depends("partner_agent_ids", "timesheet_ids.agent_ids.agent_id")
    def _compute_agents(self):
        for so in self:
            so.partner_agent_ids = [
                (6, 0, so.mapped("timesheet_ids.agent_ids.agent_id").ids)
            ]

    @api.model
    def _search_agents(self, operator, value):
        tts_agents = self.env["time.pack.line.agent"].search(
            [("agent_id", operator, value)]
        )
        return [("id", "in", tts_agents.mapped("object_id.task_id").ids)]

    def recompute_lines_agents(self):
        self.mapped("timesheet_ids").recompute_agents()
        
        
class TsmTaskTimesheet(models.Model):
    _inherit = [
        "tsm.task.timesheet",
        "commission.mixin",
    ]
    _name = "tsm.task.timesheet"

    agent_ids = fields.One2many(comodel_name="time.pack.line.agent")
    any_settled = fields.Boolean(compute="_compute_any_settled")
    
    settlement_id = fields.Many2one(
        comodel_name="commission.settlement",
        help="Settlement that generates this invoice line",
        copy=False,
    )

    @api.depends("agent_ids", "agent_ids.settled")
    def _compute_any_settled(self):
        for record in self:
            record.any_settled = any(record.mapped("agent_ids.settled"))
            
    @api.depends("task_id.partner_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # for resetting previous agents
        for record in self.filtered(lambda x: x.task_id.partner_id):
            if not record.commission_free:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record.task_id.partner_id, settlement_type="timepack_invoice"
                )

    # def _prepare_invoice_line(self, **optional_values):
    #     vals = super()._prepare_invoice_line(**optional_values)
    #     vals["agent_ids"] = [
    #         (0, 0, {"agent_id": x.agent_id.id, "commission_id": x.commission_id.id})
    #         for x in self.agent_ids
    #     ]
    #     return vals
 
    
class TimePackLineAgent(models.Model):
    _inherit = "commission.line.mixin"
    _name = "time.pack.line.agent"
    _description = "Agent detail of commission line in timesheets"

    object_id = fields.Many2one(comodel_name="tsm.task.timesheet")
    task_id = fields.Many2one(
        string="Task",
        comodel_name="tsm.task",
        related="object_id.task_id",
        store=True,
    )
    task_date = fields.Date(
        string="Task date",
        related="task_id.date_start",
        store=True,
        readonly=True,
    )
    settlement_line_ids = fields.One2many(
        comodel_name="commission.settlement.line",
        inverse_name="timepack_agent_line_id",
    )
    settled = fields.Boolean(compute="_compute_settled", store=True)
    
    @api.depends(
        "commission_id",
        "object_id.timepack_id.price_unit",
        "object_id.timepack_id.product_id",
        "object_id.amount",
    )
    def _compute_amount(self):
        for line in self:
            timesheet_line = line.object_id
            subtotal = timesheet_line.timepack_id.price_unit * timesheet_line.amount
            line.amount = line._get_commission_amount(
                line.commission_id,
                subtotal,
                timesheet_line.timepack_id.product_id,
                timesheet_line.amount,
            )

    @api.depends(
        "settlement_line_ids",
        "settlement_line_ids.settlement_id.state",
        "task_id",
        "task_id.stage_id",
    )
    def _compute_settled(self):
        # Count lines of not open or paid invoices as settled for not
        # being included in settlements
        for line in self:
            line.settled = any(
                x.settlement_id.state != "cancel" for x in line.settlement_line_ids
            )