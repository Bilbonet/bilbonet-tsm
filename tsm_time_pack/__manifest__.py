# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "TSM Task Time Service Pack",
    "summary": "Create packs of time which can be consumed in tasks.",
    "version": "15.0.1.0.0",
    "category": "Management",
    "author": "Jesus Ramiro,",
    "license": "AGPL-3",
    "depends": [
        "product",
        "tsm_task_timesheet",
        "sale",
        'web_notify',
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/tsm_time_pack_security.xml",
        "data/tsm_time_pack_sequence.xml",
        "views/tsm_task_view.xml",
        "views/tsm_task_timesheet_view.xml",
        'views/product_view.xml',
        "views/tsm_time_pack_view.xml",
        "report/tsm_time_pack_task_report.xml",
        "report/tsm_time_pack_report.xml",
        "report/tsm_time_pack_project_report.xml",
        "data/tsm_time_pack_email_template.xml",
    ],
    "application": False,
    "installable": True,
}
