# Copyright 2012 - 2013 Daniel Reis
# Copyright 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2016 - Tecnativa - Vicent Cubells
# Copyright 2017 - Tecnativa - David Vidal
# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
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
        "views/tsm_task_view.xml",
        "security/ir.model.access.csv",
    ],
}