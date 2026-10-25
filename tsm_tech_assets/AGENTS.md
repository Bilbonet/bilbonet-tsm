# AGENTS.md

## Scope and integration

`tsm_tech_assets` is an Odoo 18 addon in `bilbonet-tsm`, depending directly on
`tsm_base`. It registers customer equipment and configuration notes, links assets to TSM
tasks, and provides email templates and summary/detailed PDF reports. It does not manage
stock, accounting assets or Odoo Project tasks.

## Stable contracts

- Preserve `tsm.tech.asset`, `tsm.tech.asset.type`, XML IDs and the
  `tsm_task_tsm_tech_asset_rel` table with its `tsm_task_id` and `tsm_tech_asset_id`
  columns. The reciprocal Many2many fields exclude their links when copying either a
  task or an asset.
- Codes are required, globally unique and assigned from the `tsm.tech.asset` sequence
  when `/` is supplied. Preserve the sequence's `noupdate` data.
- Task counts include archived tasks and respect the current user's task access. Do not
  elevate reads or count all related tasks without considering disclosure.
- `can_edit` controls form fields for managers or the asset's responsible user. It is a
  UI helper, not a server-side field authorization mechanism.
- Asset ACLs allow TSM users CRUD. Asset types are readable by TSM users and managed by
  TSM managers. Managers have an unrestricted asset rule; ordinary users' rules combine
  public/followed assets for reading/writing and assigned assets for
  creating/writing/deleting. Group rules combine with OR per operation. Do not silently
  change this policy or the rules' `noupdate` status.
- `company_id` defaults to the active company. There is no asset record rule enforcing
  company isolation. Notes may contain sensitive configuration data; review privacy,
  followers and report/email recipients before changing access.

## Sensitive integration points

- Asset types are maintained by name directly in an editable configuration list.
- The task form inherits `tsm_base.tsm_task_form_view` after `date_deadline`. The
  customer hierarchy domain filters selectable assets; it is not a server constraint on
  task/asset customer consistency.
- Task asset cards stay compact and display only the name. Clicking the card opens the
  native dialog; the diagonal triangle uses `open_child_form` for full-page navigation;
  the red cross only unlinks the Many2many relation. Keep the controls separated without
  absolute positioning and preserve `role="button"` on the styled unlink anchor. The
  full-form button must remain in the native view-button pipeline so the task is saved
  before navigating.
- Reports reuse `tsm_base.tsm_report_layout` and its paper format. The detailed report
  reads related tasks under the current user's permissions; visibility of an asset does
  not establish permission to read every related task.
- The mail composer uses `default_res_ids`. Attached reports are configured by
  `mail.template.report_template_ids`; their names come from the report action.
- The follower assignment action reuses `tsm_base`'s generic wizard. This addon extends
  its model allowlist with `tsm.tech.asset`, preserving the base entries. Coordinate
  changes to this integration with the base module.

## Specifications and validation

Read [specs/README.md](specs/README.md),
[specs/module-contract.md](specs/module-contract.md) and only the specification relevant
to the task. Use the shared `odoo-sdd` skill for method maintenance. SDD documents are
in Spanish; addon code, UI source strings and documentation are in English. Keep stable
context here and functional agreements in `specs/`.

The [migration review](specs/migration-review.md) distinguishes source checks from
runtime and persisted-data validation. Regression tests live in `tests/`; do not import
them from the addon root. Focus verification on batch creation, copying, task counts
including archives and restricted tasks, editability with multiple owners,
privacy/followers, company context, Kanban actions, email composition/attachments and
both reports. Tests and database operations require the authorization defined by the
inherited workspace policy.
