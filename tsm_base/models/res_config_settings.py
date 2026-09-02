# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_tags_in_task = fields.Boolean(
        string="Use Tags in Tasks", default_model="tsm.task"
    )
    group_tsm_task_contact = fields.Boolean(
        "Task Contact", implied_group="tsm_base.group_tsm_task_contact"
    )

    def set_values(self):
        result = super().set_values()
        self.env["tsm.task"].search(
            [
                ("active", "=", True),
                ("company_id", "in", self.env.companies.ids),
            ]
        ).write({"tags_in_task": self.default_tags_in_task})
        return result
