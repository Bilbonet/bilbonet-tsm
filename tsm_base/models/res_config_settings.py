# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tsm_tags_in_task = fields.Boolean(string="Use Tags in Tasks")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            tsm_tags_in_task=self.env['ir.config_parameter'].sudo().get_param(
                'tsm_base.tsm_tags_in_task')
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'tsm_base.tsm_tags_in_task', self.tsm_tags_in_task)
