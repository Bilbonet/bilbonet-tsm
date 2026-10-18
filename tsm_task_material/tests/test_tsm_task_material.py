# Copyright 2026 Jesus Ramiro (Bilbonet)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, fields
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests.common import TransactionCase, new_test_user


class TestTsmTaskMaterial(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Material Customer"})
        cls.stage = cls.env["tsm.task.type"].create(
            {"name": "Ready for sale", "create_sale_order": True, "closed": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Material", "list_price": 12.0, "taxes_id": [Command.clear()]}
        )
        cls.user = new_test_user(
            cls.env,
            login="tsm_material_user",
            groups="tsm_base.group_tsm_user",
            context={"no_reset_password": True},
            company_id=cls.env.company.id,
            company_ids=[Command.set(cls.env.company.ids)],
        )
        cls.sales_user = new_test_user(
            cls.env,
            login="tsm_material_sales_user",
            groups="tsm_base.group_tsm_user,sales_team.group_sale_salesman",
            context={"no_reset_password": True},
            company_id=cls.env.company.id,
            company_ids=[Command.set(cls.env.company.ids)],
        )

    def _create_task(self, **values):
        return self.env["tsm.task"].create(
            {
                "name": "Material Task",
                "partner_id": self.customer.id,
                "stage_id": self.stage.id,
                "sale_autoconfirm": False,
                **values,
            }
        )

    def _create_material(self, task, **values):
        return self.env["tsm.task.material"].create(
            {"task_id": task.id, "product_id": self.product.id, **values}
        )

    def test_material_defaults_and_unit_conversion_without_onchange(self):
        task = self._create_task()
        material = self._create_material(task)
        self.assertEqual(
            material.name, self.product.get_product_multiline_description_sale()
        )
        self.assertEqual(material.product_uom_id, self.product.uom_id)
        self.assertEqual(material.price_unit, 12.0)
        dozen = self.env.ref("uom.product_uom_dozen")
        material.product_uom_id = dozen
        self.assertEqual(material.price_unit, 144.0)
        material.write({"price_unit": 100.0, "quantity": 2.0, "discount": 10.0})
        self.assertEqual(material.price_subtotal, 180.0)

    def test_invalid_material_values(self):
        task = self._create_task()
        for values in (
            {"quantity": 0.0},
            {"discount": 101.0},
            {"product_uom_id": self.env.ref("uom.product_uom_hour").id},
        ):
            with self.assertRaises(ValidationError), self.env.cr.savepoint():
                self._create_material(task, **values)

    def test_create_sale_preserves_material_and_computes_sale_defaults(self):
        invoice = self.env["res.partner"].create(
            {"name": "Invoice", "parent_id": self.customer.id, "type": "invoice"}
        )
        shipping = self.env["res.partner"].create(
            {"name": "Delivery", "parent_id": self.customer.id, "type": "delivery"}
        )
        tax = self.env["account.tax"].create(
            {"name": "Material Tax", "amount": 10.0, "company_id": self.env.company.id}
        )
        self.product.taxes_id = tax
        task = self._create_task()
        self._create_material(
            task, name="Custom material", quantity=2.0, price_unit=20.0, discount=10.0
        )
        sale = task.create_sale()
        self.assertEqual(task.sale_id, sale)
        self.assertEqual(sale.state, "draft")
        self.assertEqual(sale.partner_invoice_id, invoice)
        self.assertEqual(sale.partner_shipping_id, shipping)
        self.assertEqual(sale.origin, task.code)
        self.assertEqual(sale.order_line.name, "Custom material")
        self.assertEqual(sale.order_line.product_uom, self.product.uom_id)
        self.assertEqual(sale.order_line.tax_id, tax)
        self.assertEqual(sale.amount_untaxed, 36.0)
        self.assertTrue(
            sale.message_ids.filtered(lambda message: task.code in str(message.body))
        )
        self.assertEqual(task.sale_amount, 36.0)
        sale.order_line.price_unit = 30.0
        self.assertEqual(task.sale_amount, 54.0)
        with self.assertRaises(UserError):
            task.create_sale()

    def test_sale_confirmation_and_stage_guard(self):
        task = self._create_task(sale_autoconfirm=True)
        self._create_material(task)
        self.assertEqual(task.create_sale().state, "sale")
        task = self._create_task()
        self._create_material(task)
        task.stage_id = self.env["tsm.task.type"].create({"name": "No sale"})
        with self.assertRaises(UserError):
            task.create_sale()

    def test_create_sale_requires_sales_manager(self):
        task = self._create_task(
            user_id=self.sales_user.id, privacy_visibility="employees"
        )
        self._create_material(task)
        with self.assertRaises(AccessError):
            task.with_user(self.sales_user).create_sale()

    def test_sold_materials_cannot_be_changed_or_deleted(self):
        task = self._create_task()
        material = self._create_material(task)
        task.create_sale()
        for operation in (
            lambda: material.write({"quantity": 2.0}),
            lambda: material.unlink(),
            lambda: self._create_material(task),
            lambda: task.unlink(),
        ):
            with self.assertRaises(UserError), self.env.cr.savepoint():
                operation()
        task.sale_id.unlink()
        material.write({"quantity": 2.0})
        task.unlink()
        self.assertFalse(material.exists())

    def test_materials_follow_task_privacy_and_write_access(self):
        private = self._create_task(privacy_visibility="followers")
        private_material = self._create_material(private)
        public = self._create_task(privacy_visibility="employees")
        public_material = self._create_material(public)
        self.assertFalse(private.with_user(self.user).has_access("read"))
        self.assertFalse(private_material.with_user(self.user).has_access("read"))
        self.assertTrue(public_material.with_user(self.user).has_access("read"))
        self.assertFalse(public_material.with_user(self.user).has_access("write"))
        self.assertNotIn(
            private_material.id,
            self.env["tsm.task.material"].with_user(self.user).search([]).ids,
        )
        assigned = self._create_task(
            user_id=self.user.id, privacy_visibility="employees"
        )
        material = self._create_material(assigned).with_user(self.user)
        material.write({"quantity": 2.0})
        with self.assertRaises(AccessError), self.env.cr.savepoint():
            material.write({"task_id": private.id})

    def test_materials_are_isolated_by_company(self):
        other_company = self.env["res.company"].create(
            {"name": "Other Material Company"}
        )
        task = self._create_task(
            company_id=other_company.id, privacy_visibility="employees"
        )
        material = self._create_material(task)
        self.assertFalse(material.with_user(self.user).has_access("read"))

    def test_order_currency_conversion_preserves_material_value(self):
        currency = self.env["res.currency"].create(
            {"name": "TSM", "symbol": "T", "rounding": 0.01}
        )
        self.env["res.currency.rate"].create(
            {
                "currency_id": currency.id,
                "company_id": self.env.company.id,
                "name": fields.Date.today(),
                "company_rate": 2.0,
            }
        )
        self.customer.property_product_pricelist = self.env["product.pricelist"].create(
            {"name": "Material Foreign Currency", "currency_id": currency.id}
        )
        task = self._create_task()
        material = self._create_material(task)
        sale = task.create_sale()
        self.assertEqual(sale.currency_id, currency)
        self.assertEqual(sale.order_line.price_unit, 24.0)
        self.assertEqual(material.price_unit, 12.0)
        self.assertEqual(task.sale_amount, 12.0)

    def test_materials_preserve_base_archiving_rules(self):
        task = self._create_task(user_id=self.user.id, privacy_visibility="employees")
        self._create_material(task)
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            task.with_user(self.user).action_inactive()
        task.create_sale()
        task.with_user(self.user).action_inactive()
        self.assertFalse(task.active)

    def test_task_and_order_company_must_match(self):
        task = self._create_task()
        self._create_material(task)
        task.create_sale()
        company = self.env["res.company"].create({"name": "Different Sale Company"})
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            task.company_id = company

    def test_project_and_task_reports_render_materials(self):
        project = self.env["tsm.project"].create(
            {"name": "Material Project", "partner_id": self.customer.id}
        )
        task = self._create_task(project_id=project.id)
        self._create_material(task, name="Report material")
        for template, records in (
            ("tsm_base.tsm_task_report_document", task),
            ("tsm_base.tsm_project_report_document", project),
        ):
            html, _ = self.env["ir.actions.report"]._render_qweb_html(
                template, records.ids
            )
            self.assertIn("Report material", str(html))
