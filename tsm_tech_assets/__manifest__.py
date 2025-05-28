# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Client Technical Assets Management",
    "summary": "Helps your team control the different technical equipments of your clients",
    "category": "Management",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "website": "https://github.com/Bilbonet/bilbonet-tsm",
    "author": "Jesus Ramiro (Bilbonet),",
    "maintainers": ["bilbonet"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "tsm_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/tsm_tech_asset_security.xml",
        "data/tsm_tech_asset_sequence.xml",
        "views/tsm_tech_asset_views.xml",
        "views/tsm_task_view.xml",
        "report/tsm_tech_asset_report.xml",
        "data/tsm_tech_asset_email_template.xml",
    ],
}
