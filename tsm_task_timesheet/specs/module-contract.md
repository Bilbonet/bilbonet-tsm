# Contrato del módulo

Este contrato recoge hechos observados en el código de `tsm_task_timesheet` para
Odoo 18. No constituye aprobación de nuevos requisitos ni evidencia de compatibilidad
funcional. La [revisión de migración](migration-review.md) separa las comprobaciones
realizadas de las pendientes.

## Propósito y alcance

Registrar y consultar el tiempo dedicado a tareas de soporte de `tsm_base`. Depende
únicamente de ese addon; no utiliza Odoo Project, HR Timesheets ni
`account.analytic.line`. Incluye partes, etiquetas, configuración y vistas de análisis.
Los informes PDF pertenecen a `tsm_base`: este addon añade vistas pivot, no plantillas
PDF.

## Actores y permisos observados

- Los usuarios TSM pueden leer, crear, modificar y eliminar partes y leer etiquetas.
- Los responsables TSM pueden gestionar etiquetas. El menú de etiquetas requiere además
  el grupo de administración del sistema.
- Los grupos técnicos de título y etiqueta controlan campos y valores por defecto. La
  configuración los desmarca mutuamente mediante onchanges; no hay exclusión general de
  grupos impuesta por servidor.
- «Mis partes» filtra por usuario; «Todos los partes» y los menús de análisis están
  limitados a responsables en la navegación.
- No existen reglas de registros propias para partes. Los filtros de acción y las
  restricciones de menú no garantizan privacidad por tarea, propiedad ni aislamiento por
  compañía. El campo `company_id` obligatorio tampoco establece esa garantía.

## Modelos y conceptos principales

- `tsm.task.timesheet`: inicio, horas decimales, usuario, compañía, título y etiqueta.
  Su `task_id` no es obligatorio en el modelo, aunque las vistas principales lo exigen.
  Proyecto es calculado, almacenado y editable; el cliente es relacionado almacenado.
- `tsm.task.timesheet.tags`: nombre único, orden, activo y predeterminado. La
  restricción Python rechaza otra etiqueta activa predeterminada; no es una garantía de
  exclusión entre transacciones concurrentes.
- `tsm.task`: colección de partes y suma almacenada de horas. El cálculo utiliza
  lecturas elevadas, independientemente de los permisos del lector.

El nombre histórico `tag_ids` representa una relación Many2one. No debe renombrarse como
limpieza de código sin estudiar su migración.

## Flujos y comportamiento conservado

- Registrar una hora de inicio y una duración, o pulsar Stop para calcular las horas
  transcurridas. El final del calendario suma la duración al inicio; queda vacío si no
  hay inicio. Stop exige inicio.
- En los listados y formulario de partes se puede elegir primero proyecto o tarea. El
  proyecto filtra las tareas; la tarea completa proyecto y cliente y limita el selector
  de proyecto al suyo. Quitar la tarea conserva el proyecto como filtro. Una restricción
  de servidor impide combinar tarea y proyecto incompatibles. Cambiar el proyecto de la
  propia tarea actualiza el de sus partes. Véase la
  [especificación de selección](changes/change-2026-10-24-project-task-selection.md).
- El título calculado utiliza el nombre de la etiqueta cuando se activa su grupo y hay
  etiqueta; en modo título propone `/`. En los demás casos conserva el valor previo y
  usa `/` si no existe título. Se admite un título explícito.
- Se permite registrar partes con ambas opciones desactivadas, sin mostrar título ni
  etiqueta en la pestaña de la tarea. El nombre técnico obligatorio se calcula como `/`
  antes de insertar el parte; no se exige introducirlo al usuario.
- Iniciar desde la creación rápida exige título y cliente, valida el formulario y guarda
  la tarea antes de crear el parte. Si falta alguno, muestra los campos obligatorios
  pendientes y no crea la tarea ni el parte. Al completar los datos, añade un parte con
  duración cero y abre la tarea en edición. Sustituye su descripción por un sello
  temporal, con zona contextual/del usuario y UTC como respaldo.
- Abrir o cerrar desde un parte selecciona la primera etapa abierta o cerrada que
  encuentre la búsqueda. Cerrar desde este botón exige duración distinta de cero en
  todos los partes de la tarea.
- El onchange de etapa rechaza partes de duración cero al elegir una etapa cerrada. No
  es una restricción general sobre escrituras ORM de etapa.
- Archivar rechaza partes de duración cero y conserva las comprobaciones del padre sobre
  etapa y restablecimiento de prioridad/estado. Desarchivar no impone ese veto de
  duración.
- Eliminar una tarea con partes está prohibido en operaciones ordinarias; la salvaguarda
  no bloquea la desinstalación del módulo.

## Vistas e integración

La navegación incluye listas y formularios de partes propios y de todos los usuarios,
kanban, calendario, pivots por usuario/tarea, partes de proyecto y una pestaña en la
tarea. La configuración se inserta en la app `tsm_base`. `amount` se almacena en horas
decimales y se presenta con `float_time`.

## Conservación de datos y migración

El historial fuente confirma un salto 15.0 → 18.0. Conservar tablas, modelos, campos,
XML IDs, partes históricos y la etiqueta inicial `noupdate`. Las correcciones de esta
revisión no introducen cambios de esquema ni justifican por sí solas un script de
transformación de datos. Esto no acredita el camino de actualización de una base real
entre versiones.

## Riesgos y puntos abiertos

La política de aislamiento de partes por usuario, tarea y compañía no está definida por
reglas de registros del addon. Requiere una decisión funcional y verificación con
usuarios ordinarios antes de ofrecer esas garantías. Se ha comprobado instalación limpia
y ejecutado la suite TSM y los tests Hoot del inicio desde Kanban; la evidencia y sus
límites figuran en la revisión de migración. Quedan pendientes la actualización sobre
datos migrados y las comprobaciones funcionales no cubiertas. No se ha inspeccionado una
base de cliente.
