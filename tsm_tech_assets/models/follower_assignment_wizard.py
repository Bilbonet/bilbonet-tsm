# Copyright 2026 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models

from odoo.addons.tsm_base.wizard.follower_assignment_wizard import (
    FollowerAssignmentWizard as BaseFollowerAssignmentWizard,
)


class FollowerAssignmentWizard(models.TransientModel):
    _inherit = "follower.assignment.wizard"

    _allowed_models = BaseFollowerAssignmentWizard._allowed_models | {"tsm.tech.asset"}
