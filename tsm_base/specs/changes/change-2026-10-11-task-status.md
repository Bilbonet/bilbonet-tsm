---
id: change-2026-10-11-task-status
title: "Sustituir el indicador Kanban por el estado de la tarea"
status: verified
module: tsm_base
created: 2026-10-11
---

# Especificación del cambio

## Cambio y límites

Sustituir el indicador `kanban_state` de `tsm.task` por una selección almacenada y
editable llamada `task_status`, con etiqueta fuente `Task Status` y traducción «Estado
de la tarea». Permite clasificar visualmente el trabajo con las opciones y colores de
`project.project.last_update_status` de Odoo 18.

| Valor       | Etiqueta fuente | Traducción española | Color del selector / barra    |
| ----------- | --------------- | ------------------- | ----------------------------- |
| `on_track`  | On Track        | A tiempo            | Verde / `success`             |
| `at_risk`   | At Risk         | En riesgo           | Naranja / `warning`           |
| `off_track` | Off Track       | Atrasado            | Rojo / `danger`               |
| `on_hold`   | On Hold         | En espera           | Azul / `info`                 |
| `to_define` | Set Status      | Establecer estado   | Neutro                        |
| `done`      | Done            | Hecho               | Morado (`primary`) / `purple` |

Las traducciones corresponden al catálogo español local de Odoo 18. Las etiquetas son
fijas y no dependen de la etapa. Se mantiene la semántica del indicador de proyectos: a
tiempo, en riesgo, atrasado, en espera, sin definir o realizado.

El valor inicial es `to_define`. Debe mostrarse como estado actual sin clasificación,
conservando su etiqueta, pero queda excluido del menú de selección manual. El usuario
puede elegir los cinco estados efectivos.

`done` significa tarea realizada; deja de significar preparada para pasar a la siguiente
etapa. Cambiar el indicador no modifica por sí mismo la etapa, su condición de cierre,
el archivado, las fechas ni otros datos. Tampoco introduce restricciones de edición.

Sustituir el selector del formulario y del kanban y adaptar la barra de distribución a
los nuevos estados y colores. Aplicar `opacity-50` al contenido de la tarjeta cuando
`task_status == 'done'`. Recuperar su apariencia normal al seleccionar otro estado,
manteniendo operativos la apertura, edición y controles según los permisos existentes.
Este efecto no se aplica al listado ni al formulario.

Conservar la regla que permite archivar únicamente tareas en etapas cerradas. Al
archivarlas, restablecer la prioridad a `0` y `task_status` a `to_define`. Al
desarchivarlas, mantener ese valor sin recuperar la clasificación anterior ni exigir
otra inmediata. Conservar la presentación existente de las tareas archivadas; el
reinicio del indicador elimina la atenuación asociada a `done`.

Registrar los cambios del indicador, incluido su reinicio al archivar cuando cambie el
valor, mediante el seguimiento estándar del chatter.

Retirar `kanban_state`, `kanban_state_label`, su cálculo, `legend_normal`,
`legend_blocked` y `legend_done` de la etapa, sus campos relacionados en la tarea y las
referencias asociadas. Conservar la prioridad y `legend_priority`.

Inicializar las tareas existentes, activas y archivadas, con `to_define`, sin
equivalencias con los indicadores antiguos ni conservación de sus etiquetas
personalizadas. Preservar sus restantes datos, mensajes, adjuntos, actividades,
seguidores, permisos, privacidad y separación entre compañías.

Quedan fuera los estados y reglas de `project.task`, las actualizaciones de proyecto,
nuevos modelos de seguimiento, informes, porcentajes de progreso y cambios en addons
hermanos. La implementación está autorizada; las pruebas de Odoo, instalaciones,
actualizaciones y operaciones de base de datos requieren autorización posterior.

## Criterios de aceptación

- [x] **CA-01.** Las tareas nuevas sin clasificación explícita comienzan en `to_define`;
      las copias conservan el reinicio del indicador y comienzan también sin definir.
- [x] **CA-02.** Formulario y kanban muestran el estado actual con su etiqueta y color.
      El menú ofrece únicamente los cinco estados efectivos, con etiquetas fijas y
      traducciones correspondientes.
- [x] **CA-03.** La barra del kanban distribuye los registros por `task_status`,
      incluyendo los registros sin clasificación con presentación neutra y los colores
      de referencia para los estados efectivos.
- [x] **CA-04.** Una tarea activa marcada `done` permanece en su etapa y sigue activa y
      editable. Su contenido kanban se muestra al 50 % de opacidad; al cambiar, por
      ejemplo, a `on_hold`, recupera la apariencia normal. Sus controles siguen
      funcionando según permisos.
