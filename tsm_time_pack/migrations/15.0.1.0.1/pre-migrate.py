from openupgradelib import openupgrade

from odoo.tools import parse_version

_field_renames = [
    ("tsm.time.pack", "tsm_time_pack", "contrated_hours", "contracted_hours"),
]


@openupgrade.migrate()
def migrate(env, version):
    if parse_version(version) == parse_version("15.0.1.0.0"):
        openupgrade.rename_fields(env, _field_renames)
