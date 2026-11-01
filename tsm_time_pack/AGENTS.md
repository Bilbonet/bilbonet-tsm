# tsm_time_pack

Odoo 18 addon in `bilbonet-tsm`, extending TSM timesheets with customer hour packs. It
does not use Odoo Project, HR Timesheets or analytic lines.

## Behavior and boundaries

- `tsm.time.pack` owns a unique sequence code, customer, responsible user, dates,
  privacy, contracted hours and sale settings. Preserve model/field names, XML IDs,
  sequence and decimal precision records, including their `noupdate` policy.
- Changing the positive sale quantity also sets contracted hours. Contracted hours
  remain separately editable. Consumed hours sum linked lines with `discount_time`;
  complimentary hours sum the others. Remaining hours may be negative. A stored
  computation notifies the current user at consumption of at least 90%; it is not a
  one-time warning or a scheduled expiry process.
- Timesheets select the first accessible active pack for their task's exact customer
  when no pack is supplied. Keep `_order = "date_start, id desc"`: selection does not
  inspect expiry, company, remaining balance or commercial-parent contacts. Context
  defaults and explicit pack selections take precedence. Time entries without tasks are
  supported by the dependency and must remain creatable.
- Sale creation requires write access, sales-manager membership and no existing linked
  order. Quantity, unit price and discount feed one order line; optional automatic
  confirmation is retained. The displayed untaxed order amount uses company currency at
  the pack start date. This does not introduce price conversion for sale lines.
- Copies get distinct codes and do not inherit timesheets or a sale link. Preserve batch
  creation/copy behavior and the `[code] title` display name.

## Dependencies and sensitive areas

- Direct dependencies: `product`, `tsm_task_timesheet`, `sale`, `web_notify`. Review
  `tsm_task_timesheet/AGENTS.md` and `tsm_base/AGENTS.md` for shared behavior.
- TSM users have read/write ACLs; TSM managers additionally create/delete packs. The
  user rule restricts **reading** to responsible users, followers or employee-visible
  packs; managers have an unrestricted rule. There is no company isolation rule. Do not
  describe menu domains, `can_edit` or customer filters as server security.
- The inherited archive constraint requires sales-manager membership, although the
  archive buttons require TSM-manager membership. It also applies when `active` is
  supplied on creation. Do not silently redefine these group policies.
- Totals and the detailed report use elevated reads. Linked timesheets do not inherit
  the pack's privacy rules. Review disclosure to ordinary users, followers, companies
  and email recipients before changing those boundaries or claiming security coverage.
- The email template reuses the detailed print report action. Its `print_report_name`
  defines both the printed PDF and email attachment filename; do not add another action
  just to give email attachments a separate filename. Editing a template can replace
  customized database values because it is not `noupdate`. Review that during an update
  on a migrated database.
- Source version `15.0.1.0.1` already renamed `contrated_hours` to `contracted_hours`.
  Databases predating that change require a separate data review; do not silently
  recreate a historical migration script or assume that a source port moved data.

## Validation focus

Check product configuration; pack creation, batch edits/copy and sequence; manual,
contextual and automatic time-entry selection; charged/free hours and the 90% warning;
list/form/kanban and both menus; sale creation, confirmation, duplicates and currencies;
archive permissions; email body/recipient/attachment and summary/detailed/task/project
reports. Check installation and an update on migrated data separately.

Regression coverage is in `tests/`; it must not be imported by the addon root.
Attachment tests mock PDF generation and do not validate the PDF engine. The migration
review records actual checks and pending user verification. Database operations and test
execution follow the inherited authorization policy.

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
