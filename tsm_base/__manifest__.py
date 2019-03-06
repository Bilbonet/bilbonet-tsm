# Copyright 2018 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Technical Support Management',
    'version': '11.0.1.0.0',
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
        'data/tsm_paper_format_report.xml',
        'data/tsm_task_email_template.xml',
        'report/tsm_layout_template.xml',
        'report/tsm_task_report.xml',
        'views/tsm_project_views.xml',
        'views/tsm_task_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
