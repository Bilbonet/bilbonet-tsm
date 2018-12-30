# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TsmTaskType(models.Model):
    _inherit = 'tsm.task.type'

    create_sale_order = fields.Boolean(
        help="If you mark this check, when a task is in this state, "
             "it will be able to create sale order",)

class TsmTask(models.Model):
    _inherit = "tsm.task"

    def _compute_sale(self):
        sale = self.env['sale.order']
        for task in self:
            count = sale.search_count([
                ('tsm_project_id', '=', task.project_id.id),
                ('tsm_task_id', '=', task.id),
            ])
            if not count:
                task.sale_state = 'pending'
            else:
                task.sale_state = 'created'

    material_ids = fields.One2many(comodel_name='tsm.task.material',
                                   inverse_name='task_id',
                                   string='Material used',)
    sale_state = fields.Selection(selection=[
            ('pending', 'Pending'),
            ('created', 'Created'), ],
            compute='_compute_sale',
            help='Created, if there is a sale order created from this task',)
    create_sale_order = fields.Boolean(related='stage_id.create_sale_order',)
    sale_autoconfirm = fields.Boolean(string='Sale autoconfirm',
                    default=True,
                    help='If it is checked the sale order will be created '
                         'and confirmed automatically',)

    @api.multi
    def _prepare_sale(self):
        self.ensure_one()
        if not self.partner_id or not self.material_ids:
            raise ValidationError(_("You must first select a Customer "
                                    "and materials for Task: %s!") % self.name)
        sale = self.env['sale.order'].new({
            'partner_id': self.partner_id,
            'date_order': fields.Date.today(),
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'tsm_project_id': self.project_id.id,
            'tsm_task_id': self.id,
        })

        origin = self.name
        if 'code' in self:
            origin = self.code
        sale.update({'origin': origin})
        # Get other sale values from partner onchange
        sale.onchange_partner_id()

        return sale._convert_to_write(sale._cache)

    @api.multi
    def create_sale(self):
        """
        Create Sale order from task
        :return: Sele Order created
        """
        self.ensure_one()
        sale_vals = self._prepare_sale()
        sale = self.env['sale.order'].create(sale_vals)

        # for line in self.material_ids:
        #     sale_line_vals = self._prepare_sale_line(line, sale.id)
        #     sale_line_id = self.env['sale.order.line'].create(sale_line_vals)

        '''Update Task with the values from the sale order'''
        # vals = {'sale_line_id': sale_line_id}
        # self.update(vals)

        ''' Autoconfirm sale order if it's checked'''
        # if self.sale_autoconfirm:
        #     sale.action_confirm()

        return sale
