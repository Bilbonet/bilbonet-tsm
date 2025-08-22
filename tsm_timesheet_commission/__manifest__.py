# Copyright 2024 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "TSM Timesheet Commissions",
    "summary": "Links TSM Task Timesheet with commissions",
    "category": "Commissions",
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
        "tsm_time_pack",
        "account_commission",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/tsm_task_view.xml",
        "views/tsm_task_timesheet_view.xml",
        "views/commission_views.xml",
        "views/commission_settlement_views.xml",
    ],
}
