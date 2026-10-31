# Contrato del módulo

Este documento describe hechos comprobados en el código de `tsm_time_pack` para Odoo 18.
No acredita aprobación histórica de requisitos ni verificación funcional. Consulta
[la revisión de migración](migration-review.md) para conocer qué se ha comprobado y qué
falta por validar.

## Propósito y límites

Gestionar bonos de horas de soporte de clientes y consumirlos mediante partes de
`tsm.task.timesheet`. Integra productos de servicio, pedidos de venta, notificaciones,
correo e informes PDF. Los proyectos y tareas son modelos TSM; no son proyectos ni
partes analíticos del estándar de Odoo.

## Actores y permisos

- Los usuarios TSM tienen ACL de lectura y escritura; los gestores TSM también pueden
  crear y borrar bonos.
- La regla de lectura permite al usuario ver los bonos de los que es responsable,
  aquellos que sigue y los visibles para todos los empleados. Los gestores tienen una
  regla sin restricción. Esa regla de usuario no restringe escritura.
- Crear una venta requiere acceso de escritura al bono y pertenecer al grupo de gestores
  de ventas, como exige el botón existente. Un bono con venta vinculada rechaza otra
  creación.
- El archivo y la restauración conservan la restricción heredada de gestores de ventas,
  aunque sus botones se muestran a gestores TSM. La restricción sobre `active` también
  puede actuar al crear un bono.
- No hay reglas de aislamiento por compañía. `can_edit` solo controla edición visual, y
  los filtros por cliente tampoco impiden escrituras ORM distintas.

## Conceptos y flujos principales

- `tsm.time.pack`: código único, título opcional, cliente, responsable, compañía,
  fechas, privacidad, descripción HTML, saldo de horas y configuración de venta.
- `product.template.service_time_pack`: marca los servicios que pueden seleccionarse
  como producto de un bono.
- `tsm.task.timesheet.timepack_id`: vincula un parte al bono. `discount_time` distingue
  tiempo consumido y tiempo de cortesía.
- Si el alta de un parte con tarea no aporta bono, se busca el primer bono activo
  accesible del cliente exacto de la tarea, según `date_start, id desc`. No se filtra
  por vencimiento, saldo, compañía o contacto comercial superior. Se respetan bonos
  explícitos y valores por defecto del contexto. También se admiten partes sin tarea,
  conforme a la dependencia.
- La cantidad de venta debe ser positiva y al cambiarla se actualizan las horas
  contratadas. Estas también se pueden editar por separado. El descuento admite valores
  de hasta 100; el código no impone un mínimo.
- El botón de venta crea un pedido con una línea a partir del producto, cantidad, precio
  y descuento; añade una nota de origen y opcionalmente lo confirma. El importe sin
  impuestos se muestra en moneda de compañía usando la fecha inicial del bono. El precio
  de la línea no incorpora conversión propia entre monedas.

## Cálculos y numeración

- Tiempo total: suma de las horas de todos los partes vinculados.
- Consumo: suma de los partes con `discount_time` marcado.
- Cortesía: diferencia entre tiempo total y consumo.
- Saldo: horas contratadas menos consumo; puede ser negativo.
- Progreso: porcentaje del consumo sobre las horas contratadas; es cero cuando estas no
  son positivas. El cálculo almacenado solicita una notificación de peligro al usuario
  actual desde el 90%; no registra un aviso único ni envía automáticamente un correo.
- El alta y la copia asignan códigos de secuencia. Las copias no incluyen partes ni
  venta vinculada. El nombre mostrado conserva `[código] título`.

## Interfaz e integraciones

Menús Mis bonos y Todos los bonos, con lista, formulario, búsqueda y kanban. Los
formularios de tareas y las vistas de partes permiten seleccionar y abrir bonos. Se
extiende la ficha de producto para configurar servicios.

El correo carga cliente, remitente, resumen de horas y un informe detallado. El adjunto
reutiliza la acción del informe detallado y su `print_report_name`, igual que la
impresión desde el menú. El nombre se configura en esa única acción. Existen informes de
bono resumido y detallado, y extensiones de informes de tareas y proyectos. El detallado
incluye descripciones de tareas y subtotal de horas por tarea. Los cálculos y parte de
los informes leen con elevación de permisos.

## Restricciones de datos y actualización

Se conservan modelos, campos actuales, XML IDs existentes, relaciones, códigos,
secuencia, precisión decimal y políticas `noupdate`. El origen inmediato es
`15.0.1.0.1`, que ya incorpora el renombrado de `contrated_hours` a `contracted_hours`.
No se crea un script nuevo de datos sin una transición demostrada. Una base anterior
necesita revisar ese renombrado antes del salto.

La plantilla de correo no es `noupdate`: la actualización puede reemplazar
personalizaciones guardadas en la base. Deben revisarse junto con adjuntos, seguidores,
actividades y reglas en una copia migrada.

## Riesgos y puntos abiertos

Faltan instalación, actualización de una copia migrada y verificación funcional. La
privacidad de los bonos no se propaga a partes ni compañías. Deben revisarse las
lecturas elevadas y el contenido enviado a clientes. La política de archivo, la
cobertura de permisos y la venta en varias compañías/monedas requieren comprobación; no
se redefine su política comercial durante esta migración.
