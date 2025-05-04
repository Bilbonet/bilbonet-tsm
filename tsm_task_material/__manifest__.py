# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "TSM Task Material",
    "summary": "Record products spent in a Task and create Sale Order",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "category": "Management",
    "website": "https://github.com/Bilbonet/bilbonet-tsm/tsm_task_material",
    "author": "Jesus Ramiro,",
    "maintainers": ["biblonet"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
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
}
