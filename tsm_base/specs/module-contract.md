# Contrato del módulo

## Identidad y fuentes

- Nombre técnico: `tsm_base`; nombre del manifest: `Technical Support Management`.
- Odoo: `18.0`; versión declarada del addon: `18.0.1.0.0`; estado: `Beta`.
- Workspace: `/home/bilbonet/odoo18`; repositorio: `_ext/bilbonet/bilbonet-tsm`.
- Ruta del módulo: `_ext/bilbonet/bilbonet-tsm/tsm_base`; el enlace activo
  `server/3addons/tsm_base` del workspace apunta a esa misma fuente.

Este contrato conserva las reglas documentadas previamente. El acuerdo funcional y su
evidencia histórica están en la
[especificación de migración](changes/change-2026-09-05-migrate-tsm-base-15-to-18.md),
con `status: verified`. El manifest, los modelos y las reglas de seguridad permiten
contrastar la implementación disponible; su lectura no constituye aprobación de
requisitos adicionales ni verificación funcional nueva.

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
- `tsm.task`: código único, cliente/contacto, usuario asignado, proyecto, etapa y
  fechas.
- `tsm.task.type`: etapas ordenadas, indicadores de cierre y plegado y leyendas de
  Kanban.
- `tsm.task.tags`: etiquetas de clasificación únicas y color.
- `follower.assignment.wizard`: acciones masivas sobre seguidores de tareas, proyectos y
  contactos.

## Invariantes estables de negocio

Los códigos de tarea siguen siendo únicos; las copias reciben códigos nuevos. Solo
pueden archivarse tareas en etapas cerradas. No pueden archivarse proyectos con tareas
activas. No pueden eliminarse proyectos que tengan alguna tarea, incluidas las
archivadas. Ocultar etiquetas no elimina sus asignaciones. Los registros de negocio, el
historial, los adjuntos, las actividades y los seguidores deben conservarse en la
migración.

## Integraciones

Dependencias directas: `base_setup`, `product`, `mail` y `web`. El módulo extiende
`res.partner` y `res.config.settings` y utiliza hilos de correo, actividades, plantillas
e informes QWeb. El correo de tareas prefiere un contacto con dirección de correo y, en
su defecto, el cliente; el correo de proyectos utiliza el cliente.

## Restricciones de datos y actualización

Conservar los nombres de modelos, XML IDs, códigos y continuidad de las secuencias. Las
plantillas y los datos propios del módulo se actualizan a las definiciones de Odoo 18;
las copias independientes y los registros de negocio se conservan. No se presupone
ninguna transición de esquema hasta que los datos de producción demuestren su necesidad.

La comparación sobre una copia de producción y la actualización real de producción están
aplazadas a un cambio separado y no forman parte del alcance verificado de la migración
de código. No se ha identificado una transición de datos persistidos o metadatos que
requiera un script de migración local del módulo. Conservar registros es un requisito;
la evidencia histórica existente no demuestra una migración de producción completada.

## Riesgos y puntos abiertos

Antes de actualizar una base de datos de producción, inspeccionar registros sin
compañía, relaciones entre compañías, asignaciones históricas de responsables, addons
hermanos instalados y el conjunto de datos de migración de producción. No reasignar ni
eliminar silenciosamente esos datos. El manifest y el registro de `oca-port` no
demuestran compatibilidad en ejecución.

Estas comprobaciones de producción siguen pendientes según la especificación existente.
La preparación documental no las resuelve ni autoriza operaciones de base de datos.
