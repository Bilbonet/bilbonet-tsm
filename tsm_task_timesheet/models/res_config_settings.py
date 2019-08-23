# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_tsm_timesheet_title = fields.Boolean("Timesheet Title",
                implied_group='tsm_task_timesheet.group_tsm_timesheet_title')
    group_tsm_timesheet_tag = fields.Boolean("Timesheet Tag",
                implied_group='tsm_task_timesheet.group_tsm_timesheet_tag')
