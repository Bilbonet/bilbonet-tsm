# AGENTS.md

Repository-level context for the Bilbonet Odoo 18 addons repository. Keep this file
concise and limited to facts that are useful to future agents and are not already
provided by the Odoo 18 workspace instructions, OCA skills, or the repository
configuration.

## Repository identity

- **Name:** `bilbonet-tsm`
- **Purpose:** private Bilbonet addons for managing technical-support projects and
  tasks.
- **Odoo version:** `18.0`
- **Main branch:** `18.0`
- **Type:** custom vertical addon repository.
- **Status:** active maintenance; the current module manifest declares the module as
  `Beta`.

## Scope and boundaries

This repository currently contains one addon:

| Module     | Purpose                                                                                                            | Status                    |
| ---------- | ------------------------------------------------------------------------------------------------------------------ | ------------------------- |
| `tsm_base` | Technical-support projects and tasks, with stages, tags, followers, activities, email composition and PDF reports. | Beta / active maintenance |

The repository includes the addon source, module-local specifications, tests, README
source fragments and repository tooling. It does not own Odoo core, addons for other
Odoo versions, deployment infrastructure or customer production data.

Detailed functional invariants, permissions, migration constraints and validation focus
belong in [`tsm_base/AGENTS.md`](tsm_base/AGENTS.md) and its `specs/` directory. Do not
duplicate those details here.

## Working context and source of truth

- Work from the Odoo 18 workspace and use its version-matched environment and active
  addon layout. Do not apply API or command assumptions from another Odoo version
  without checking the Odoo 18 source.
- Follow inherited workspace and global instructions first. This file adds
  repository-specific context; `tsm_base/AGENTS.md` adds more specific module context.
- Treat the module manifest, repository configuration, CI workflows and source
  specifications as authoritative for technical behavior. Do not treat an `oca-port` log
  or an automated migration result as proof of runtime compatibility.
- Requirements and migration behavior belong in `tsm_base/specs/`; generated
  `README.rst` files are outputs and must not be edited directly. Update their source
  fragments when documentation changes are requested.

## Dependencies and integrations

The repository has no shared integration layer beyond the addon. `tsm_base` declares
these Odoo dependencies in its manifest:

- `base_setup`
- `product`
- `mail`
- `web`

The module uses Odoo mail threads, activities, templates, QWeb reports and
configuration/contact extensions. Review its module-level context before changing
security, mail, reports, data definitions or model contracts.

## Validation expected by this repository

The configured repository gate is:

```text
pre-commit run --all-files --show-diff-on-failure --color=always
```

The CI test workflow uses the OCA container and runs, in order, addon installation,
license and development-status checks, test-database initialization and `oca_run_tests`.
These checks require an authorized Odoo 18 and PostgreSQL environment; do not run them,
upgrade modules or use a database unless the user explicitly requests it. When checks
are omitted, report that fact rather than claiming validation.

## Change boundaries

Normal changes are limited to the existing addon, its tests, module specifications,
README source fragments and repository configuration that is needed for the requested
work.

Require explicit review and coordinated inspection before changing:

- manifest dependencies, licensing/authorship metadata or addon boundaries;
- security groups, access rules, company/privacy behavior or follower access;
- module-owned data, templates, reports, XML IDs or translations;
- persisted-data migration behavior or assumptions about production records;
- repository CI, pre-commit hooks or external Python/system dependencies.

Do not create another addon, assume a database-wide migration is part of an addon
change, or silently change deployment-specific files. Preserve existing user changes in
unrelated files and keep generated files under their normal generation workflow.

## Module-level context policy

Keep `tsm_base/AGENTS.md` because this addon has its own business invariants,
permissions, migration constraints and validation risks. Add or update repository-level
context only when a fact is shared across modules or affects repository-wide work; do
not use either `AGENTS.md` as a task log or a generic replacement for Odoo/OCA guidance.
