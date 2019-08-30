# Copyright 2019 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_tags_in_task = fields.Boolean(string="Use Tags in Tasks",
                                          default_model='tsm.task')
    group_tsm_task_contact = fields.Boolean("Task Contact",
                implied_group='tsm_base.group_tsm_task_contact')

    # Update field in active tasks
    @api.onchange('default_tags_in_task')
    def _onchange_default_tags_in_task(self):
        self.env['tsm.task'].search([
            ('active', '=', True)
        ]).write({'tags_in_task': self.default_tags_in_task})
