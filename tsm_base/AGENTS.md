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

Keep generated documentation in its source fragments; do not edit generated `README.rst`
directly. Preserve task codes, sequence continuity, business records, archived records,
messages, attachments, activities and followers. Verify privacy, company boundaries and
follower actions with non-administrator users.

Task status is independent of stage closure and archiving. Its selector belongs to this
addon's backend assets and uses `web`; keep the addon independent of Odoo Project.
Consult the [task-status spec](specs/changes/change-2026-10-11-task-status.md) before
changing this boundary or reintroducing stage-specific status labels.

Project archive/delete safeguards must include tasks hidden by record rules without
exposing their contents. Check project access before using elevated existence checks;
deletion must also include archived tasks. Contacts from another customer account are
allowed; do not introduce account-membership validation or automatic contact clearing.

## Specifications

- Use the shared `odoo-sdd` skill to initialize or adapt the module's SDD method.
- Read [specs/README.md](specs/README.md),
  [specs/module-contract.md](specs/module-contract.md) and only the specifications
  relevant to the current task before implementing behavior. Method navigation links to
  [changes](specs/changes/README.md), [decisions](specs/decisions/README.md) and
  editable [change](specs/templates/change.md) and
  [decision](specs/templates/decision.md) templates are kept in specs/README.md.
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

## Validation focus

Cover counts, stage expansion, batch create/copy, archive/delete safeguards, settings
save/discard, permissions, follower subscriptions, email composition and Spanish PDF
output. Test fresh installation separately from production-data migration. Follow
inherited validation policy before executing checks.
