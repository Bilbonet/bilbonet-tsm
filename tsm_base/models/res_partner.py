# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    """ Inherits partner and adds Tasks information in the partner form """
    _inherit = 'res.partner'

    tsm_task_ids = fields.One2many('tsm.task', 'partner_id',
        string='Partner related tasks')
    tsm_task_count = fields.Integer(string='Amount Partner Tasks',
        compute='_compute_task_count')

    def _compute_task_count(self):
        fetch_data = self.env['tsm.task'].with_context(active_test=False).read_group(
            domain=[('partner_id', 'in', self.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        result = dict(
                    (data['partner_id'][0], data['partner_id_count'])
                    for data in fetch_data
        )
        for partner in self:
            partner.tsm_task_count = result.get(partner.id, 0)
