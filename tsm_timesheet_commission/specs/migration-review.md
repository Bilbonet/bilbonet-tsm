# Revisión de migración de 15.0 a 18.0

Módulo: `tsm_timesheet_commission`. Rama: `18.0-mig-tsm_timesheet_commission`. Fecha: 1
de noviembre de 2026.

Se completa la migración del módulo de Odoo 15.0 a 18.0, con correcciones de
compatibilidad y de operativa. La comprobación manual de los flujos revisados es
correcta. La suite local del módulo pasa sus nueve pruebas. La instalación limpia del
conjunto se comprueba en CI; la actualización de una copia migrada de 15.0 mantiene su
verificación independiente pendiente. Se incluye la
[edición nativa de líneas pendientes](changes/change-2026-11-01-remove-pending-settlement-lines.md)
de hojas TSM sin facturar, conservando el origen y las reglas de período OCA. El
manifiesto utiliza `account_commission_oca` y omite claves opcionales redundantes.

## Alcance y fuentes

Se revisan manifiesto, modelos, asistente, ACL, vistas, documentación y cambios del
commit de migración `59eec1f`. Se contrastan las APIs con Odoo 18 y los addons activos
`commission_oca`, `account_commission_oca`, `tsm_base`, `tsm_task_timesheet` y
`tsm_time_pack`.

Se consultan las guías OCA para los saltos [16.0], [17.0] y [18.0]. La fuente local de
Odoo 18 y de las dependencias es la referencia para las APIs concretas. El resultado de
las herramientas de migración no demuestra instalación ni funcionamiento.

