# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tsm_project_id = fields.Many2one(comodel_name='tsm.project',
                            string='Project related that generated this order')
    tsm_task_id = fields.Many2one(comodel_name='tsm.task',
                            string='Task related that generated this order')
