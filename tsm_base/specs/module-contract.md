# Module Contract

## Purpose and scope

Manage customer technical support through TSM projects and tasks. Own projects, tasks,
stages, tags, bulk follower management, customer task navigation, tag and contact
settings, email templates and PDF reports. Timesheets, materials and technical assets
belong to sibling addons; deployment and database-wide migration are outside this
module.

## Actors and permissions

The baseline has TSM users and managers. Users access employee-visible or followed
records and responsible-user operations; managers manage stages, tags and the follower
wizard. The approved migration changes manager assignment to explicit assignment and
adds company-scoped access. Project and task privacy remain employee-visible or
follower-only unless the migration spec says otherwise.

## Models and invariants

- `tsm.project`: customer project, manager, privacy, company and tasks.
- `tsm.task`: unique code, customer/contact, responsible user, project, stage and dates.
- `tsm.task.type`: ordered stages, closed/folded flags and Kanban legends.
- `tsm.task.tags`: unique classification tags and color.
- `follower.assignment.wizard`: bulk follower actions on tasks, projects and contacts.

Task codes remain unique; copies receive new codes. Only tasks in closed stages can be
archived. Projects with active tasks cannot be archived. Projects with any task,
including archived tasks, cannot be deleted. Hiding tags does not delete assignments.
Business records, history, attachments, activities and followers survive migration.

## Integrations and upgrade constraints

Dependencies: `base_setup`, `product`, `mail`, `web`. Task mail prefers a contact with
email, otherwise the customer; project mail uses the customer. Preserve model names, XML
IDs, codes and sequence continuity. Module-owned templates and data are updated to Odoo
18 definitions; independent copies and business records remain. No schema transition is
assumed until production data proves one is needed.

## Risks and open points

Inspect company-less records, cross-company relations, historic manager assignments,
installed sibling modules and the production migration dataset before upgrade. The
manifest and oca-port log do not prove runtime compatibility.
