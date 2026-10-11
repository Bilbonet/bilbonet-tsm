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

## Specifications

- Use the shared `odoo-sdd` skill to initialize or adapt the module's SDD method.
- Read [specs/README.md](specs/README.md),
  [specs/module-contract.md](specs/module-contract.md) and only the specifications
  relevant to the current task before implementing behavior.
- Keep functional requirements in specs/ and stable agent context in this file. Maintain
  specs as the current coherent agreement: rewrite affected sections after agreed
  changes and remove contradictions and discarded proposals. Avoid conversation
  transcripts, personal attribution and dated revision logs; retain minimal metadata and
  useful verification evidence with brief notes.
- Follow the approval and verification workflow documented in specs/README.md.
- When asked to review adjustments, process the relevant spec's final
  `Ajustes pendientes` inbox according to specs/README.md. Integrate notes into
  requirements, open points or verification before removing them; preserve their actual
  approval, implementation and verification state.
- Use the brief specification core for bounded changes and expand for material risk or
  uncertainty, as defined in specs/README.md. Reuse existing specs for maintenance; do
  not turn optional sections into a questionnaire.
- Inspect relevant facts before asking and group consequential open questions. Discuss
  material decisions, functional assumptions and weaknesses before presenting a spec for
  approval. Explain consequences and recommend options; refine the same draft from the
  answers. Highlight remaining open points and their implementation impact in the
  delivery summary. Ask no artificial questions. Do not re-ask for requirements or
  approvals already provided for the same scope.
- Write SDD prose in Spanish. Keep technical identifiers, paths, frontmatter keys and
  workflow status values unchanged; keep addon code and documentation in English.

## Validation focus

Cover counts, stage expansion, batch create/copy, archive/delete safeguards, settings
save/discard, permissions, follower subscriptions, email composition and Spanish PDF
output. Test fresh installation separately from production-data migration. Follow
inherited validation policy before executing checks.
