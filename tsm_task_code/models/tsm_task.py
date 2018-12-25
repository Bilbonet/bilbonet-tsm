# Copyright 2018 Bilbonet <jesus@bilbonet.net>
#  Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class TsmTask(models.Model):
    _inherit = 'tsm.task'

    code = fields.Char(
        string='Task Number', required=True, default="/", readonly=True)

    _sql_constraints = [
        ('tsm_task_unique_code', 'UNIQUE (code)',
         _('The code must be unique!')),
    ]

    @api.model
    def create(self, vals):
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('tsm.task')
        return super(TsmTask, self).create(vals)

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code('tsm.task')
        return super(TsmTask, self).copy(default)

    @api.multi
    def name_get(self):
        result = super(TsmTask, self).name_get()
        new_result = []

        for task in result:
            rec = self.browse(task[0])
            name = '[%s] %s' % (rec.code, task[1])
            new_result.append((rec.id, name))
        return new_result
