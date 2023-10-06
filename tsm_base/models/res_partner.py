# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    """ Inherits partner and adds Tasks information in the partner form """
    _inherit = 'res.partner'

    tsm_task_ids = fields.One2many(string='TSM tasks',
        comodel_name='tsm.task', 
        inverse_name='partner_id',
       )
    tsm_task_count = fields.Integer(
        string='Amount Partner Tasks',
        compute='_compute_tsm_task_count',
        readonly=True,
    )

    def _compute_tsm_task_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        tsm_task_groups = self.with_context(
            active_test=False
        ).env['tsm.task'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )

        partners = self.browse()
        for group in tsm_task_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.tsm_task_count += group['partner_id_count']
                    partners |= partner
                partner = partner.parent_id
        (self - partners).tsm_task_count = 0
