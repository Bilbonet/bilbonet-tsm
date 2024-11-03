# Copyright 2024 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, exceptions, fields, models


class TsmTask(models.Model):
    _inherit = "tsm.task"

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
    settlement_count = fields.Integer(compute="_compute_settlement")
    settlement_ids = fields.One2many(
        "commission.settlement",
        string="Settlements",
        compute="_compute_settlement",
    )

    def _compute_settlement(self):
        for task in self:
            settlements = task.timesheet_ids.settlement_id
            task.settlement_ids = settlements
            task.settlement_count = len(settlements)

    @api.depends("partner_agent_ids", "timesheet_ids.agent_ids.agent_id")
    def _compute_agents(self):
        for task in self:
            task.partner_agent_ids = [
                (6, 0, task.mapped("timesheet_ids.agent_ids.agent_id").ids)
            ]

    @api.model
    def _search_agents(self, operator, value):
        tts_agents = self.env["time.pack.line.agent"].search(
            [("agent_id", operator, value)]
        )
        return [("id", "in", tts_agents.mapped("object_id.task_id").ids)]

    @api.depends("timesheet_ids.agent_ids.amount")
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = 0.0
            for line in record.timesheet_ids:
                record.commission_total += sum(x.amount for x in line.agent_ids)

    #!Cuando damos las comisiones por facturadas!!!
    # def action_post(self):
    #     """Put settlements associated to the invoices in invoiced state."""
    #     self.mapped("line_ids.settlement_id").write({"state": "invoiced"})
    #     return super().action_post()
    #!Esto impide cancelar facturas con comisiones. Adaptar a nuestro caso
    # def button_cancel(self):
    #     """Check settled lines and put settlements associated to the invoices in
    #     exception.
    #     """
    #     if any(self.mapped("invoice_line_ids.any_settled")):
    #         raise exceptions.ValidationError(
    #             _("You can't cancel an invoice with settled lines"),
    #         )
    #     self.mapped("line_ids.settlement_id").write({"state": "except_invoice"})
    #     return super().button_cancel()

    def recompute_lines_agents(self):
        self.mapped("timesheet_ids").recompute_agents()

    #!Si borramos una liquidación de comisiones. Las comisiones pasarán a no liquidadas
    # def unlink(self):
    #     """Put 'invoiced' settlements associated to the invoices back in settled state."""
    #     self.invoice_line_ids.settlement_id.filtered(
    #         lambda s: s.state == "invoiced"
    #     ).write({"state": "settled"})
    #     return super().unlink()


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

    def _filter_commission_applicable_lines(self):
        return self.filtered(
            lambda x: x.timepack_id
            and x.discount_time
            and x.amount > 0
        )

    @api.depends("task_id.partner_id")
    def _compute_agent_ids(self):
        self.agent_ids = False  # for resetting previous agents
        for record in self.filtered(lambda x: x.task_id.partner_id):
            if not record.commission_free:
                record.agent_ids = record._prepare_agents_vals_partner(
                    record.task_id.partner_id, settlement_type="timepack"
                )


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
    invoice_date = fields.Date(
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
    company_id = fields.Many2one(
        comodel_name="res.company",
        compute="_compute_company",
        store=True,
    )
    currency_id = fields.Many2one(
        related="company_id.currency_id",
    )
    
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

    @api.depends("object_id", "object_id.company_id")
    def _compute_company(self):
        for line in self:
            line.company_id = line.object_id.company_id
            
    @api.constrains("agent_id", "amount")
    def _check_settle_integrity(self):
        for record in self:
            if any(record.mapped("settled")):
                raise exceptions.ValidationError(
                    _("You can't modify a settled line"),
                )
    
    def _skip_settlement(self):
        """This function should return False if the commission can be paid.

        :return: bool
        """
        self.ensure_one()
        return (
            self.commission_id.task_stage == "closed"
            and not self.task_id.stage_id.closed
        ) or not self.task_id

    