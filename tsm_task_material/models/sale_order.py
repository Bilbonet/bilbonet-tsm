# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    tsm_task_id = fields.Many2one(comodel_name='tsm.task',
                            string='TSM Task related',
                            help="Task related that generated this order")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tsm_task_id = fields.Many2one(comodel_name='tsm.task',
                string='Task related that generated this order line')
    tsm_task_material_id = fields.Many2one(comodel_name='tsm.task.material',
                string='Task Material related that generated this order line')
