# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, exceptions, fields, models, _
from datetime import datetime, timedelta


class TsmTaskTimesheeetTags(models.Model):
    """ Tags of timesheets """
    _name = "tsm.task.timesheet.tags"
    _description = "Tags in timesheet"
    _order = "sequence, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide"
        " the tag without removing it.")
    default = fields.Boolean('Default', default=False,
        help="Selected by default when create timesheet.")
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of tags.")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]

    @api.constrains('default')
    def _check_default(self):
        if self.default:
            checked_bool = self.search([
                                ('id', '!=', self.id),('default', '=', True)])
            if checked_bool:
                raise ValidationError(
                    _("There's already one Tag checked as defautl.\n "
                      "Tag Checked : %s") % checked_bool[0].name)
