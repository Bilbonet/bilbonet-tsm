---
id: change-2026-09-05-migrate-tsm-base-15-to-18
title: "Migrate tsm_base from Odoo 15 to Odoo 18"
status: verified
module: tsm_base
created: 2026-09-05
---

# Change Specification

## Problem and goal

The Odoo 15 production module was ported with `oca-port`, but automatic changes left
Odoo 18 load blockers and incompatible ORM, mail, view and permission APIs. Deliver a
working Odoo 18 module while preserving production business data and the agreed behavior
below. Continue on `18.0-mig-tsm_base`; do not create another branch.

## Scope

Adapt Python/ORM contracts, list/Kanban/settings views, security, followers, composer
and email templates, reports, translations and packaging. Add scripts only for proven
persisted-data or metadata transitions. Fresh installation and production upgrade are
separate scenarios. The production upgrade is explicitly deferred from this change
because no persisted-data or metadata transition requiring a module-local migration
script has been identified.

## Agreed behavior

1. TSM management is granted explicitly, not through the new-user template. Records are
   company-scoped; managers see all records in allowed companies.
2. A project cannot be deleted while it has any task, active or archived.
3. Changing “Use Tags in Tasks” takes effect on Save for active tasks and future
   defaults; Discard has no effect. Archived tasks and tag assignments remain.
4. Bulk follower operations use standard Odoo 18 document subscription APIs, default
   subscription types and existing preferences, without system-wide administrative
   bypasses or duplicate followers.
5. Module-owned XML data, templates, reports and translations are updated to the Odoo 18
   definitions. Business records and independently created copies remain.

## Functional scenarios

### Creation and counts

Given configured stages, projects and customer hierarchies, create or copy tasks
individually and in batches. Preserve defaults, unique codes, `[code] title` display
names and empty stage columns. Counts include accessible archived tasks and customer
descendants without stale accumulation.

### Archive and deletion

Only tasks in closed stages can be archived; restore is allowed. Archiving resets
priority to Low and Kanban state to Normal. Projects with active tasks cannot be
archived. Projects with any task cannot be deleted, including when all tasks are
archived. Batch operations enforce the same rules.

### Settings and access

Save/discard has exactly the agreed tag behavior. Users, managers, two companies,
followers and non-followers respect company, privacy and responsibility rules in menus,
counts, reports and the follower wizard.

### Mail and reports

Task mail prefers a contact with email, otherwise the customer; project mail uses the
customer. Composer opens without sending. Reports retain company identity, content,
archived-task behavior and Spanish filenames, including the task code.

### Production upgrade (deferred)

On a production copy, retain records, relations, codes, sequence continuity, archives,
messages, attachments, activities and followers. Update module-owned definitions
intentionally, without resetting business data.

## Acceptance criteria

- [x] Fresh installation loads all declared data and views without errors.
- [x] Menus, forms, lists, Kanban, settings, quick create, stage expansion, avatars,
      colors and actions work.
- [x] Individual and batch create/copy preserve defaults and unique task codes.
- [x] Counts/navigation cover archives and customer descendants correctly.
- [x] Archive/restore/delete safeguards hold for visible and hidden related tasks.
- [x] Settings Save/Discard has the agreed effects without deleting tags.
- [x] Explicit manager assignment and company/privacy rules hold for all roles.
- [x] Followers work without system administration or duplicates.
- [x] Mail composition, recipients, report attachments and Spanish PDFs work.
- [x] Authorized repository checks pass and omitted checks are recorded.

The production-copy comparison and real production upgrade are deferred to a separate
change. They are not required to verify this source migration because the current module
changes do not introduce a persisted-data transition or module-local migration script.

## Implementation and validation plan

Fix email-template and settings load blockers first. Then adapt `_read_group`, stage
expansion, display names, batch copy, composer context and Odoo 18 views. Implement the
agreed deletion, settings, security and follower behavior. Inspect production data
before adding module-local migration scripts. Add focused tests for counts, codes/copy,
safeguards, settings and permissions; inspect Kanban and PDF output in Spanish;
intercept outgoing mail. Run pre-commit, tests, installation or upgrade only when
explicitly authorized.

## Open points and risks

Before database execution, identify company-less records, cross-company relations,
historic manager assignments, installed sibling addons and the database migration
orchestration. Do not silently reassign or delete such data. The current manifest,
oca-port log and static source do not prove completed migration.

## Verification record

Manual functional verification was completed on the installed/demo environment,
including installation, project and task Kanban behavior, menus, smart buttons, settings
and the migrated views.

The Odoo transaction suite was executed on database `18-bilbonet` while updating
`tsm_base`: 8 tests ran with 0 failures and 0 errors. The existing filestore was
available during the run.

Python compilation and the configured repository pre-commit gate pass, including XML,
Odoo module, Ruff and mandatory `pylint-odoo` checks. The production-copy comparison and
real production upgrade remain intentionally deferred to a future change; no
module-local migration script is included in this migration.
