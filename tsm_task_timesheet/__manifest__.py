# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'TSM tasks timesheet time control',
    'version': '12.0.1.0.0',
    'category': 'Management',
    'author': 'bilbonet.NET,',
    'website': 'https://github.com/Bilbonet/bilbonet-tsm/',
    'depends': [
        'tsm_base',
    ],
    'data': [
        'security/tsm_timesheet_security.xml',
        'security/ir.model.access.csv',
        'data/tsm_task_timesheet_tag_data.xml',
        'views/res_config_settings_views.xml',
        'views/tsm_task_view.xml',
        'views/tsm_task_timesheet_view.xml',
        'views/tsm_task_timesheet_report_view.xml',
        'views/tsm_project_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
}
