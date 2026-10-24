# Copyright 2018 Bilbonet <jesus@bilbonet.net>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "TSM tasks timesheet time control",
    "summary": "Users can encode and track their time spent on the different tasks",
    "category": "Management",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "website": "https://github.com/Bilbonet/bilbonet-tsm",
    "author": "Jesus Ramiro (Bilbonet),",
    "maintainers": ["bilbonet"],
    "license": "AGPL-3",
    "depends": [
        "tsm_base",
    ],
    "assets": {
        "web.assets_backend": [
            "tsm_task_timesheet/static/src/views/task_quick_create.esm.js",
        ],
        "web.assets_unit_tests": [
            "tsm_task_timesheet/static/tests/task_quick_create.test.js",
        ],
    },
    "data": [
        "security/tsm_timesheet_security.xml",
        "security/ir.model.access.csv",
        "data/tsm_task_timesheet_tag_data.xml",
        "views/res_config_settings_views.xml",
        "views/tsm_task_view.xml",
        "views/tsm_task_timesheet_view.xml",
        "views/tsm_task_timesheet_tags_view.xml",
        "views/tsm_task_timesheet_report_view.xml",
        "views/tsm_project_view.xml",
    ],
}
