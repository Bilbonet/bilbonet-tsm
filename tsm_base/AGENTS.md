# tsm_base

## Purpose and boundaries

Technical support projects and tasks with stages, tags, followers, activities, email
composition and PDF reports. Owns `tsm.project`, `tsm.task`, `tsm.task.type` and
`tsm.task.tags`; it is separate from Odoo Project.

## Dependencies and integrations

Direct dependencies are `base_setup`, `product`, `mail` and `web`. The module extends
`res.partner` and `res.config.settings`, and uses mail threads, activities, templates
and QWeb reports. Odoo 15 sibling modules `tsm_task_material`, `tsm_task_timesheet` and
`tsm_tech_assets` extend these models and need coordinated review when migrated.

## Working guidance

Read `specs/module-contract.md` and the relevant change specification before
implementation. Keep requirements in specs and generated documentation in its source
fragments; do not edit generated `README.rst` directly. Preserve task codes, sequence
continuity, business records, archived records, messages, attachments, activities and
followers. Verify privacy, company boundaries and follower actions with
non-administrator users.

## Validation focus

Cover counts, stage expansion, batch create/copy, archive/delete safeguards, settings
save/discard, permissions, follower subscriptions, email composition and Spanish PDF
output. Test fresh installation separately from production-data migration. Follow
inherited validation policy before executing checks.
