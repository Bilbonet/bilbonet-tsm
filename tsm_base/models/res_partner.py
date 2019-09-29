# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    """ Inherits partner and adds Tasks information in the partner form """
    _inherit = 'res.partner'

    tsm_task_ids = fields.One2many('tsm.task', 'partner_id',
                                   string='Partner related tasks')
    tsm_task_count = fields.Integer(
        compute='_compute_task_count', string='Amount Partner Tasks')

    def _compute_task_count(self):
        fetch_data = self.env['tsm.task'].read_group(
            [('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id']
        )
        result = dict(
                    (data['partner_id'][0], data['partner_id_count'])
                    for data in fetch_data
        )
        for partner in self:
            partner.tsm_task_count = result.get(partner.id, 0)