[16.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-16.0
[17.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-17.0
[18.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0

## Correcciones confirmadas

- Vistas, grupos y ACL apuntan a los XML IDs `commission_oca.*`; se conservan los
  nombres de modelo `commission`, `commission.settlement` y sus mixins.
- Se retiran los grupos del registro de vista heredada de liquidaciones, prohibidos por
  `ir.ui.view._check_groups`. Se restringen sus campos mediante `groups` y se limpia la
  relación anterior al actualizar ese registro.
- Los campos `agent_ids` ocultos en las listas de tarea, partes y bonos declaran una
  subvista con `agent_id`, `commission_id`, `specific_price` y `price_unit`. El widget
  `list.one2many` no carga la vista independiente de agentes; sin campos hijos, la
  especificación de onchange estaba vacía y `RecordSnapshot.diff` podía devolver
  comandos de creación sin agente ni comisión. Se preservan los datos de los agentes
  virtuales, sin relajar campos obligatorios ni alterar permisos. El diagnóstico se
  contrasta con el código del cliente y del serializador Odoo 18; el flujo manual de
  alta, guardado y apertura de comisiones funciona correctamente.
- Los bloqueos de edición de los partes, incluidos Time Pack y descuento de tiempo
  dentro de la tarea, dependen de `any_settled`: permiten trabajar antes de liquidar y
  bloquean cuando existe alguna liquidación no cancelada. Cancelar solo parte de las
  liquidaciones conserva el bloqueo; cancelarlas todas lo libera al recargar la vista.
  Se añade el campo técnico donde faltaba, sin cambiar las restricciones adicionales de
  las vistas base.
- Los campos técnicos de listas usan `column_invisible`. Se corrige `tittle` a `title`
  en el botón de asignación excepcional y se conserva la política de sus grupos.
- Los cálculos de fecha, comisión e importe de líneas de liquidación delegan los
  orígenes ajenos a TSM en la implementación heredada. Antes impedían el cálculo de las
  líneas de facturas de `account_commission_oca`.
- Se prepara y filtra la asignación automática con `tsm_commission_id`, conforme a la
  finalidad explícita del campo. El mixin enviaba la comisión general y anulaba la
  comisión TSM, incluso cuando ambas tenían distintos tipos de liquidación.
- Los vetos de borrado admiten varios agentes y varios partes mediante `mapped` y `any`.
  Se usan métodos `@api.ondelete(at_uninstall=False)`, conservando la protección de
  líneas liquidadas sin bloquear la desinstalación.
- Una fecha de parte vacía produce fecha de comisión vacía en vez de un error de
  atributo. Se conserva la conversión de datetime a fecha sin cambiar zona horaria.
- El cálculo del importe actualiza el precio del registro que está procesando, en vez de
  recalcular repetidamente todo el lote. Se incluyen dependencias de precio específico,
  producto y bono de la línea; el producto sigue el producto del bono o de la comisión.
  Se elimina una dependencia del campo de agentes de tarea consigo mismo.
- Se retiran bloques de código comentado sin efecto, incluido el que producía E501. Se
  aplica el formato exigido por pre-commit.
- Se documentan la comisión TSM, permisos y recorrido de liquidación reales. La lista
  OCA `Invoices Settlements` filtra por `sale_invoice` y no muestra liquidaciones TSM;
  se indica usar `Settlements`. README e índice HTML se regeneran mediante el hook.

## Conservación de comportamiento y datos

Se conservan campos, modelos, XML IDs propios, ACL, relaciones y valores almacenados, la
selección de agentes del cliente, los tipos de tarea abierta/cerrada, los períodos y la
agrupación OCA por compañía y moneda. Se conservan el cálculo bruto/margen y por
porcentaje/tramos, el precio del bono, las horas de cortesía y el producto sin bono. Un
precio específico cero sigue significando precio automático.

No se añade recálculo histórico al cambiar tarifas, porcentajes o tramos. Cualquier
ampliación requiere acordar el efecto sobre líneas existentes y liquidadas. Las
correcciones de dependencias no acreditan que todas las combinaciones de edición estén
funcionalmente verificadas.

El campo `settlement_id` del parte conserva su significado y no se rellena al liquidar
agentes; por tanto los campos de liquidación de tarea basados en esa relación no
representan automáticamente las liquidaciones de todos sus agentes. No se reinterpreta
esa relación ni se reconstruyen enlaces.

No se añade un script de migración de datos sin una transición propia demostrada. Antes
de actualizar una copia migrada deben resolverse los renombrados de addons OCA
(`commission` a `commission_oca`, `account_commission` a `account_commission_oca`) y sus
metadatos y XML IDs mediante el proceso de migración correspondiente. El cambio de
dependencia del manifiesto no realiza esa conversión. Comparar agentes, comisiones,
precios, importes, estados y vínculos de liquidación antes y después.

Los catálogos existentes se conservan; no se ha ejecutado una exportación de
traducciones desde Odoo. No se modifican configuraciones CI ni dependencias externas.

## Comprobaciones técnicas

- Pylint con la configuración del IDE (`/home/bilbonet/odoo18/.vscode/.pylintrc`): se
  reproducen los cuatro diagnósticos aportados en `models/tsm_task.py` y, tras
  corregirlos, el archivo termina sin diagnósticos (salida 0). El dominio llama a
  `_domain_agent_id()` mediante lambda para respetar sobrescrituras posteriores. Los
  tres errores de negocio usan `self.env._`, conservando sus textos traducibles.
- Primera pasada de pre-commit: formato de los seis XML y E501 en código comentado.
- La pasada posterior señala los retornos de los tres métodos que ahora delegan en
  `super()`; se conservan sus retornos, sin silenciar pylint.
- Comprobación estática correcta de sintaxis de 11 ficheros Python (incluidos los
  tests), 6 XML, 15 referencias externas/de modelos y 10 vistas heredadas. Las fuentes
  de los 30 módulos de la cadena de dependencias y sus datos declarados están
  disponibles. Se aplican las arquitecturas al padre con
  `odoo.tools.template_inheritance.apply_inheritance_specs`, sin registro ni BD.
- Esta comprobación no valida el registro ORM, todos los campos y permisos, las
  extensiones hermanas instaladas ni el renderizado del cliente.
- Ajuste de edición hasta la liquidación: comprobados los trece modificadores y
  compuestas estáticamente las cuatro vistas afectadas, con `any_settled` disponible en
  cada lista. Pre-commit sobre los archivos modificados y `git diff --check` correctos.
  El caso de regresión amplía edición previa, cancelación parcial y edición tras
  cancelar todas; no se ha ejecutado en Odoo.
- Se inicializa `specs/` desde los recursos canónicos completos de `odoo-sdd`, como
  archivos editables sin permiso ejecutable. El contrato recoge hechos observados;
  `AGENTS.md` del módulo y el del repositorio incorporan el contexto y la navegación.
- Gate completo correcto (salida 0): `/home/bilbonet/.local/bin/pre-commit` 4.2.0, con
  `run --all-files --show-diff-on-failure --color=always`. Incluye Ruff, formato, XML y
  pylint obligatorio y opcional, sin avisos opcionales pendientes.
- Pasada adicional correcta (salida 0) con
  `run --files <rutas nuevas> --show-diff-on-failure --color=always` sobre los diez
  archivos nuevos de contexto, SDD y tests. `--all-files` solo incluye archivos ya
  versionados; no se añaden archivos al índice para esta comprobación.
- Estructura SDD completa y dos enlaces Markdown relativos comprobados; los ocho
  documentos de contexto y especificación tienen permisos normales sin ejecución.
  `git diff --check` correcto. El diff queda limitado al addon y su entrada de contexto
  en `AGENTS.md` del repositorio, en la rama de migración.

## Edición nativa de líneas de liquidaciones sin facturar

La lista de líneas TSM usa una condición XML de solo lectura basada en el estado: se
edita en `settled` y se bloquea en los demás estados. Se reutilizan la lista
`editable="top"`, la papelera y los permisos OCA existentes. La cabecera y los demás
tipos de liquidación conservan su condición original `can_edit`.

Al guardar la eliminación de una línea se conserva el parte y el agente, se recalcula el
total y la comisión queda pendiente si no conserva otra liquidación activa. El asistente
mantiene la agrupación por fecha y período, sin aplazamientos nuevos. No se añaden
campos, métodos Python, acciones, controles de borrado o traducciones para esta
operación. Se aplican las ACL y el mecanismo ORM habituales de OCA.

La validación estática del ajuste XML se registra en la especificación de edición. La
comprobación manual de edición y borrado nativos es correcta. La suite local pasa sus
nueve pruebas; la actualización de una copia migrada mantiene su verificación
independiente pendiente.

## Pruebas automatizadas y operaciones de base de datos

Se añade `tests/test_timesheet_commission.py` con nueve casos de regresión: comisión TSM
frente a la general y totales; filtrado por el tipo TSM; fecha y tarea opcionales;
borrado por lotes; liquidación, protección, cancelación y no duplicación; espera a
cierre; precio específico, cambio de bono y cortesía; coexistencia de cálculos de
liquidación TSM, de factura y manuales; conservación de agente, comisión y precio
específico en la serialización onchange de las tres vistas afectadas. No se importan
tests desde la raíz del addon.

**Resultado automatizado local:** 9 pruebas del módulo correctas, 0 fallos y 0 errores,
con Odoo 18 y el entorno `odoo18-venv`, en una base temporal aislada. Se ejecuta
`--test-tags=/tsm_timesheet_commission` con actualización exclusiva del módulo en esa
base. No se utiliza la base de trabajo ni una base de producción.

El caso de tarea cerrada materializa los agentes calculados con `env.flush_all()` antes
de consultar sus líneas desde el asistente. Así reproduce el final de la llamada RPC de
alta del parte y comprueba realmente el bloqueo por etapa. La etiqueta del importe pasa
a `Commission Amount` para evitar la duplicidad con el estado de comisión; se conserva
la traducción española y no cambian los cálculos.

El pipeline de GitHub ejecuta por separado instalación limpia y la batería conjunta con
OCB 18.0. El resultado del commit final se comprueba antes de integrar el PR. La
actualización de datos reales migrados de 15.0 continúa pendiente. Las pruebas internas
de coexistencia usan registros en memoria y no acreditan el recorrido completo de
facturación ni la generación PDF.

## Pruebas manuales y aprobación

Comprobaciones manuales de la operativa realizadas con resultado correcto. La ejecución
automatizada se registra en el apartado anterior; la actualización de una copia migrada
no queda acreditada por las comprobaciones manuales.

- [x] **Configuración:** asignar a un agente comisiones general y TSM distintas → se
      guardan ambas; la TSM permite producto, porcentaje/tramos y estado de tarea.
- [x] **Asignación:** añadir un parte de horas desde una tarea con agentes del cliente,
      guardar y abrir su botón de comisiones → aparecen los agentes admitidos por su
      tipo TSM y se usa su comisión TSM, aunque la general sea otra.
- [x] **Edición y regeneración:** editar agentes con el botón y regenerarlos desde la
      tarea → se recupera la configuración del cliente y se respetan los bloqueos de
      líneas liquidadas.
- [x] **Precios:** registrar horas con bono, sin bono y de cortesía → se aplican precio
      de bono, precio de producto y cero respectivamente. Comprobar también precio
      específico distinto de cero y su vuelta al automático mediante cero.
- [x] **Totales:** usar varios agentes, cambiar horas/bono y retirar un agente sin
      liquidar → importes por agente, parte y tarea coinciden con el cálculo esperado.
- [x] **Vistas:** abrir formulario de tarea, listas de partes, bono, contacto, tipos de
      comisión y liquidaciones → los controles funcionan y no aparecen columnas técnicas
      vacías.
- [x] **Fecha opcional:** crear un parte sin fecha y un parte sin tarea → se guardan sin
      error; una línea sin tarea no se incluye en la liquidación.
- [x] **Liquidación:** elegir Timesheet, agentes y fecha de corte → aparecen solo líneas
      elegibles del período; repetir no duplica comisiones ya liquidadas.
- [x] **Tarea cerrada:** liquidar una comisión configurada para cierre con la tarea
      abierta y después cerrada → solo se liquida tras el cierre.
- [x] **Borrado por lotes:** borrar varios agentes y partes no liquidados → funciona;
      intentar con alguno liquidado → se rechaza; cancelar la liquidación lo libera.
- [x] **Convivencia:** liquidar comisiones de facturas de venta y TSM, y revisar una
      liquidación manual → fecha, comisión e importes de cada origen son correctos.
- [x] **Factura:** facturar una liquidación TSM de agente externo → proveedor, producto,
      diario, moneda, total y estado coinciden; revisar el PDF si se utiliza.
- [x] **Permisos:** comparar usuario TSM, gestor de comisiones y contabilidad → se
      conservan accesos y restricciones previstos; comprobar además lectura de datos de
      otros usuarios, compañías y tareas privadas con los permisos reales.

**Resultado de la verificación manual funcional:** correcto. La ejecución automatizada
tiene su evidencia separada. La actualización de una copia migrada de 15.0 no se ha
comprobado específicamente.

## Límites heredados

El módulo no define reglas de registro de agentes. El dominio del selector y los campos
de solo lectura de las vistas no son una barrera RPC ni demuestran aislamiento por tarea
o compañía. No se rediseñan estos permisos. Las reglas y ACL OCA de liquidaciones son
independientes de las de TSM. Debe verificarse la exposición real con los usuarios de
destino antes de considerar el módulo listo para producción.
