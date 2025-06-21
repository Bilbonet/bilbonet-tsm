# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class TsmTask(models.Model):
    _inherit = "tsm.task"

    asset_ids = fields.Many2many(
        comodel_name="tsm.tech.asset",
        relation="tsm_task_tsm_tech_asset_rel",
        column1="tsm_task_id",
        column2="tsm_tech_asset_id",
        string="Tech Assets",
        context={"active_test": False},
    )
