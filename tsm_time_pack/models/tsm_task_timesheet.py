# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, models, fields, _


class TsmTaskTimesheet(models.Model):
    _inherit = "tsm.task.timesheet"

    timepack_id = fields.Many2one(
        comodel_name='tsm.time.pack',
        string='Time Packs', index=True)
    discount_time = fields.Boolean(
        string="Discount Time", default="True",
        help="Indicate if discount the time from the time pack")

    @api.model_create_multi
    def create(self, vals_list):
        '''If we don't indicate Time Pack in the new Timesheet. 
           We search any Time Pack available for the partner'''
        for vals in vals_list:
            if not vals['timepack_id']:
                task = self.env['tsm.task'].browse(vals['task_id'])
                tp = self.env['tsm.time.pack'].search([
                    ('partner_id', '=', task.partner_id.id),
                    ('active', '=', True),
                ], limit=1)

                if tp:
                    vals.update({
                        'timepack_id': tp.id
                    })

        return super(TsmTaskTimesheet, self).create(vals_list)

    # @api.onchange('amount', 'timepack_id', 'discount_time')
    # def _onchange_timepack(self):
    #     self.timepack_id._hours_get()
    #     if self.timepack_id.progress > 90:
    #         contrated_hours = '{0:02.0f}:{1:02.0f}'.format(
    #             *divmod(float(self.timepack_id.contrated_hours) * 60, 60)
    #         )
    #         consumed_hours = '{0:02.0f}:{1:02.0f}'.format(
    #             *divmod(float(self.timepack_id.consumed_hours) * 60, 60)
    #         )

    #         message = _(
    #             'Hours Contrated: %s'
    #             '\nHours Consumed:  %s'
    #             '\nProgress: %s %%') \
    #             % (contrated_hours, consumed_hours, self.timepack_id.progress)
    #         warning_mess = {
    #             'title': _("Alert Time Pack: %s") % self.timepack_id.code,
    #             'message': message
    #         }
    #         return {'warning': warning_mess}
    #     return {}

    def view_time_pack(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tsm.time.pack',
            'res_id': self.timepack_id.id,
            'view_type': 'form',
            'view_mode': 'form,tree',
        }
