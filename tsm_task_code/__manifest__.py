# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sequential Code for TSM Tasks",
    "version": "11.0.1.0.0",
    "category": "Management",
    "author": "bilbonet.NET",
    "website": "http://www.bilbonet.net",
    "license": "AGPL-3",
    "contributors": [
        "Jesus Ramiro <jesus@bilbonet.net>",
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristo@gmail.com>",
        "Vicent Cubells <vicent.cubells@tecnativa.com>",
    ],
    "depends": [
        "tsm_base",
    ],
    "data": [
        "views/tsm_view.xml",
    ],
    'installable': True,
    "pre_init_hook": "create_code_equal_to_id",
    "post_init_hook": "assign_old_sequences",
}
