# Copyright 2025 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FollowerAssignmentWizard(models.TransientModel):
    _name = "follower.assignment.wizard"
    _description = "Assign and Unassign Followers to Record"

    record_followers_ids = fields.Many2many(
        string="Followers",
        comodel_name="res.partner",
        relation="record_followers_assignment_rel",
        column1="record_id",
        column2="partner_id",
    )

    _allowed_models = {"res.partner", "tsm.project", "tsm.task"}

    def _selected_records(self):
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids")
        if active_model not in self._allowed_models or not active_ids:
            return False
        return (
            self.env[active_model]
            .with_context(active_test=False)
            .browse(active_ids)
            .exists()
        )

    def assign_followers(self):
        records = self._selected_records()
        if records:
            records.message_subscribe(partner_ids=self.record_followers_ids.ids)
        return True

    def update_followers(self):
        records = self._selected_records()
        if records:
            records.message_unsubscribe(partner_ids=self.record_followers_ids.ids)
        return True
