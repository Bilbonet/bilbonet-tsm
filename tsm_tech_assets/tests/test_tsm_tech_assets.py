# Copyright 2026 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import patch

from odoo import Command
from odoo.tests.common import TransactionCase, new_test_user


class TestTsmTechAssets(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Asset Customer"})
        cls.asset_type = cls.env["tsm.tech.asset.type"].create({"name": "Hardware"})
        cls.asset_user = new_test_user(
            cls.env,
            login="tsm_asset_user",
            groups="tsm_base.group_tsm_user",
            context={"no_reset_password": True},
            company_id=cls.env.company.id,
            company_ids=[Command.set(cls.env.company.ids)],
        )
        cls.manager = new_test_user(
            cls.env,
            login="tsm_asset_manager",
            groups="tsm_base.group_tsm_manager",
            context={"no_reset_password": True},
            company_id=cls.env.company.id,
            company_ids=[Command.set(cls.env.company.ids)],
        )

    def _asset_values(self, name="Customer Asset", **values):
        return {
            "name": name,
            "partner_id": self.partner.id,
            "type_id": self.asset_type.id,
            "privacy_visibility": "employees",
            **values,
        }

    def test_batch_create_assigns_distinct_codes(self):
        assets = self.env["tsm.tech.asset"].create(
            [self._asset_values("First Asset"), self._asset_values("Second Asset")]
        )
        self.assertEqual(len(set(assets.mapped("code"))), 2)
        self.assertNotIn("/", assets.mapped("code"))
        self.assertEqual(assets.company_id, self.env.company)

    def test_company_defaults_to_current_company(self):
        company = self.env["res.company"].create({"name": "Asset Company"})
        asset = (
            self.env["tsm.tech.asset"]
            .with_company(company)
            .create(self._asset_values(code="OTHER-COMPANY-ASSET"))
        )
        self.assertEqual(asset.company_id, company)

    def test_editability_for_multiple_owners_and_users(self):
        assets = self.env["tsm.tech.asset"].create(
            [
                self._asset_values("Own Asset", user_id=self.asset_user.id),
                self._asset_values("Other Asset", user_id=self.manager.id),
            ]
        )
        ordinary_assets = assets.with_user(self.asset_user)
        self.assertEqual(ordinary_assets.mapped("can_edit"), [True, False])
        self.assertEqual(
            assets.with_user(self.manager).mapped("can_edit"), [True, True]
        )
        assets[1].user_id = self.asset_user
        self.assertTrue(ordinary_assets[1].can_edit)

    def test_count_includes_archived_tasks_and_updates_links(self):
        asset = self.env["tsm.tech.asset"].create(self._asset_values())
        self.assertEqual(asset.task_count, 0)
        closed_stage = self.env["tsm.task.type"].create(
            {"name": "Closed", "closed": True}
        )
        tasks = self.env["tsm.task"].create(
            [
                {
                    "name": "Active Asset Task",
                    "partner_id": self.partner.id,
                    "asset_ids": [Command.link(asset.id)],
                },
                {
                    "name": "Archived Asset Task",
                    "partner_id": self.partner.id,
                    "stage_id": closed_stage.id,
                    "active": False,
                    "asset_ids": [Command.link(asset.id)],
                },
            ]
        )
        self.assertEqual(asset.task_count, 2)
        self.assertEqual(set(asset.task_ids.ids), set(tasks.ids))
        tasks[0].asset_ids = [Command.clear()]
        self.assertEqual(asset.task_count, 1)

    def test_copy_does_not_copy_task_asset_links(self):
        asset = self.env["tsm.tech.asset"].create(self._asset_values())
        task = self.env["tsm.task"].create(
            {
                "name": "Asset Task",
                "partner_id": self.partner.id,
                "asset_ids": [Command.link(asset.id)],
            }
        )
        copied_asset = asset.copy()
        self.assertNotEqual(copied_asset.code, asset.code)
        self.assertEqual(copied_asset.name, f"{asset.name} (copy)")
        self.assertFalse(copied_asset.task_ids)
        self.assertFalse(task.copy().asset_ids)
        self.assertEqual(task.asset_ids, asset)

    def test_count_respects_task_access_when_switching_users(self):
        asset = self.env["tsm.tech.asset"].create(self._asset_values())
        self.env["tsm.task"].create(
            {
                "name": "Public Asset Task",
                "partner_id": self.partner.id,
                "privacy_visibility": "employees",
                "asset_ids": [Command.link(asset.id)],
            }
        )
        private_task = self.env["tsm.task"].create(
            {
                "name": "Private Asset Task",
                "partner_id": self.partner.id,
                "user_id": self.manager.id,
                "privacy_visibility": "followers",
                "asset_ids": [Command.link(asset.id)],
            }
        )
        private_task.message_unsubscribe(partner_ids=self.asset_user.partner_id.ids)
        self.assertEqual(asset.with_user(self.manager).task_count, 2)
        self.assertEqual(asset.with_user(self.asset_user).task_count, 1)
        self.assertEqual(asset.with_user(self.manager).task_count, 2)

    def test_email_action_initializes_composer(self):
        asset = self.env["tsm.tech.asset"].create(self._asset_values())
        action = asset.action_tech_asset_send()
        composer = (
            self.env["mail.compose.message"]
            .with_context(**action["context"])
            .create({})
        )
        self.assertEqual(composer.model, asset._name)
        self.assertEqual(composer.res_ids, repr(asset.ids))
        self.assertEqual(
            composer.template_id,
            self.env.ref("tsm_tech_assets.tsm_tech_asset_email_template"),
        )

    def test_follower_wizard_assigns_and_removes_asset_followers(self):
        asset = self.env["tsm.tech.asset"].create(self._asset_values())
        follower = self.asset_user.partner_id
        asset.message_unsubscribe(partner_ids=follower.ids)
        wizard = (
            self.env["follower.assignment.wizard"]
            .with_context(active_model=asset._name, active_ids=asset.ids)
            .create({"record_followers_ids": [Command.set(follower.ids)]})
        )
        wizard.assign_followers()
        self.assertIn(follower, asset.message_partner_ids)
        wizard.update_followers()
        self.assertNotIn(follower, asset.message_partner_ids)

    def test_follower_wizard_keeps_base_models_and_rejects_other_models(self):
        wizard_model = self.env["follower.assignment.wizard"]
        self.assertTrue(
            {"res.partner", "tsm.project", "tsm.task"} <= wizard_model._allowed_models
        )
        wizard = wizard_model.with_context(
            active_model="res.users", active_ids=self.asset_user.ids
        ).create({"record_followers_ids": [Command.set(self.partner.ids)]})
        self.assertFalse(wizard._selected_records())

    def test_email_template_generates_named_report_attachment(self):
        asset = self.env["tsm.tech.asset"].create(self._asset_values())
        template = self.env.ref(
            "tsm_tech_assets.tsm_tech_asset_email_template_report_attached"
        )
        report = self.env.ref("tsm_tech_assets.tsm_tech_asset_report_action")
        self.assertEqual(template.report_template_ids, report)
        with patch.object(
            type(self.env["ir.actions.report"]),
            "_render_qweb_pdf",
            return_value=(b"PDF placeholder", "pdf"),
        ):
            values = template._generate_template_attachments(
                asset.ids, ["report_template_ids"]
            )
        attachments = values[asset.id]["attachments"]
        self.assertEqual(len(attachments), 1)
        self.assertEqual(
            attachments[0][0],
            f"({asset.code})_{asset.name.replace(' ', '-')}.pdf",
        )
