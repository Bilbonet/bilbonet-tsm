# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, _


class TsmTaskType(models.Model):
    _name = 'tsm.task.type'
    _description = 'Task Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    legend_priority = fields.Char(
        string='Starred Explanation', translate=True,
        help='Explanation text to help users using the '
             'star on tasks in this stage.')
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'),
        translate=True, required=True,
        help='Override the default value displayed for the blocked state for '
             'kanban selection, when the task is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready for Next Stage'),
        translate=True, required=True,
        help='Override the default value displayed for the done state for '
             'kanban selection, when the task is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'),
        translate=True, required=True,
        help='Override the default value displayed for the normal state for '
             'kanban selection, when the task is in that stage.')
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no '
             'records in that stage to display.')
    closed = fields.Boolean(
        help="Tasks in this stage are considered closed. "
             "You can only archive a task in a stage with state closed.",
        default=False,
    )