- [x] **CA-05.** El cambio de indicador no altera automáticamente fechas, prioridad,
      etapa ni condición de cierre, y no introduce atenuación en listado o formulario.
- [x] **CA-06.** Archivar en una etapa abierta sigue siendo rechazado, incluso con
      indicador `done`. En una etapa cerrada, el archivado restablece prioridad e
      indicador; desarchivar mantiene `to_define`. Las operaciones por lotes conservan
      las salvaguardas existentes.
- [x] **CA-07.** Los cambios efectivos de `task_status`, incluido el reinicio al
      archivar, aparecen mediante seguimiento estándar en el chatter. No se crean
      actualizaciones de proyecto ni mensajes personalizados adicionales.
- [x] **CA-08.** Las etapas dejan de ofrecer etiquetas personalizadas del indicador. Se
      conservan su descripción, cierre, plegado y `legend_priority`.
- [x] **CA-09.** Al introducir el nuevo campo en una base existente, todas las tareas
      parten de `to_define`, independientemente del antiguo indicador. Se conservan los
      restantes registros y relaciones; una actualización posterior no reinicia
      clasificaciones nuevas ya guardadas.
- [x] **CA-10.** La sustitución respeta los permisos de lectura y escritura, la
      privacidad y las compañías permitidas, también con usuarios no administradores.
      Funciona sin requerir Odoo Project y sin referencias operativas a los campos
      retirados dentro del alcance del módulo.

## Impacto en Odoo

### Modelos y seguimiento

Incorporar una selección normal, obligatoria, con `default='to_define'`, `copy=False` y
`tracking=True`. Retirar los campos y cálculo antiguos en `tsm.task` y las tres leyendas
en `tsm.task.type`. Adaptar el reinicio del archivado conservando sus salvaguardas.

### Interfaz y assets

El selector local extiende `StateSelectionField` de `web`, configura colores y filtra
opciones. Su registro, plantilla y estilos se incorporan a `web.assets_backend` desde el
manifest. Se mantienen las dependencias existentes, sin añadir `project`.

La adaptación obtiene la etiqueta actual de la selección completa y filtra `to_define`
únicamente del menú. La plantilla conserva la etiqueta como tooltip también en lectura.
Se mantiene la escritura estándar del componente, con una salvaguarda de solo lectura
que también cubre sus comandos.

Los estilos locales reproducen las variables del selector de referencia. La barra
mantiene los tokens de la vista de proyectos; los registros sin clasificación aparecen
en su segmento neutro residual. Se añade un estilo para `bg-purple` limitado al kanban
de TSM, usando el color CSS `purple` que emplea el filtro de columnas de `web`. El
selector de `done` conserva `$primary`; son referencias distintas. Los colores efectivos
forman parte de la comprobación manual confirmada. La opacidad usa la utilidad
`opacity-50` de `web`, limitada al contenido de las tarjetas con
`task_status == 'done'`.

### Datos y compatibilidad

La fuente de Odoo 18 contempla inicializar columnas nuevas mediante su valor por
defecto. Se usa este mecanismo estándar, sin renombrar el campo antiguo ni convertir sus
valores. La verificación manual de CA-09 confirma su inicialización y la conservación de
datos y clasificaciones posteriores dentro del entorno comprobado. No se requiere una
tabla de conversión ni se presupone la necesidad de un script local de migración.

La retirada rompe referencias externas a los campos antiguos. El inventario previo
identificó referencias en modelos, vistas, `i18n/es.po`, `i18n/tsm_base.pot` y la prueba
de archivado de `tests/test_tsm_base.py`. La implementación retira esas referencias y
los textos de ayuda de las etapas sobre bloqueo o preparación para la etapa siguiente;
adapta la prueba al nuevo indicador. No se encontraron referencias al indicador en los
datos XML ni en los informes del módulo.

`readme/USAGE.md` describe los estados nuevos, la opacidad, el seguimiento y el reinicio
al archivar. La documentación se mantiene en inglés y los documentos generados siguen el
flujo habitual del repositorio.

No aparecen referencias directas a esos campos en los addons hermanos de Odoo 15
consultados: `tsm_task_material`, `tsm_task_timesheet`, `tsm_tech_assets`,
`tsm_time_pack` y `tsm_timesheet_commission`. Esto no demuestra su compatibilidad en
ejecución ni cubre personalizaciones almacenadas en una base de datos. Su revisión para
un despliegue conjunto queda fuera de este cambio.

### Documentación SDD

Mantener esta spec durante su desarrollo. Conservar la
[spec de migración](change-2026-09-05-migrate-tsm-base-15-to-18.md) en `verified`: su
escenario del indicador antiguo documenta el comportamiento anterior y su evidencia no
verifica esta sustitución. Este cambio sustituye únicamente el indicador y su reinicio;
conserva las reglas de etapas y archivado.

