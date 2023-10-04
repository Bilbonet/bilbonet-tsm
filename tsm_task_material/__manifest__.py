# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "TSM Task Material",
    "summary": "Record products spent in a Task and create Sale Order",
    "version": "15.0.1.0.0",
    "category": "Management",
    "author": "Jesus Ramiro,",
    "license": "AGPL-3",
    "depends": [
        "tsm_base",
        "sale",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tsm_task_view.xml",
        "report/tsm_task_material_report.xml",
        "report/tsm_material_project_report.xml",
    ],
    "application": False,
    "installable": True,
}
