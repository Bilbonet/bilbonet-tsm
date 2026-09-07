---
id: change-2026-09-05-migrate-tsm-base-15-to-18
title: "Migrate tsm_base from Odoo 15 to Odoo 18"
status: implementing
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
separate scenarios.

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

### Production upgrade

On a production copy, retain records, relations, codes, sequence continuity, archives,
messages, attachments, activities and followers. Update module-owned definitions
intentionally, without resetting business data.

## Acceptance criteria

- [ ] Fresh installation loads all declared data and views without errors.
- [ ] Menus, forms, lists, Kanban, settings, quick create, stage expansion, avatars,
      colors and actions work.
- [ ] Individual and batch create/copy preserve defaults and unique task codes.
- [ ] Counts/navigation cover archives and customer descendants correctly.
- [ ] Archive/restore/delete safeguards hold for visible and hidden related tasks.
- [ ] Settings Save/Discard has the agreed effects without deleting tags.
- [ ] Explicit manager assignment and company/privacy rules hold for all roles.
- [ ] Followers work without system administration or duplicates.
- [ ] Mail composition, recipients, report attachments and Spanish PDFs work.
- [ ] A production-copy comparison proves data and sequence preservation.
- [ ] Authorized repository checks pass and omitted checks are recorded.

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

Focused regression tests now cover archived task counts, customer descendants, batch
copies, archive/delete safeguards, settings behavior, follower assignment and composer
contexts. Python compilation and the configured repository pre-commit gate pass,
including XML, Odoo module, Ruff and mandatory `pylint-odoo` checks.

Odoo transaction tests, fresh installation, PDF/mail rendering and production database
comparison remain intentionally unexecuted. They require an authorized Odoo database
environment and production-copy evidence before this specification can move to
`verified`.
