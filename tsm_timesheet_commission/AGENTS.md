# tsm_timesheet_commission

Odoo 18 addon in `bilbonet-tsm`, bridging TSM timesheets and OCA commissions. It uses
`tsm.task.timesheet`, not HR Timesheets or analytic lines.

## Behavior and boundaries

- Direct dependencies: `tsm_time_pack` and `account_commission_oca`. OCA addon XML IDs
  use `commission_oca`; the model names remain `commission`, `commission.mixin`,
  `commission.line.mixin` and `commission.settlement`.
- Customer agents are copied to time entries using each agent's `tsm_commission_id`.
  Automatic selection accepts an unspecified settlement type or `timesheet`.
  Regenerating agents replaces existing assignments and is blocked by settled lines.
- Hidden `agent_ids` fields inside lists need an inline subview carrying agent,
  commission and editable price values. The list x2many widget does not load its
  standalone subview; omitting these fields drops unsaved agent values from onchange
  responses and produces empty create commands.
- Agent commissions use decimal hours and the OCA gross/net and fixed/section
  calculator. Automatic hourly price comes from the pack when consuming hours, zero for
  complimentary pack hours, or the commission's product without a pack. A nonzero
  specific price overrides this; zero retains its automatic meaning. Do not introduce
  automatic historical repricing when changing configuration.
- Settlement uses the OCA wizard, period, company and currency grouping. Closed-task
  commissions wait for a closed stage; lines without a task are skipped. Cancelling a
  settlement releases its agent lines. Preserve invoice/manual settlement computes when
  extending the shared model: delegate other sources through `super()`.
- TSM settlement lines use native list editing and deletion while the sheet is
  `settled`; other states are readonly in the view. Preserve standard OCA ACLs and the
  header's existing editability. Saving a deleted settlement row releases its source
  commission if no other active settlement remains. Re-settlement uses the source date;
  it does not defer the commission to the following month.
- `timesheet.settlement_id` is the existing link to a settlement generating a time
  entry. It is not the inverse of agent settlement lines; do not populate it from the
  settlement wizard or redefine task settlement counters without reviewing scope.
- Preserve model/field names, XML IDs and stored relations. Renaming the OCA
  dependencies does not migrate an existing database or its external IDs.

## Permissions and sensitive areas

- TSM users have CRUD access to timesheet agent lines and read access to commission
  definitions/sections. This addon defines no record rules for its agent lines.
- The agent selector restricts non-commission-managers to their own contact. This domain
  and UI readonly modifiers are not server access controls. Do not describe them as
  ownership or company isolation. OCA settlement permissions remain separate.
- Timesheet field readonly modifiers use `any_settled`, not the presence of agents.
  Assigning an agent leaves the fields editable; any non-cancelled agent settlement
  locks them. Cancelling all such settlements releases them. Keep this condition
  consistent in task, standalone timesheet and pack views.
- Settled agent lines cannot be deleted or have their agent/amount changed; time entries
  with settled agents cannot be deleted. Deletion vetoes are bypassed at uninstall.
- Check task/pack privacy, company boundaries, monetary totals and existing settled
  records before changing access, regeneration or calculation dependencies.

## Validation focus

Check agent configuration, mixed sales/TSM commissions, automatic/manual assignments,
multiple agents, hourly prices with/without a pack, complimentary time, empty dates,
totals, batch deletion, closed-task gating, settlement/cancellation, invoice-source
settlements and commission invoicing. Check clean installation and migrated-data updates
separately. Regression tests are in `tests/`; they must not be imported by `__init__.py`
at the addon root. See [the migration review](specs/migration-review.md) for actual
validation and pending checks.

## Specifications

- Use the shared `odoo-sdd` skill to initialize or adapt the module's SDD method.
- Read specs/README.md, specs/module-contract.md and only the specifications relevant to
  the current task before implementing behavior.
- Keep functional requirements in specs/ and stable agent context in this file. Maintain
  specs as the current coherent agreement: rewrite affected sections after agreed
  changes and remove contradictions and discarded proposals. Avoid conversation
  transcripts, personal attribution and dated revision logs; retain minimal metadata and
  useful verification evidence with brief notes.
- Follow the approval and verification workflow documented in specs/README.md.
- During implementation and manual testing, apply requested minor adjustments that
  preserve agreed behavior without documenting each iteration or asking whether to add
  it to the spec. Resolve functional scope changes before the affected implementation.
  Before closing verification, check final spec alignment, consolidate only necessary
  agreed changes and flag affected tests for rechecking.
- Read `Pruebas manuales y aprobación` before resuming or closing implementation. A
  user-marked checkbox confirms that the check was performed successfully; no additional
  result/evidence field, assessment or note is required. Read any issues reported by
  chat or in `Ajustes pendientes` and check explicit user conformity; "continue" alone
  does not confirm successful tests. Automated tests are not requested or run by
  default; execute them only with applicable explicit authorization. Follow
  specs/README.md for pending checks and verified status.
- When asked to review adjustments, process the relevant spec's final
  `Ajustes pendientes` inbox according to specs/README.md. Integrate notes into
  requirements, open points or verification before removing them; preserve their actual
  approval, implementation and verification state. Resolved minor adjustments that
  preserve the agreement follow the README exception: report their resolution without
  adding requirements or an iteration log.
- Use the brief specification core for bounded changes and expand for material risk or
  uncertainty, as defined in specs/README.md. Reuse existing specs for maintenance; do
  not turn optional sections into a questionnaire.
- Prefer the simplest maintainable solution that meets the agreement, reusing existing
  Odoo and module mechanisms. Before adding custom pieces or material complexity for
  further scenarios, explain the concrete gap, simpler option's limits and
  development/maintenance cost, and obtain the user's scope decision. Follow
  `Solución más sencilla y ampliaciones de alcance` in specs/README.md; preserve
  required security and data integrity and reuse prior scope decisions. Routine
  technical choices need no additional approval.
- Inspect relevant facts before asking and group consequential open questions. Discuss
  material decisions, functional assumptions and weaknesses before the first change
  draft. Explain consequences and recommend options; incorporate answers into the
  requirements. Retain open decisions only with an explicitly agreed deferral or
  requested partial draft; explain them before affected criteria and identify their
  implementation limits. Ask no artificial questions. Do not re-ask for requirements or
  approvals already provided for the same scope.
- Write criteria and manual checks briefly and naturally for a user familiar with the
  change: what must work, what to do and what to observe. Keep implementation detail in
  its technical sections. Explain CA/M references once and spell out each criterion
  reference; keep internal technical checks in their own plan.
- Write SDD prose in Spanish. Keep technical identifiers, paths, frontmatter keys and
  workflow status values unchanged; keep addon code and documentation in English.
