# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class TsmTaskType(models.Model):
    _name = "tsm.task.type"
    _description = "Task Stage"
    _order = "sequence, id"

    name = fields.Char(string="Stage Name", required=True, translate=True)
    sequence = fields.Integer(default=1)
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage is folded in the kanban view when there are no "
        "records in that stage to display.",
    )
    closed = fields.Boolean(
        help="Tasks in this stage are considered closed. "
        "You can only archive a task in a stage with state closed.",
        default=False,
    )
