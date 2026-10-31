# Copyright 2026 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from lxml import html

from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user


class TestTsmTimePack(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create({"name": "Time Pack Customer"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Support Hours",
                "type": "service",
                "service_time_pack": True,
                "list_price": 100,
            }
        )
        cls.task = cls.env["tsm.task"].create(
            {"name": "Support Task", "partner_id": cls.partner.id}
        )
        cls.manager = new_test_user(
            cls.env,
            login="time_pack_manager",
            groups="tsm_base.group_tsm_manager",
            context={"no_reset_password": True},
            company_id=cls.env.company.id,
            company_ids=[Command.set(cls.env.company.ids)],
        )

    def _pack_values(self, **values):
        return {
            "name": "Customer Support",
            "partner_id": self.partner.id,
            "product_id": self.product.id,
            "quantity": 10,
            "price_unit": 100,
            "description_sale": "Support Hours",
            "sale_autoconfirm": False,
            "privacy_visibility": "employees",
            **values,
        }

    def test_batch_create_and_copy(self):
        packs = self.env["tsm.time.pack"].create(
            [self._pack_values(quantity=5), self._pack_values(quantity=8)]
        )
        self.assertEqual(packs.mapped("contracted_hours"), [5, 8])
        self.assertEqual(len(set(packs.mapped("code"))), 2)
        copies = packs.copy()
        self.assertEqual(copies.mapped("contracted_hours"), [5, 8])
        self.assertEqual(len(set((packs + copies).mapped("code"))), 4)
        self.assertFalse(copies.sale_id)
        self.assertFalse(copies.timesheet_ids)
        self.assertNotIn("/", (packs + copies).mapped("code"))

    def test_batch_constraints(self):
        packs = self.env["tsm.time.pack"].create(
            [self._pack_values(), self._pack_values()]
        )
        packs.write({"quantity": 6, "discount": 25})
        self.assertEqual(packs.mapped("contracted_hours"), [6, 6])
        self.assertEqual(packs.mapped("price_subtotal"), [450, 450])
        for values in ({"quantity": 0}, {"discount": 101}):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                packs.write(values)

    def test_company_and_display_name(self):
        company = self.env["res.company"].create({"name": "Time Pack Company"})
        pack = (
            self.env["tsm.time.pack"]
            .with_company(company)
            .create(self._pack_values(code="TP-OTHER-COMPANY"))
        )
        self.assertEqual(pack.company_id, company)
        self.assertEqual(pack.display_name, "[TP-OTHER-COMPANY] Customer Support")
        pack.name = False
        self.assertEqual(pack.display_name, "[TP-OTHER-COMPANY]")
        pack.name = "New Title"
        self.assertEqual(pack.display_name, "[TP-OTHER-COMPANY] New Title")

    def test_timesheet_defaults_and_optional_task(self):
        pack = self.env["tsm.time.pack"].create(self._pack_values())
        lines = self.env["tsm.task.timesheet"].create(
            [{"task_id": self.task.id}, {"task_id": False}]
        )
        self.assertEqual(lines[0].timepack_id, pack)
        self.assertFalse(lines[1].timepack_id)
        contextual = (
            self.env["tsm.task.timesheet"]
            .with_context(default_task_id=self.task.id)
            .create({})
        )
        self.assertEqual(contextual.timepack_id, pack)
        other_pack = self.env["tsm.time.pack"].create(self._pack_values())
        contextual = (
            self.env["tsm.task.timesheet"]
            .with_context(
                default_task_id=self.task.id, default_timepack_id=other_pack.id
            )
            .create({})
        )
        self.assertEqual(contextual.timepack_id, other_pack)
        explicit = self.env["tsm.task.timesheet"].create(
            {"task_id": self.task.id, "timepack_id": other_pack.id}
        )
        self.assertEqual(explicit.timepack_id, other_pack)

    def test_automatic_selection_keeps_existing_order_and_active_filter(self):
        packs = self.env["tsm.time.pack"].create(
            [
                self._pack_values(date_start="2020-01-01", active=False),
                self._pack_values(date_start="2021-01-01", date_end="2021-12-31"),
                self._pack_values(date_start="2022-01-01"),
            ]
        )
        line = self.env["tsm.task.timesheet"].create({"task_id": self.task.id})
        self.assertEqual(line.timepack_id, packs[1])

    def test_hours_recompute_on_amount_flag_and_link_changes(self):
        packs = self.env["tsm.time.pack"].create(
            [self._pack_values(), self._pack_values()]
        )
        lines = self.env["tsm.task.timesheet"].create(
            [
                {"task_id": self.task.id, "timepack_id": packs[0].id, "amount": 2},
                {
                    "task_id": self.task.id,
                    "timepack_id": packs[0].id,
                    "amount": 1.5,
                    "discount_time": False,
                },
            ]
        )
        self.assertEqual(packs[0].total_hours_spent, 3.5)
        self.assertEqual(packs[0].consumed_hours, 2)
        self.assertEqual(packs[0].complimentary_hours, 1.5)
        self.assertEqual(packs[0].remaining_hours, 8)
        lines[1].discount_time = True
        self.assertEqual(packs[0].consumed_hours, 3.5)
        self.assertEqual(packs[0].progress, 35)
        lines[0].amount = 3
        self.assertEqual(packs[0].remaining_hours, 5.5)
        lines[0].timepack_id = packs[1]
        self.assertEqual(packs[0].consumed_hours, 1.5)
        self.assertEqual(packs[1].consumed_hours, 3)
        lines[1].unlink()
        self.assertEqual(packs[0].consumed_hours, 0)

    def test_sale_creation_origin_and_duplicate_guard(self):
        pack = self.env["tsm.time.pack"].create(self._pack_values(discount=20))
        sale = pack.create_sale()
        self.assertEqual(pack.sale_id, sale)
        self.assertEqual(sale.partner_id, self.partner)
        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.origin, pack.code)
        self.assertEqual(sale.order_line.product_id, self.product)
        self.assertEqual(sale.order_line.product_uom_qty, 10)
        self.assertEqual(sale.order_line.discount, 20)
        self.assertTrue(sale.message_ids)
        with self.assertRaises(UserError):
            pack.create_sale()

    def test_sale_autoconfirm(self):
        pack = self.env["tsm.time.pack"].create(
            self._pack_values(sale_autoconfirm=True)
        )
        self.assertEqual(pack.create_sale().state, "sale")

    def test_sale_requires_sales_manager(self):
        pack = self.env["tsm.time.pack"].create(self._pack_values())
        with self.assertRaises(AccessError):
            pack.with_user(self.manager).create_sale()
        self.assertFalse(pack.sale_id)

    def test_sale_amount_uses_company_currency_and_updates(self):
        currency = self.env["res.currency"].create(
            {"name": "TPX", "symbol": "T", "rounding": 0.01}
        )
        for item, rate in [(self.env.company.currency_id, 1), (currency, 2)]:
            values = {
                "currency_id": item.id,
                "company_id": self.env.company.id,
                "name": fields.Date.today(),
                "rate": rate,
            }
            existing = self.env["res.currency.rate"].search(
                [
                    (key, "=", values[key])
                    for key in ("currency_id", "company_id", "name")
                ]
            )
            if existing:
                existing.write({"rate": rate})
            else:
                self.env["res.currency.rate"].create(values)
        pricelist = self.env["product.pricelist"].create(
            {"name": "Time Pack Currency", "currency_id": currency.id}
        )
        self.partner.property_product_pricelist = pricelist
        pack = self.env["tsm.time.pack"].create(self._pack_values())
        self.assertEqual(pack.sale_amount, 0)
        sale = pack.create_sale()
        self.assertEqual(sale.currency_id, currency)
        self.assertEqual(pack.sale_amount, sale.amount_untaxed / 2)
        sale.order_line.price_unit = 200
        self.assertEqual(pack.sale_amount, sale.amount_untaxed / 2)

    def test_mail_composer_subject_and_named_attachment(self):
        pack = self.env["tsm.time.pack"].create(self._pack_values())
        template = self.env.ref(
            "tsm_time_pack.tsm_time_pack_email_template"
        ).with_context(lang="en_US")
        report = self.env.ref("tsm_time_pack.tsm_time_pack_report_detailed_action")
        action = pack.action_time_pack_send()
        self.assertNotIn("default_res_id", action["context"])
        self.assertEqual(template.report_template_ids, report)
        with patch.object(
            type(report), "_render_qweb_pdf", return_value=(b"PDF placeholder", "pdf")
        ):
            composer = (
                self.env["mail.compose.message"]
                .with_context(**action["context"])
                .create({})
            )
            self.assertEqual(composer.res_ids, repr(pack.ids))
            self.assertEqual(composer.template_id, template)
            attachments = template._generate_template_attachments(
                pack.ids, ["report_template_ids"]
            )[pack.id]["attachments"]
        subject = template._render_field("subject", pack.ids)[pack.id]
        self.assertIn(self.env.company.name, subject)
        self.assertEqual(
            attachments[0][0], f"Time_Pack_({pack.code})_Customer-Support.pdf"
        )

    def test_reports_with_empty_notes_and_multiple_tasks(self):
        pack = self.env["tsm.time.pack"].create(self._pack_values(description=False))
        task = self.task.copy({"name": "Second Support Task"})
        self.env["tsm.task.timesheet"].create(
            [
                {"task_id": self.task.id, "timepack_id": pack.id, "amount": 1},
                {"task_id": task.id, "timepack_id": pack.id, "amount": 2},
                {"timepack_id": pack.id, "amount": 0.5},
            ]
        )
        for kind in ("summary", "detailed"):
            report = self.env.ref(f"tsm_time_pack.tsm_time_pack_report_{kind}_action")
            content, _ = report._render_qweb_html(report, pack.ids)
            self.assertIn(pack.code.encode(), content)
            if kind == "detailed":
                totals = html.fromstring(content).xpath(
                    "//table[contains(@class, 'table-striped')]"
                    "/tfoot/tr/th/span[last()]"
                )
                self.assertEqual(
                    [node.text_content().strip() for node in totals],
                    ["03:30", "01:00", "02:00"],
                )
