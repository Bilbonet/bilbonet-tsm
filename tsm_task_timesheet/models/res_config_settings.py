# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_tsm_timesheet_title = fields.Boolean(
        string="Timesheet Title",
        implied_group="tsm_task_timesheet.group_tsm_timesheet_title",
    )
    group_tsm_timesheet_tag = fields.Boolean(
        string="Timesheet Tag",
        implied_group="tsm_task_timesheet.group_tsm_timesheet_tag",
    )

    @api.onchange("group_tsm_timesheet_title")
    def onchange_group_tsm_timesheet_title(self):
        if self.group_tsm_timesheet_title:
            self.group_tsm_timesheet_tag = False
            
    @api.onchange("group_tsm_timesheet_tag")
    def onchange_group_tsm_timesheet_tag(self):
        if self.group_tsm_timesheet_tag:
            self.group_tsm_timesheet_title = False
