# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Technical Support Management',
    'version': '15.0.1.0.0',
    'category': 'Management',
    'license': 'AGPL-3',
    'author': 'Jesus Ramiro (Bilbonet.NET)',
    'website': 'https://www.bilbonet.net',
    'depends': [
        'base_setup',
        'product',
        'mail',
        'web',
    ],
    'data': [
        'security/tsm_security.xml',
        'security/ir.model.access.csv',
        'data/tsm_task_sequence.xml',
        'data/tsm_base_data.xml',
        'report/tsm_layout_template.xml',
        'report/tsm_task_report.xml',
        'report/tsm_project_report.xml',
        'data/tsm_task_email_template.xml',
        'data/tsm_project_email_template.xml',
        'views/tsm_task_views.xml',
        'views/tsm_project_views.xml',
        'views/tsm_task_type_views.xml',
        'views/tsm_task_tags_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
