# Contrato del módulo

## Identidad y fuentes

- Nombre técnico: `tsm_base`; nombre del manifest: `Technical Support Management`.
- Odoo: `18.0`; versión declarada del addon: `18.0.1.1.0`; estado: `Beta`.
- Workspace: `/home/bilbonet/odoo18`; repositorio: `_ext/bilbonet/bilbonet-tsm`.
- Ruta del módulo: `_ext/bilbonet/bilbonet-tsm/tsm_base`; el enlace activo
  `server/3addons/tsm_base` del workspace apunta a esa misma fuente.

Este contrato conserva las reglas documentadas previamente. El acuerdo funcional y su
evidencia histórica están en la
[especificación de migración](changes/change-2026-09-05-migrate-tsm-base-15-to-18.md),
con `status: verified`. El manifest, los modelos y las reglas de seguridad permiten
contrastar la implementación disponible; su lectura no constituye aprobación de
requisitos adicionales ni verificación funcional nueva.

La sustitución del indicador por `task_status` se define en la
[spec de estado de la tarea](changes/change-2026-10-11-task-status.md), con
`status: verified`. El usuario ha confirmado la comprobación de CA-01 a CA-10, incluidos
interfaz, actualización de datos, conservación de clasificaciones y permisos. Los
resultados y el alcance de la evidencia se recogen en esa spec. La evidencia histórica
de la migración sigue siendo independiente de este cambio posterior.

## Propósito, alcance y límites

Gestionar el soporte técnico a clientes mediante proyectos y tareas TSM. El módulo
incluye proyectos, tareas, etapas, etiquetas, gestión masiva de seguidores, navegación a
tareas desde clientes, ajustes de etiquetas y contactos, plantillas de correo e informes
PDF. Es independiente de Odoo Project. Las hojas de horas, los materiales y los activos
técnicos pertenecen a addons hermanos; el despliegue y la migración global de la base de
datos quedan fuera del módulo.

## Actores y permisos

Existen usuarios y responsables de TSM. Los usuarios acceden a registros visibles para
empleados o seguidos por ellos y realizan las operaciones permitidas al usuario
asignado. Los responsables gestionan etapas, etiquetas y el asistente de seguidores. La
migración acordada establece la asignación explícita del grupo de responsables y el
acceso limitado por compañía; los responsables acceden a los registros de las compañías
permitidas. La privacidad de proyectos y tareas sigue siendo visible para empleados o
restringida a seguidores, según lo definido en la especificación de migración.

## Modelos principales

- `tsm.project`: proyecto del cliente, responsable, privacidad, compañía y tareas.
- `tsm.task`: código único, cliente/contacto, usuario asignado, proyecto, etapa, fechas
  e indicador visual `task_status` con seguimiento estándar en el chatter.
- `tsm.task.type`: etapas ordenadas, indicadores de cierre y plegado y leyenda de
  prioridad; sin etiquetas personalizadas del estado de la tarea.
- `tsm.task.tags`: etiquetas de clasificación únicas y color.
- `follower.assignment.wizard`: acciones masivas sobre seguidores de tareas, proyectos y
  contactos.

## Invariantes estables de negocio

Los códigos de tarea siguen siendo únicos; las copias reciben códigos nuevos. Solo
pueden archivarse tareas en etapas cerradas. No pueden archivarse proyectos con tareas
activas. No pueden eliminarse proyectos que tengan alguna tarea, incluidas las
archivadas, aunque las reglas de privacidad oculten tareas al usuario que opera sobre el
proyecto. Estas comprobaciones no conceden acceso al contenido de tareas ocultas ni
amplían los permisos sobre el proyecto. Ocultar etiquetas no elimina sus asignaciones.
Los registros de negocio, el historial, los adjuntos, las actividades y los seguidores
deben conservarse en la migración.

El estado visual de la tarea es independiente de su etapa, cierre y archivado. `done`
expresa tarea realizada sin cerrar, archivar ni bloquear su edición. Archivar restablece
la prioridad a `0` y el indicador a `to_define`; restaurar no recupera la clasificación
anterior. Las nuevas tareas y copias parten sin clasificación. La opacidad por `done`
afecta únicamente al contenido kanban.

El kanban resalta las fechas límite anteriores al día actual de la zona horaria del
cliente web. Una tarea que vence hoy, en una fecha futura o sin fecha límite no se
resalta como vencida.

## Integraciones

Dependencias directas: `base_setup`, `product`, `mail` y `web`. El módulo extiende
`res.partner` y `res.config.settings` y utiliza hilos de correo, actividades, plantillas
e informes QWeb. El correo de tareas prefiere un contacto con dirección de correo y, en
su defecto, el cliente; el correo de proyectos utiliza el cliente. El contacto puede
pertenecer a otra cuenta por necesidades entre empresas y sucursales. Cambiar el cliente
o el proyecto no lo borra automáticamente ni impone una validación de pertenencia.

El PDF individual de una tarea y su adjunto de correo usan el nombre
`código_título_de_la_tarea.pdf`, sin paréntesis. El código precede al título y las
secuencias de espacios en blanco se sustituyen por un guion bajo. La traducción del
nombre conserva la misma expresión que el informe.

## Restricciones de datos y actualización

Conservar los nombres de modelos, XML IDs, códigos y continuidad de las secuencias. Las
plantillas y los datos propios del módulo se actualizan a las definiciones de Odoo 18;
las copias independientes y los registros de negocio se conservan. Las transiciones de
esquema se justifican por el cambio concreto, sin presuponer conversiones de producción
ajenas a su alcance.

La comparación sobre una copia de producción y la actualización real de producción están
aplazadas a un cambio separado y no forman parte del alcance verificado de la migración
de código. No se incluye un script local para actualizar bases existentes. Las seis
reglas de seguridad están bajo `noupdate="1"`; si una base conserva los XML IDs de Odoo
15, una actualización ordinaria no reemplaza sus dominios antiguos. Retirar la
asignación del grupo de responsables a `base.default_user` del XML tampoco elimina
membresías anteriores. Conservar registros es un requisito; la evidencia histórica
existente no demuestra una migración de producción completada.

El cambio de `task_status` añade una columna independiente con valor inicial
`to_define`, mediante la inicialización estándar de Odoo. Incluye tareas activas y
archivadas, sin equivalencias con el indicador anterior ni renombrado de su columna. Las
actualizaciones posteriores conservan las clasificaciones nuevas guardadas. La
verificación manual de CA-09 confirma esta transición y la conservación de datos en el
entorno comprobado; no acredita una actualización real de producción.

## Riesgos y puntos abiertos

Antes de actualizar una base de datos de producción, inspeccionar registros sin
compañía, relaciones entre compañías, asignaciones históricas de responsables, addons
hermanos instalados y el conjunto de datos de migración de producción. No reasignar ni
eliminar silenciosamente esos datos. El manifest y el registro de `oca-port` no
demuestran compatibilidad en ejecución.

Antes de la migración productiva, comparar en cada base los dominios y metadatos de las
seis reglas y las asignaciones de grupos, incluidas las de `base.default_user`. Puede
utilizarse un procedimiento común con acciones condicionadas al estado encontrado, pero
no deben sobrescribirse personalizaciones ni retirarse permisos históricos sin revisión.
Las nuevas validaciones de relaciones entre compañías quedan aplazadas.

Estas comprobaciones de producción siguen pendientes según la especificación existente.
La preparación documental no las resuelve ni autoriza operaciones de base de datos.
