# tsm_task_timesheet

Odoo 18 addon in `bilbonet-tsm`, extending `tsm_base` with task time entries. It does
not use Odoo Project, HR Timesheets or analytic lines.

## Behavior and boundaries

- `tsm.task.timesheet` stores decimal hours and a start datetime. Its stored end
  datetime feeds the calendar; a missing start date leaves the end date empty. Stop
  computes elapsed hours and requires a start date.
- `tag_ids` is an established **Many2one** despite its plural technical name. Preserve
  that name, model names, XML IDs and the `noupdate` default tag.
- Title/tag configuration uses implied groups and mutually exclusive UI onchanges. This
  is not a server constraint preventing both groups together. An explicit title remains
  editable. Computation uses the selected tag in tag mode and `/` in title mode;
  otherwise it preserves the existing title, with `/` as a fallback. Both options may be
  disabled. The required title must be computed before insertion when omitted; keep
  `precompute=True` so hidden fields do not block time entry creation. A fixed field
  default would bypass tag-based computation.
- Closing from a timesheet rejects tasks containing zero-duration lines. The task stage
  onchange gives the same feedback; it does not enforce every direct ORM stage write.
  Archiving also checks durations and retains the parent's stage and status rules.
  Deletion with lines is blocked, except during module uninstallation.
- Start replaces the task description with a timestamp and adds a running line. Preserve
  this existing behavior unless a functional change is requested.
- Quick-create Start validates and saves the task before calling the server method. The
  backend asset installs the native view-button hook only for TSM task quick creation.
  Keep the title/customer checks and the stop-on-failed-save behavior; an empty
  recordset must produce a user-facing error rather than a singleton traceback.

- Timesheet projects are computed, stored and editable. Selecting a task supplies its
  project; selecting a project filters tasks. A task/project constraint also protects
  ORM calls. Do not turn this into an editable related field: its inverse could move the
  task itself. Changing the task's project must still update its time entries. See the
  [selection specification](specs/changes/change-2026-10-24-project-task-selection.md).

## Dependencies and sensitive areas

- The only direct dependency is `tsm_base`. Review its settings app, task views, stages,
  archive checks and access rules when changing this integration.
- Timesheet ACLs grant all TSM users CRUD. Tags are readable by TSM users and managed by
  TSM managers. The configuration menu additionally requires system access. This addon
  has no timesheet record rules: action/menu filters do not enforce ownership, task
  privacy or company isolation. Do not claim that timesheet security mirrors task
  security; changes need an explicit policy.
- Task totals use elevated reads. Review disclosure and company boundaries with ordinary
  users before claiming functional/security compatibility.

## Validation focus

Check settings save/discard, manual titles and tags, quick start with/without a
timezone, stop and totals, list/form/kanban/calendar/pivot views, date filters,
close/reopen, archive/delete and batch tag validation. Check installation and an update
on migrated data separately; source compatibility does not prove database migration. See
[the migration review](specs/migration-review.md). Database operations and Odoo test
execution follow the inherited authorization policy. Regression tests live in `tests/`
and must not be imported by the addon root.

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
