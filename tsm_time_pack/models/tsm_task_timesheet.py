# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields, _
from datetime import datetime, timedelta


class TsmTaskTimesheet(models.Model):
    _inherit = "tsm.task.timesheet"

    timepack_id = fields.Many2one('tsm.time.pack', 'Time Packs', index=True)
    discount_time = fields.Boolean(
        default="True",
        string="Discount Time",
        help="Indicate if discount the time from the time pack")

    @api.model
    def create(self, values):
        # We search Time Pack available for the partner
        task = self.env['tsm.task'].browse(values['task_id'])
        time_pack_id = self.env['tsm.time.pack'].search([
            ('partner_id', '=', task.partner_id.id)], limit=1)

        if time_pack_id and not values['timepack_id']:
            values['timepack_id'] = time_pack_id.id

        return super(TsmTaskTimesheet, self).create(values)

    @api.onchange('amount', 'timepack_id', 'discount_time')
    def _onchange_timepack(self):
        self.timepack_id._hours_get()
        if self.timepack_id.progress > 90:
            contrated_hours = (datetime(2000,1,1)+timedelta(
                seconds=self.timepack_id.contrated_hours*3600)
                ).strftime('%H:%M')
            consumed_hours = (datetime(2000,1,1)+timedelta(
                seconds=self.timepack_id.consumed_hours*3600)
                ).strftime('%H:%M')

            message = _(
                'Hours Contrated: %s'
                '\nHours Consumed:  %s'
                '\nProgress: %s %%') \
                % (contrated_hours, consumed_hours, self.timepack_id.progress)
            warning_mess = {
                'title': _("Alert Time Pack %s") % self.timepack_id.code,
                'message': message
            }
            return {'warning': warning_mess}
        return {}
