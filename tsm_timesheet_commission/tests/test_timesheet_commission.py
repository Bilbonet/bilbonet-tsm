# Copyright 2026 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase

from odoo.addons.web.models.models import RecordSnapshot


class TestTimesheetCommission(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product = cls.env["product.product"].create(
            {"name": "Commission Support", "type": "service", "list_price": 100}
        )
        cls.commission = cls.env["commission"].create(
            {
                "name": "TSM 10%",
                "fix_qty": 10,
                "settlement_type": "timesheet",
                "timesheet_product_id": cls.product.id,
            }
        )
        cls.invoice_commission = cls.env["commission"].create(
            {"name": "Invoice 5%", "fix_qty": 5, "settlement_type": "sale_invoice"}
        )
        cls.agents = cls.env["res.partner"].create(
            [
                {
                    "name": name,
                    "agent": True,
                    "commission_id": cls.invoice_commission.id,
                    "tsm_commission_id": cls.commission.id,
                    "settlement": "monthly",
                }
                for name in ("TSM Agent One", "TSM Agent Two")
            ]
        )
        cls.customer = cls.env["res.partner"].create(
            {"name": "Commission Customer", "agent_ids": [Command.set(cls.agents.ids)]}
        )
        cls.open_stage = cls.env["tsm.task.type"].create(
            {"name": "Commission Open", "closed": False}
        )
        cls.closed_stage = cls.env["tsm.task.type"].create(
            {"name": "Commission Closed", "closed": True}
        )
        cls.task = cls.env["tsm.task"].create(
            {
                "name": "Commission Task",
                "partner_id": cls.customer.id,
                "stage_id": cls.open_stage.id,
            }
        )

    def _timesheet(self, **values):
        return self.env["tsm.task.timesheet"].create(
            {
                "task_id": self.task.id,
                "date_time": "2026-01-15 10:00:00",
                "amount": 2,
                **values,
            }
        )

    def _settle(self):
        wizard = self.env["commission.make.settle"].create(
            {
                "settlement_type": "timesheet",
                "date_to": "2026-02-01",
                "agent_ids": [Command.set(self.agents.ids)],
            }
        )
        return wizard.action_settle()

    def test_tsm_commission_and_totals(self):
        line = self._timesheet()
        self.assertEqual(line.agent_ids.agent_id, self.agents)
        self.assertEqual(line.agent_ids.commission_id, self.commission)
        self.assertEqual(line.agent_ids.mapped("amount"), [20, 20])
        self.assertEqual(line.commission_amount, 40)
        self.assertEqual(self.task.commission_total, 40)
        self.assertEqual(self.task.partner_agent_ids, self.agents)

    def test_filter_uses_tsm_commission_type(self):
        self.agents[1].tsm_commission_id = self.invoice_commission
        line = self._timesheet()
        self.assertEqual(line.agent_ids.agent_id, self.agents[0])

    def test_inline_agent_values_survive_onchange_serialization(self):
        """Hidden nested agents must carry their values back to the web client."""
        views = (
            ("tsm.task", "tsm_base.tsm_task_form_view", "form", True),
            (
                "tsm.task.timesheet",
                "tsm_task_timesheet.tsm_task_timesheet_line_tree",
                "list",
                False,
            ),
            ("tsm.time.pack", "tsm_time_pack.tsm_time_pack_form_view", "form", True),
        )
        for model_name, view_ref, view_type, nested in views:
            with self.subTest(view=view_ref):
                model = self.env[model_name]
                view = model.get_view(
                    view_id=self.env.ref(view_ref).id, view_type=view_type
                )
                spec = model._get_fields_spec(view)
                if nested:
                    spec = spec["timesheet_ids"]["fields"]
                agent_spec = spec["agent_ids"]
                self.assertTrue(
                    {"agent_id", "commission_id", "specific_price", "price_unit"}
                    <= agent_spec.get("fields", {}).keys()
                )
                line = self.env["tsm.task.timesheet"].new(
                    {
                        "task_id": self.task.id,
                        "date_time": "2026-01-15 10:00:00",
                        "amount": 2,
                    }
                )
                line.agent_ids[0].specific_price = 50
                snapshot = RecordSnapshot(line, {"agent_ids": agent_spec})
                commands = snapshot.diff({})["agent_ids"]
                self.assertEqual(len(commands), len(self.agents))
                agent_ids = set()
                for operation, _record_id, values in commands:
                    self.assertEqual(operation, Command.CREATE)
                    agent_ids.add(values["agent_id"]["id"])
                    self.assertEqual(values["commission_id"]["id"], self.commission.id)
                self.assertEqual(agent_ids, set(self.agents.ids))
                self.assertEqual(commands[0][2]["specific_price"], 50)

    def test_optional_date_and_task(self):
        line = self._timesheet(date_time=False)
        self.assertFalse(any(line.agent_ids.mapped("invoice_date")))
        standalone = self._timesheet(task_id=False, date_time=False)
        self.assertFalse(standalone.agent_ids)

    def test_batch_delete_unsettled(self):
        line = self._timesheet()
        agents = line.agent_ids
        agents.unlink()
        self.assertFalse(agents.exists())
        lines = self._timesheet() + self._timesheet()
        self.assertEqual(len(lines.agent_ids), 4)
        lines.unlink()
        self.assertFalse(lines.exists())

    def test_settlement_cancel_and_delete(self):
        line = self._timesheet()
        self.assertFalse(line.any_settled)
        line.write({"date_time": "2026-01-16 10:00:00", "amount": 3})
        self.assertEqual(line.agent_ids.mapped("amount"), [30, 30])
        action = self._settle()
        self.assertEqual(action["res_model"], "commission.settlement")
        self.assertTrue(line.any_settled)
        settlements = line.agent_ids.settlement_line_ids.settlement_id
        self.assertEqual(len(settlements), 2)
        self.assertEqual(settlements.mapped("total"), [30, 30])
        self.assertTrue(all(settlements.line_ids.mapped("timesheet_line_id")))
        self.assertFalse(self._settle())
        with self.assertRaises(UserError), self.cr.savepoint():
            line.agent_ids.unlink()
        with self.assertRaises(UserError), self.cr.savepoint():
            line.unlink()
        settlements[0].action_cancel()
        self.assertTrue(line.any_settled)
        settlements[1:].action_cancel()
        self.assertFalse(line.any_settled)
        line.write({"date_time": "2026-01-17 10:00:00", "amount": 4})
        self.assertEqual(line.agent_ids.mapped("amount"), [40, 40])
        line.unlink()
        self.assertFalse(line.exists())

    def test_closed_task_gate(self):
        self.commission.task_stage = "closed"
        line = self._timesheet()
        self.assertFalse(self._settle())
        self.task.stage_id = self.closed_stage
        self.assertTrue(self._settle())
        self.assertTrue(line.any_settled)

    def test_specific_price_and_pack_selection(self):
        line = self._timesheet()
        agent_line = line.agent_ids[0]
        agent_line.specific_price = 50
        self.assertEqual(agent_line.amount, 10)
        pack = self.env["tsm.time.pack"].create(
            {
                "name": "Commission Pack",
                "partner_id": self.customer.id,
                "product_id": self.product.id,
                "quantity": 10,
                "price_unit": 80,
            }
        )
        line.timepack_id = pack
        self.assertEqual(line.agent_ids[1].amount, 16)
        line.discount_time = False
        self.assertEqual(line.agent_ids[1].amount, 0)
        self.assertEqual(agent_line.amount, 10)

    def test_mixed_settlement_sources(self):
        """TSM computations must preserve invoice and manual settlement lines."""
        line = self._timesheet()
        invoice_agent = self.env["account.invoice.line.agent"].new(
            {
                "agent_id": self.agents[0].id,
                "commission_id": self.invoice_commission.id,
                "invoice_date": fields.Date.to_date("2026-01-10"),
                "amount": 7,
            }
        )
        settlement_line = self.env["commission.settlement.line"]
        tsm = settlement_line.new({"timesheet_agent_line_id": line.agent_ids[0].id})
        invoice = settlement_line.new({"invoice_agent_line_id": invoice_agent.id})
        manual = settlement_line.new(
            {
                "date": "2026-01-01",
                "commission_id": self.commission.id,
                "settled_amount": 3,
            }
        )
        lines = tsm + invoice + manual
        lines._compute_date()
        lines._compute_commission_id()
        lines._compute_settled_amount()
        self.assertEqual(tsm.date, fields.Date.to_date("2026-01-15"))
        self.assertEqual(tsm.commission_id, self.commission)
        self.assertEqual(tsm.settled_amount, 20)
        self.assertEqual(invoice.date, fields.Date.to_date("2026-01-10"))
        self.assertEqual(invoice.commission_id, self.invoice_commission)
        self.assertEqual(invoice.settled_amount, 7)
        self.assertEqual(manual.date, fields.Date.to_date("2026-01-01"))
        self.assertEqual(manual.commission_id, self.commission)
        self.assertEqual(manual.settled_amount, 3)
