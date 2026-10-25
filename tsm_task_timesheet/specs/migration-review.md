# Revisión de migración 15.0 → 18.0

## Alcance y estado

Mantenimiento de `tsm_task_timesheet` en `18.0-mig-tsm_task_timesheet` para restaurar
compatibilidad con Odoo 18 conservando el comportamiento existente. El manifiesto
anterior al port (`6964d8b`) declara `15.0.1.0.0`; el actual declara `18.0.1.0.0`. El
port automatizado consta en `a9a8de2`.

La petición autoriza revisar y corregir problemas confirmados e inicializar el contexto
del harness. Este documento registra alcance técnico y evidencia; no atribuye aprobación
de requisitos nuevos ni validación funcional. No se reconstruyen especificaciones
históricas de funcionalidades.

## Correcciones revisadas

| Área                    | Defecto confirmado                                                              | Corrección                                                                                               |
| ----------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Ajustes                 | El nodo `div[data-key='tsm_base']` ya no existe en el padre.                    | Heredar `app[name='tsm_base']` e insertar `block/setting`.                                               |
| Interfaz                | `boolean_button` y `res.users.image_small` no existen en web/base 18.           | Estado visible en el botón existente y avatar `image_128`.                                               |
| Calendario              | La conversión de una fecha vacía provoca una excepción.                         | Sumar a datetime directamente y devolver False sin inicio.                                               |
| Stop                    | Restar una fecha vacía provoca una excepción de Python.                         | Validar todos los inicios antes de modificar las duraciones.                                             |
| Título                  | El campo obligatorio podía llegar vacío a la inserción al ocultarlo por grupos. | Calcular antes de insertar con `precompute=True`, usar `/` como respaldo y conservar títulos explícitos. |
| Etiquetas               | La restricción accedía a campos de varios registros como singleton.             | Validar por etiqueta, conservando la exclusión del predeterminado activo.                                |
| Inicio rápido           | Una zona horaria ausente rompe `pytz.timezone`; Ruff detecta UP031.             | Usar `fields.Datetime.context_timestamp` y formato de fecha en f-string.                                 |
| Borrado                 | El veto en `unlink` también se aplica durante la desinstalación.                | `@api.ondelete(at_uninstall=False)`, con el mismo veto ordinario.                                        |
| Formato y documentación | XML sin formatear y README que describe líneas analíticas.                      | Aplicar hooks y regenerar README desde sus fragmentos.                                                   |

Se conserva el cambio previo del manifiesto que retira `application`, `installable` y
`preloadable`. No se cambian dependencias, licencia, autoría, ACL, modelos, campos, XML
IDs ni el registro inicial `noupdate`.

## Verificación técnica

Entorno de validación: Odoo Community 18.0 del workspace, Python 3.12.15 y PostgreSQL
14.24. Se utilizaron bases temporales independientes, sin datos de cliente ni
demostración, y un directorio de datos propio. Los tests HTTP se limitaron a 127.0.0.1.

- Pre-commit compartido 4.2.0:
  `pre-commit run --all-files --show-diff-on-failure --color=always` correcto,
  incluyendo todos los archivos nuevos. Se revisaron el formato aplicado y la
  documentación regenerada; no se desactivaron comprobaciones.
- Instalación limpia de `tsm_task_timesheet` y `tsm_task_material`, con sus
  dependencias: correcta. Resultado final de Odoo: **0 fallos y 0 errores de 45 tests**:
  13 de `tsm_base`, 12 de `tsm_task_material` y 20 de `tsm_task_timesheet`.
- Actualización en una base de pruebas 18.0 con los tres módulos instalados: **32 tests
  correctos**, correspondientes a Partes y Materiales. Esto no equivale a actualizar una
  base desde Odoo 15.
- Suite Hoot `@tsm_task_timesheet/task_quick_create`, ejecutada con Chrome for Testing
  156.0.8078.47: **4 tests y 14 aserciones correctos**. Comprueba los campos vacíos, la
  ausencia individual de título/cliente y el guardado previo al RPC con un ID
  persistido.
- XML, referencias de herencia, esquemas de lista de Odoo 18, dominios y enlaces de
  especificaciones revisados. Los nuevos assets se convierten con el transpilador de
  Odoo 18. `git diff --check` correcto.

La ejecución confirmó y permitió corregir los datos de prueba: compañía y privacidad
explícitas del usuario/tareas, vaciado de Many2one mediante recordsets en `Form`, reloj
congelado para los valores por defecto y modelos Mail requeridos por Hoot. El test de
impuestos de Materiales ahora prepara país fiscal y grupo de impuestos sin depender de
datos de demostración. También se oculta el título del formulario de parte cuando su
opción está desactivada.

Comandos de referencia, usando una base y directorio de datos temporales:

```bash
python server/odoo-bin -c /dev/null \
  --db_host=/var/run/postgresql --db_user=bilbonet -d <test_database> \
  --addons-path=server/addons,_ext/bilbonet/bilbonet-tsm \
  --data-dir=<test_data_directory> --max-cron-threads=0 --workers=0 \
  --without-demo=all --test-enable \
  --test-tags=/tsm_task_timesheet,/tsm_base,/tsm_task_material \
  -i tsm_task_timesheet,tsm_task_material --stop-after-init
```

La suite de navegador se ejecuta con el servidor HTTP habilitado, un navegador indicado
mediante `ODOO_BROWSER_BIN`, `web` actualizado en esa base temporal y:

