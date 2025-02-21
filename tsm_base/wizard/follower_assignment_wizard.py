# Copyright 2025 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models


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

    def assign_followers(self):
        context = self._context
        if context is None:
            context = {}
        if context.get("active_model"):
            # Current model name
            model_obj = self.env[context["active_model"]]
            model_follower_obj = self.env["mail.followers"]
            followers_ids = self.record_followers_ids.ids
            if context.get("active_ids"):
                # get values from current active_ids
                for value in model_obj.search([("id", "in", context["active_ids"])]):
                    existing_followers_id = followers_to_assign = []
                    existing_followers_id = [
                        val.partner_id.id for val in value.message_follower_ids
                    ]
                    # check existing message followers and assigned followers
                    followers_to_assign = list(
                        set(followers_ids) - set(existing_followers_id)
                    )
                    for val_loop in followers_to_assign:
                        model_follower_obj.create(
                            {
                                "partner_id": val_loop,
                                "res_model": context["active_model"],
                                "res_id": value.id,
                            }
                        )
        return True

    def update_followers(self):
        context = self._context
        if context is None:
            context = {}
        if context.get("active_model"):
            model_obj = self.env[context["active_model"]]
            model_follower_obj = self.env["mail.followers"]
            active_model_id = model_obj.search(
                [("id", "in", self._context.get("active_ids"))]
            )
            followers_ids = [val.id for val in self.record_followers_ids]
            for line in active_model_id:
                # check existing message followers and record_followers_ids
                followers_to_unassign = list(set(followers_ids))
                for val_loop in followers_to_unassign:
                    model_follower_obj.search(
                        [
                            ("partner_id", "=", val_loop),
                            ("res_model", "=", self._context.get("active_model")),
                            ("res_id", "=", line.id),
                        ]
                    ).unlink()

        return True
