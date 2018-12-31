# Copyright 2018 - Bilbonet <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "TSM Task Material",
    "summary": "Record products spent in a Task",
    "version": "11.0.1.0.0",
    "category": "Management",
    "author": "Jesus Ramiro,",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "tsm_base",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tsm_task_view.xml",
        "views/sale_order_view.xml",
    ],
}
