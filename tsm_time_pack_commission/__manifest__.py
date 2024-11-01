# Copyright 2024 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "TSM Time Pack Commissions",
    "summary": "Links TSM Time Pack with commissions.",
    "version": "15.0.1.0.0",
    "author": "Jesus Ramiro,",
    "category": "Commissions",
    "license": "AGPL-3",
    "depends": [
        "tsm_time_pack",
        "commission",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tsm_task_view.xml",
    ],
    "application": False,
    "installable": True,
}
