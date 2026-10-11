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
separate scenarios.

La actualización de producción queda aplazada a un cambio separado. No se incluye un
script local: antes hay que inspeccionar los datos, las reglas bajo `noupdate` y las
asignaciones históricas de grupos de cada base.

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

Solo se archivan tareas en etapas cerradas; restaurarlas está permitido. El reinicio de
prioridad y estado visual se define en la especificación vigente de `task_status`. Los
proyectos con tareas activas no se archivan. Los proyectos con cualquier tarea, activa o
archivada, no se eliminan. Estas protecciones incluyen tareas privadas que el usuario no
puede leer y se aplican al lote completo antes de modificarlo. Se comprueba primero el
permiso sobre los proyectos; detectar la existencia de tareas ocultas no concede acceso
a su contenido ni permite modificarlas.

El kanban resalta como vencidas las fechas límite anteriores al día actual del cliente
web, conservando el día calendario de `fields.Date`. Hoy, las fechas futuras y la
ausencia de fecha límite no se resaltan como vencidas.

### Settings and access

Save/discard has exactly the agreed tag behavior. Users, managers, two companies,
followers and non-followers respect company, privacy and responsibility rules in menus,
counts, reports and the follower wizard.

### Correo e informes

El correo de tareas prefiere un contacto con dirección de correo y, en su defecto, el
cliente; el correo de proyectos utiliza el cliente. Se permite conservar un contacto de
otra cuenta para relaciones entre empresas y sucursales; cambiar el cliente o el
proyecto no lo limpia ni impone una validación de pertenencia. El compositor se abre sin
enviar. Los informes conservan la identidad de la compañía, el contenido y el
comportamiento de las tareas archivadas. El PDF individual de una tarea y su adjunto de
correo se llaman `código_título_de_la_tarea.pdf`, sin paréntesis; las secuencias de
espacios en blanco se sustituyen por un guion bajo. La traducción conserva la expresión
del informe sin sustituir el código por el título.

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

La comparación con una copia y la actualización real de producción quedan aplazadas a un
cambio separado y no forman parte de la evidencia histórica de esta migración de código.
Las correcciones actuales requieren nueva verificación funcional; no se deduce su
resultado de las casillas ni del estado histórico de esta especificación.

## Implementation and validation plan

Fix email-template and settings load blockers first. Then adapt `_read_group`, stage
expansion, display names, batch copy, composer context and Odoo 18 views. Implement the
agreed deletion, settings, security and follower behavior. Inspect production data
before adding module-local migration scripts. Add focused tests for counts, codes/copy,
safeguards, settings and permissions; inspect Kanban and PDF output in Spanish;
intercept outgoing mail. Run pre-commit, tests, installation or upgrade only when
explicitly authorized.

## Open points and risks

Antes de ejecutar operaciones de base de datos, inspeccionar registros sin compañía,
relaciones entre compañías, asignaciones históricas de responsables, addons hermanos
instalados y la orquestación de la migración. Las validaciones nuevas de compatibilidad
entre compañías quedan aplazadas; no reasignar ni eliminar datos silenciosamente.

Las seis reglas de seguridad mantienen `noupdate="1"`. Si se conservan sus XML IDs de
Odoo 15, una actualización ordinaria no sustituye los dominios antiguos sin filtro por
compañía. Retirar del XML el grupo TSM Manager de `base.default_user` tampoco elimina
asignaciones existentes. Antes de migrar cada base, contrastar dominios, metadatos
`noupdate` y grupos históricos. Puede prepararse un procedimiento común, condicionado a
ese inventario y a la revisión de personalizaciones, sin aplicar una sobrescritura
indiscriminada. El manifest, el registro de `oca-port` y el código no demuestran la
migración de producción.

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

La evidencia histórica de los PDF no verifica el ajuste actual de su nombre. Se ha
comprobado por lectura que la descarga individual y los adjuntos de correo usan
`print_report_name`; el XML y su traducción española contienen la misma expresión. El
parseo XML y del catálogo y la evaluación aislada de la expresión con valores ficticios
confirman el código inicial y los guiones bajos, también con espacios repetidos,
tabulaciones y saltos de línea. Queda pendiente cargar la definición y su traducción en
Odoo y verificar la descarga y el adjunto de correo en ejecución, con autorización.

Las protecciones de proyectos se han corregido para incluir tareas ocultas mediante
consultas de existencia acotadas, después de comprobar el acceso al proyecto. Se han
añadido dos regresiones: usuario normal con una tarea privada oculta, operaciones en
lote y tarea archivada; y rechazo por permisos antes de comprobar tareas ocultas. Los
fixtures invalidan `task_ids` antes de leerlo con el usuario limitado para no reutilizar
la caché poblada como administrador y comprueban la ocultación mediante búsqueda o
permiso de lectura. La ejecución aportada obtuvo 13 pruebas correctas y tres avisos de
obsolescencia de `datetime.utcnow()` en el core de correo de Odoo.

La preparación del usuario utiliza `no_reset_password=True` para evitar su invitación
automática. La asignación de los dos proyectos aplica
`mail_auto_subscribe_no_notify=True` solo en esa escritura, conservando seguidores y
tracking y evitando las notificaciones de asignación ajenas a la prueba de permisos. No
se modifica el core ni se filtran warnings. Queda pendiente repetir la suite tras este
ajuste para comprobar el resultado y la desaparición de esos avisos; el agente no ha
ejecutado pruebas de Odoo. El resaltado usa `text-danger fw-bold`, compatible con las
tarjetas de Odoo 18; `oe_kanban_text_red` solo se define para tarjetas antiguas. La
sintaxis Python y XML y el lint de Ruff son correctos. La expresión kanban se ha
evaluado aisladamente con Luxon del core: 80 casos correctos en cinco zonas horarias,
incluidos ayer, hoy, mañana, ausencia de fecha, cambio de año y año bisiesto. Queda
pendiente repetir la suite tras el ajuste de notificaciones y comprobar el resaltado en
el navegador, con autorización. El estado `verified` conserva la evidencia histórica; no
acredita estas correcciones posteriores.
