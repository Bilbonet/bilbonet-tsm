# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Client Technical Assets Management',
    'version': '11.0.1.0.0',
    'category': 'Management',
    'license': 'AGPL-3',
    'author': 'Jesus Ramiro (Bilbonet.NET)',
    'website': 'https://www.bilbonet.net',
    'depends': [
        'tsm_base',
    ],
    'data': [
        'data/tsm_tech_asset_sequence.xml',
        'security/ir.model.access.csv',
        'views/tsm_tech_asset_views.xml',
        'views/tsm_task_view.xml',
        'report/tsm_tech_asset_report.xml',
    ],
    'installable': True,
}
