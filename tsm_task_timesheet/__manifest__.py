# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'TSM tasks timesheet time control',
    'version': '11.0.1.0.0',
    'category': 'Management',
    'author': 'bilbonet.NET,',
    'website': 'https://github.com/Bilbonet/bilbonet-tsm/',
    'depends': [
        'tsm_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/tsm_task_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
