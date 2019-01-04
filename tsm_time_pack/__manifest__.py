# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "TSM Task Time Service Pack",
    "summary": "Create packs of time which can be consumed in tasks.",
    "version": "11.0.1.0.0",
    "category": "Management",
    "author": "Jesus Ramiro,",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "tsm_base",
        "tsm_task_timesheet",
        "product",
    ],
    "data": [
        "data/tsm_time_pack_sequence.xml",
        "security/ir.model.access.csv",
        "views/tsm_time_pack_view.xml",
        "views/tsm_task_view.xml",
        "views/tsm_task_timesheet_view.xml",
        "report/tsm_time_pack_report.xml",
    ],
}
