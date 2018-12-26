# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields


class Project(models.Model):
    _inherit = "tsm.project"

    allow_timesheets = fields.Boolean("Allow timesheets", default=True)
