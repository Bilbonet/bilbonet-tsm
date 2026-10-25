# Contrato del módulo

Este contrato describe hechos observados en el código de `tsm_tech_assets` para Odoo 18.
No acredita aprobación histórica de requisitos ni validación funcional. Las correcciones
de compatibilidad y su evidencia se recogen en
[migration-review.md](migration-review.md).

## Propósito

Registrar activos técnicos de clientes, sus notas técnicas y de configuración, y el
historial de tareas TSM relacionadas.

## Alcance y límites

Incluye tipos de activo, prioridades, archivo/restauración, seguidores y actividades,
correo y dos informes PDF. Extiende las tareas de `tsm_base`. No implementa inventario,
amortizaciones, contabilidad ni Odoo Project.

## Actores y permisos

Los usuarios TSM tienen ACL de lectura, creación, escritura y borrado de activos. Las
reglas ordinarias permiten leer y escribir activos públicos o seguidos; otra regla
permite crear, escribir y borrar los asignados al usuario. Estas reglas de grupo se
combinan con OR por operación, no como restricciones acumulativas. Los gerentes tienen
una regla de acceso irrestricto.

Los tipos son legibles por usuarios TSM y administrables por gerentes. `can_edit` limita
visualmente ciertos campos al gerente o responsable; no establece restricciones
adicionales de escritura en el servidor.

## Conceptos principales del dominio

Un activo tiene cliente, responsable, tipo, código único y notas HTML. Puede ser privado
para seguidores o visible a empleados dentro de la política de acceso TSM. Se relaciona
con tareas mediante una Many2many recíproca.

## Flujos principales de negocio

Crear un activo asigna código mediante secuencia cuando se recibe `/`. Desde una tarea
pueden vincularse activos filtrados por la jerarquía del cliente. El activo permite
consultar tareas relacionadas, incluidas archivadas, según los permisos del usuario.
Copiar una tarea o un activo no copia sus vínculos. Copiar un activo genera otro código
y añade `(copy)` al título.

El usuario puede archivar/restaurar, gestionar actividades y seguidores, componer correo
y generar un informe resumido o detallado con tareas.

## Modelos principales

- `tsm.tech.asset`: ficha del activo, privacidad, notas y tareas relacionadas.
- `tsm.tech.asset.type`: clasificación de activos.
- `tsm.task`: incorpora `asset_ids` al modelo de `tsm_base`.

## Invariantes estables de negocio

El código es obligatorio y único globalmente, no por compañía. La tabla
`tsm_task_tsm_tech_asset_rel` y sus columnas `tsm_task_id` y `tsm_tech_asset_id`
representan ambos lados de la misma relación. Los vínculos están excluidos de las copias
en ambos modelos.

## Vistas, acciones y menús

Menú de activos dentro de TSM con lista, formulario, Kanban y actividades; configuración
de tipos bajo el menú de configuración TSM. El formulario de tarea muestra tarjetas de
activos. El botón de tareas del activo abre sus tareas relacionadas. Se conserva el
identificador histórico `tsm_tech_assets_tree_view` aunque su arquitectura usa `<list>`.

Los tipos se mantienen por su nombre directamente en una lista editable. En la tarea,
las tarjetas compactas muestran únicamente el nombre del elemento: pulsar la tarjeta
abre el formulario en ventana, el triángulo diagonal abre la ficha completa en la vista
principal y la X roja desvincula sin borrar el activo. El botón de ficha completa usa el
guardado nativo de la tarea antes de navegar. Las acciones permanecen separadas en una
columna lateral, sin posiciones absolutas ni campos auxiliares.

## Integraciones

Dependencia directa: `tsm_base`. Reutiliza sus grupos, formulario de tarea, asistente de
seguidores, diseño QWeb y formato de papel. Correo y actividades proceden de los mixins
de Mail; no hay integración externa propia. El módulo añade `tsm.tech.asset` a la lista
de modelos admitidos por el asistente compartido de seguidores, manteniendo sus modelos
originales.

Existen una plantilla con notas y otra con informe adjunto. El asistente usa
`default_res_ids`; el adjunto procede de `report_template_ids` y toma el nombre de
`ir.actions.report.print_report_name`.

## Restricciones de datos y actualización

Conservar modelos, campos, XML IDs, tabla relacional, ACL y datos `noupdate` de
secuencia y reglas. Estas correcciones no identifican una transición propia de datos
almacenados que justifique añadir scripts de migración. La migración de la base y de las
estructuras generales de Mail sigue pendiente de comprobar en una copia de datos
procedentes de Odoo 15.

## Riesgos y áreas sensibles

Las notas pueden contener datos sensibles. Las reglas no imponen aislamiento por
compañía, aunque el activo guarda la compañía activa al crearse. El dominio de cliente
de la vista no garantiza coherencia desde ORM o RPC. El informe detallado lee tareas que
pueden tener permisos distintos del activo; su renderizado debe comprobarse con usuarios
de acceso restringido.

## Puntos abiertos

La política deseada de aislamiento por compañía y de correspondencia obligatoria entre
cliente de tarea y activo no se ha definido adicionalmente. Se conserva la
implementación existente; estos límites no autorizan nuevas restricciones. La
compatibilidad funcional y la conservación de datos quedan limitadas a las
comprobaciones realmente registradas en la revisión de migración.