```text
--test-tags=/web:WebSuite.test_unit_desktop[@tsm_task_timesheet/task_quick_create]
```

El contraste de código incluye defaults y precálculo del ORM, el controlador de creación
rápida de Kanban y el hook nativo de botones. Las guías OCA de migración a [16.0],
[17.0] y [18.0] se usaron como referencia; no se ejecutaron comandos de migración de
bases de cliente.

[16.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-16.0
[17.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-17.0
[18.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0

## Pruebas manuales y aprobación

Prueba cada caso y marca los que funcionen. Una casilla marcada confirma que la
comprobación está realizada y es correcta; no requiere notas adicionales.

- [ ] **Ajustes:** activar título o etiqueta y guardar → la opción se conserva;
      descartar una edición posterior → no se guardan sus cambios.
- [ ] **Partes sin título ni etiqueta:** desactivar ambas opciones y añadir un parte
      desde una tarea → ninguno de esos campos se muestra y el parte se guarda.
- [ ] **Varios partes sin opciones:** añadir dos partes desde la tarea con ambas
      opciones desactivadas → se guardan ambos y el total suma sus duraciones.
- [ ] **Títulos:** registrar un parte con título manual y modificar su duración → el
      título se conserva.
- [ ] **Etiquetas:** activar etiquetas y registrar un parte → aparece la predeterminada;
      elegir otra → el título calculado corresponde a esa etiqueta.
- [ ] **Comenzar con formulario vacío:** en Kanban, abrir la creación rápida y pulsar
      Comenzar sin título ni cliente → aparecen los campos pendientes, sin error RPC ni
      creación de tarea o parte.
- [ ] **Comenzar sin cliente:** introducir solo el título y pulsar Comenzar → se
      solicita el cliente y se conserva lo escrito.
- [ ] **Comenzar sin título:** seleccionar solo el cliente y pulsar Comenzar → se
      solicita el título y se conserva el cliente.
- [ ] **Completar y comenzar:** completar los campos tras un aviso y pulsar Comenzar →
      se guarda una tarea, se añade un parte de duración cero y se abre su formulario en
      edición.
- [ ] **Inicio rápido:** iniciar una tarea con y sin zona horaria configurada → se crea
      un parte de duración cero y el sello temporal esperado.
- [ ] **Stop y total:** detener un parte con inicio conocido → se calcula el tiempo
      transcurrido y se actualiza el total de horas de la tarea.
- [ ] **Calendario:** abrir partes con distintas duraciones → sus finales corresponden a
      inicio más duración; un parte sin inicio no rompe la vista.
- [ ] **Kanban y formulario:** abrir un parte → avatar, estado y botón para abrir/cerrar
      la tarea se muestran y funcionan con confirmación.
- [ ] **Filtros y análisis:** comprobar Hoy, semana y mes y abrir los pivots por
      usuario/tarea → selección y totales corresponden a los partes de prueba.
- [ ] **Proyecto:** abrir sus partes desde el botón del proyecto → se muestran los
      partes del proyecto seleccionado.
- [ ] **Cierre:** cerrar desde un parte de una tarea con otro parte de duración cero →
      se rechaza; asignar duración y repetir → se cierra.
- [ ] **Archivo:** archivar una tarea cerrada con un parte de duración cero → se
      rechaza; asignar duración y repetir → se archiva y puede restaurarse.
- [ ] **Borrado:** eliminar una tarea con partes → se rechaza; retirar sus partes y
      repetir → se elimina.

**Conformidad del usuario:** autoriza el cierre de la migración condicionado a
pre-commit y tests correctos. No se han confirmado individualmente todas las
comprobaciones manuales; sus casillas conservan el estado real.

## Pruebas automatizadas y base de datos

**Decisión:** ejecución solicitada expresamente para el cierre, el commit y el PR.
**Resultado:** 45 tests Python y 4 tests Hoot correctos; ver la evidencia técnica.

Se ha comprobado creación por formulario y ORM, valores por defecto, selección
proyecto/tarea, validación de combinaciones incompatibles, propagación al mover la
tarea, fechas vacías, Stop, totales, etiquetas por lote, título sin opciones, zona
horaria, Comenzar desde Kanban y salvaguardas de borrado/archivo.

Permanecen fuera de la evidencia obtenida:

- Actualización sobre una copia de datos migrados desde 15.0: conservación de partes,
  relaciones, etiquetas, grupos, XML IDs y datos archivados.
- Desinstalación en una base desechable.
- Revisión completa de acceso con distintas compañías y partes de tareas privadas.
- Las comprobaciones manuales no marcadas. `Form` y las pruebas de dominios no
  sustituyen la verificación de todos los desplegables y pantallas en navegador.

## Límites y riesgos heredados

Los partes tienen ACL amplias para usuarios TSM y no tienen reglas propias de registros.
No se garantiza aislamiento por propietario, privacidad de tarea ni compañía; el filtro
de «Mis partes» no lo demuestra. No se ha cambiado esa política sin un requisito
confirmado. Las reglas de `tsm_base` tampoco bastan por sí solas para acreditar
protección de estos registros.

La validación al cambiar etapa es un onchange, no una garantía general de servidor para
cierre mediante ORM. La exclusión de etiqueta predeterminada tampoco garantiza
concurrencia. Son límites observados, no funciones añadidas.

No se identifica un cambio de esquema o identificadores que requiera un script de datos
por estas correcciones. No se ha comprobado la actualización de una base real. La
validación funcional queda limitada a las pruebas descritas, sin extenderla a los
escenarios pendientes.