El contrato y el contexto del módulo reflejan la sustitución aprobada, sin reabrir
requisitos ajenos. Se conservan los requisitos, criterios y evidencia de la migración
existente.

## Verificación

### Plan

Las comprobaciones manuales corresponden al usuario. El agente no ejecutará pruebas de
Odoo, actualizaciones ni operaciones de base de datos en esta revisión:

- Comprobar CA-01 a CA-05 en formulario y kanban, incluyendo creación rápida, copia,
  etiquetas en español, colores, distribución y controles de una tarjeta atenuada.
- Comprobar CA-06 y CA-07 mediante archivado permitido y rechazado, restauración,
  operaciones por lotes y seguimiento del chatter una vez finalizada la transacción.
  Incluir el archivado desde un estado efectivo y desde `to_define`.
- Revisar la retirada de referencias y la configuración de etapas para CA-08.
- Separar instalación nueva y actualización de una copia con tareas activas y archivadas
  para CA-09; incluir los tres valores antiguos, comparar datos y relaciones conservados
  y repetir la actualización con clasificaciones nuevas.
- Comprobar CA-10 con usuarios asignados, responsables, usuarios con acceso de lectura y
  compañías permitidas y ajenas, en un entorno sin `project`.

### Resultados

Verificación manual completada por el usuario: CA-01 a CA-10 aparecen marcados como
comprobados y se ha confirmado expresamente que todas las verificaciones están
realizadas. Estas marcas constituyen la evidencia manual aportada; no se adjunta un
registro detallado por operación ni se identifica aquí la base de datos utilizada. No se
han comunicado incidencias pendientes dentro de estos criterios. La confirmación previa
tras `Ctrl+F5` resolvió la presentación del selector en kanban.

| Criterio | Resultado manual confirmado                                                                                                | Evidencia complementaria disponible                                                                                 |
| -------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| CA-01    | Comprobado: valor inicial y reinicio en copias.                                                                            | La suite verifica `to_define` al crear y copiar, y códigos únicos.                                                  |
| CA-02    | Comprobado: selector en formulario y kanban, etiquetas, colores y cinco opciones efectivas.                                | Revisión estática del widget y catálogo español; la confirmación previa del kanban es coherente con este resultado. |
| CA-03    | Comprobado: distribución de la barra, segmento neutro y colores.                                                           | Configuración de la vista y estilos contrastada con el core.                                                        |
| CA-04    | Comprobado: `done` mantiene actividad, etapa, edición y controles; atenuación y recuperación visual.                       | La suite comprueba que el indicador no modifica etapa ni actividad.                                                 |
| CA-05    | Comprobado: independencia de fechas, prioridad, etapa y cierre; listado y formulario sin atenuación.                       | La suite compara los campos antes y después de cada estado efectivo.                                                |
| CA-06    | Comprobado: rechazo en etapa abierta, archivado permitido, reinicios, restauración y lotes.                                | Regresiones de archivado individual y por lotes superadas.                                                          |
| CA-07    | Comprobado: seguimiento estándar de cambios y reinicios sin mensajes adicionales ni actualizaciones de proyecto.           | La prueba de tracking comprueba cambios, reinicio y ausencia de mensajes por escrituras sin cambios.                |
| CA-08    | Comprobado: retirada de leyendas antiguas y conservación de descripción, cierre, plegado y prioridad.                      | Inventario de modelos, vistas y referencias retiradas.                                                              |
| CA-09    | Comprobado: inicialización en una base existente, conservación de datos y relaciones y segunda actualización sin reinicio. | Lectura de la inicialización estándar de columnas de Odoo; no sustituye la comprobación manual.                     |
| CA-10    | Comprobado: permisos, privacidad, compañías, usuarios no administradores e independencia de `project`.                     | Revisión de dependencias y ausencia de referencias operativas a campos retirados.                                   |

Implementación disponible, contrastada por lectura:

- `models/tsm_task.py` declara la selección con valor inicial `to_define`, `copy=False`
  y seguimiento estándar; conserva el ajuste existente de archivado y cambia su reinicio
  al nuevo campo. La versión del addon es `18.0.1.1.0`.
- Las vistas usan el selector local y la barra de distribución nueva; el contenido
  kanban aplica `opacity-50` solo para `done`. Se conserva la presentación del título
  archivado y la leyenda de prioridad de la etapa.
- El selector y sus estilos están en `static/src/fields/task_status_selection/`, sin
  importar recursos de `project`.
