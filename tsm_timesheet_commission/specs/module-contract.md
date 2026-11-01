# Contrato del módulo

## Propósito

Vincular los partes de tareas TSM con las comisiones y liquidaciones OCA en Odoo 18.
Este contrato recoge el comportamiento observado en el código. La verificación de la
operativa y sus límites se documentan en `migration-review.md`.

## Alcance y límites

El módulo amplía `tsm.task`, `tsm.task.timesheet`, `res.partner`, `commission`,
`commission.settlement`, sus líneas y el asistente `commission.make.settle`. Define
`tsm.task.timesheet.agent`. Depende de `tsm_time_pack` y `account_commission_oca`; las
facturas de comisiones las gestiona OCA. No incluye una migración de base de datos de
15.0 a 18.0.

## Flujos e invariantes observados

- Los agentes del cliente se proponen en sus partes con la comisión específica
  `tsm_commission_id`, siempre que su tipo sea vacío o `timesheet`. Cada parte admite
  como máximo una línea por agente, según la restricción heredada de OCA.
- Se puede regenerar la asignación desde la tarea. La operación reemplaza los agentes;
  las líneas liquidadas quedan protegidas contra su borrado.
- El importe aplica el cálculo OCA (porcentaje fijo o tramos, sobre bruto o margen) a
  las horas decimales y al precio por hora. Con bono se usa su precio si consume horas y
  cero para horas de cortesía; sin bono se usa el producto de la comisión. Un precio
  específico distinto de cero prevalece. Cero significa precio automático.
- El asistente selecciona líneas no liquidadas anteriores al inicio del período indicado
  y agrupa por agente, período, compañía y moneda. Una comisión para tarea cerrada
  espera al cierre; una línea sin tarea no se liquida.
- Cancelar una liquidación libera sus líneas. Una liquidación no cancelada impide borrar
  sus agentes y sus partes; la restricción de integridad protege cambios de agente e
  importe liquidados. La desinstalación no aplica los vetos de borrado.
- Los importes de agentes alimentan los totales del parte y de la tarea. Las líneas de
  liquidación TSM conservan origen, cliente y tarea; deben coexistir con líneas de
  facturas y manuales sin anular sus cálculos.

- Las líneas de una hoja TSM en estado `settled` permiten edición y borrado nativos
  según los permisos OCA. Guardar la eliminación conserva el parte y el agente y deja la
  comisión pendiente si no tiene otra liquidación activa. Los demás estados dejan la
  lista en solo lectura. Se mantienen la cabecera y los otros tipos de liquidación bajo
  su control habitual. Véase
  [la especificación de edición](changes/change-2026-11-01-remove-pending-settlement-lines.md).

## Actores y permisos

Los usuarios TSM tienen CRUD en agentes de partes y lectura de comisiones y tramos. No
hay reglas de registro propias de agentes. El dominio de selección limita en la interfaz
a agentes no gestores a su contacto, pero no impone esa restricción por RPC. Las reglas
OCA de liquidaciones y los permisos TSM de tareas/bonos son independientes. No se
acredita aislamiento de privacidad o compañía por el dominio de una vista.

## Vistas y entradas

Configuración de agente en contactos; parámetros TSM en tipos de comisión; edición
mediante el botón de agentes de los partes de tarea; totales y búsqueda por agente;
columnas de origen TSM en liquidaciones. Las listas de partes y bonos conservan los
bloqueos de edición mientras algún agente tenga una liquidación no cancelada. Asignar un
agente por sí solo no bloquea esos campos. Cancelar todas las liquidaciones de sus
agentes libera la edición. Véase
[la especificación de edición](changes/change-2026-11-01-timesheet-edit-until-settlement.md).

## Restricciones de datos y actualización

Conservar modelos, campos, XML IDs propios y relaciones. Los XML IDs externos de
comisiones pertenecen a `commission_oca`. Una base migrada debe haber resuelto por
separado los renombrados de addons OCA y sus metadatos antes de actualizar el módulo. El
campo `settlement_id` del parte mantiene su significado previo: no se rellena al
liquidar sus agentes ni se usa para reconstruir sus liquidaciones.

## Riesgos y puntos abiertos

La actualización de configuración de tarifas, porcentajes o tramos no se convierte en un
mecanismo de recálculo histórico. Su efecto sobre líneas existentes, especialmente
liquidadas, requiere validación y una decisión funcional antes de ampliarlo. La
instalación limpia y la actualización de una copia migrada mantienen su validación
independiente pendiente. El resultado manual de la operativa se registra en
`migration-review.md`.
