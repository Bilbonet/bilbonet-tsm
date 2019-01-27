# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields, _
from datetime import datetime, timedelta

class TsmTaskTimesheet(models.Model):
    _inherit = "tsm.task.timesheet"

    # @api.model
    # def _default_timepack(self):
    #     time_pack_data = self.env['tsm.time.pack'].search(
    #         ['partner_id', '=', self.task_partner_id], limit=1
    #     )
    #     return False
    #
    #     # if time_pack_data:
    #     #     return time_pack_data.id
    #
    #     # return self.env['tsm.time.pack'].search(
    #     #     [], limit=1
    #     # )


    #     if not self.task_id:
    #         return {'domain': {'timepack_id': []}}
    #
    #     time_pack_data = self.env['tsm.time.pack'].search(
    #             ['partner_id', '=', self.task_id.partner_id], limit=1
    #     )
    #     if time_pack_data:
    #         self.timepack_id = time_pack_data.id
    # @api.model
    # def create(self, values):
    #     time_pack_data = self.env['tsm.time.pack'].search(
    #                 ['partner_id', '=', self.task_id.partner_id], limit=1
    #         )

    timepack_id = fields.Many2one('tsm.time.pack', 'Time Packs',
                                  # default=_default_timepack,
                                  index=True,)
    discount_time = fields.Boolean(
        default="True",
        string="Discount Time",
        help="Indicate if discount the time from the time pack")

    # @api.onchange('task_id')
    # def _onchange_task_id(self):
    #     # force domain on task when project is set
    #     return {'domain': {
    #         'timepack_id': [('partner_id', '=', self.task_partner_id)]
    #     }}

    @api.onchange('timepack_id', 'discount_time')
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