- Las traducciones incluyen el campo y las seis opciones nuevas; se retiraron las
  entradas obsoletas. La búsqueda de los campos retirados no devuelve referencias
  operativas fuera de `specs/`.
- Se adaptaron las pruebas existentes de archivado y copia y se prepararon regresiones
  de independencia respecto a etapas y fechas, archivado por lotes y seguimiento del
  reinicio.

La ejecución aportada de la suite actual obtuvo 13 pruebas correctas y tres avisos de
obsolescencia del core de correo de Odoo. La preparación de ajustes fija
`tags_in_task=False` explícitamente, sin depender de `ir.default`, y comprueba tanto
activar como desactivar el ajuste sin cambiar tareas archivadas. La lógica del ajuste
conserva su filtro de tareas activas y compañías autorizadas. Las regresiones de
proyectos con tareas ocultas invalidan la relación poblada como administrador antes de
leerla con el usuario limitado. La preparación evita ahora invitaciones del usuario y
notificaciones de asignación innecesarias mediante contextos acotados; su repetición
pendiente se documenta en la especificación de migración. La prueba explícita de
tracking conserva el comportamiento del chatter. El agente no ha ejecutado pruebas ni
accedido a una base de datos.

Comprobaciones realizadas sin cargar Odoo ni acceder a una base de datos:

- Análisis de sintaxis con `ast.parse` de los cuatro archivos Python afectados y lectura
  del manifest con `ast.literal_eval`.
- Parseo XML con `lxml` de las dos vistas y la plantilla del selector; esto no valida su
  carga en Odoo ni su renderizado.
- Parseo del catálogo español con Babel y comprobación de existencia de los tres assets
  declarados. El catálogo POT anterior se ha retirado.
- Comprobación de sintaxis JavaScript con `node --input-type=module --check` y revisión
  de espacios con `git diff --check`.
- Regeneración de `README.rst` e `index.html` desde los fragmentos mediante
  `oca-gen-addon-readme`, usando la revisión de maintainer-tools configurada en el
  repositorio y sin commit.

Referencias técnicas contrastadas en el workspace Odoo 18:

- `server/addons/project/models/project_project.py`: opciones, predeterminado y creación
  de `project.update` en la escritura del indicador; esta última lógica queda excluida
  de la adaptación.
- `server/addons/project/static/src/components/project_state_selection/`,
  `static/src/utils/project_utils.js`, `static/src/scss/project_widgets.scss` y
  `views/project_project_views.xml`: filtrado del menú, colores y barra de referencia;
  `server/addons/project/i18n/es.po`: traducciones españolas.
- `server/addons/web/static/src/views/fields/state_selection/` y
  `server/addons/web/static/src/views/fields/formatters.js`: componentes reutilizables y
  cálculo de la etiqueta de selección.
- `server/addons/project/views/project_task_views.xml`: uso de `opacity-50` en el
  contenido kanban; se adapta solo el efecto visual para `task_status`.
- `server/odoo/fields.py`, `update_db_notnull`, y `server/odoo/models.py`,
  `_init_column`: inicialización estándar de la columna nueva con su valor por defecto
  para las filas existentes.
- `server/addons/mail/models/mail_thread.py`: seguimiento estándar de escrituras de
  campos con `tracking`.

La lectura no demuestra por sí misma el comportamiento en ejecución. La evidencia
histórica de la migración no se traslada a esta spec: el cierre funcional se apoya en la
confirmación manual de sus diez criterios y en los resultados de la suite aportados. Se
establece `status: verified` para este alcance. La migración de producción y la revisión
de personalizaciones de cada base mantienen sus límites independientes.

El agente no ha ejecutado pruebas de Odoo, instalaciones, actualizaciones de módulos ni
operaciones de base de datos.

Gate local del repositorio ejecutado en `18.0-mig-tsm_base`:

```text
~/.local/bin/pre-commit run --all-files --show-diff-on-failure --color=always
```

Resultado: correcto, código de salida `0`, incluidos los assets nuevos, ESLint,
traducciones, comprobaciones de Odoo, Ruff y pylint obligatorio. La primera ejecución
detectó que la atribución del manifest no contenía el autor independiente `Bilbonet`; se
conservan ambas atribuciones como `Bilbonet, Jesus Ramiro`. Se corrigieron también los
avisos JavaScript del comentario `@odoo-module` y del orden de imports. Los hooks
regeneraron la documentación desde los fragmentos y formatearon los documentos SDD; sus
cambios se revisaron. Los ajustes de autoría, comentarios, imports y formato conservan
el comportamiento verificado y no requieren repetir pruebas funcionales.

## Ajustes pendientes

<!-- Bandeja de entrada para notas aún no incorporadas. Trasladarlas no implica
aprobarlas, implementarlas ni verificarlas. -->
