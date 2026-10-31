# Revisión de migración de 15.0 a 18.0

Módulo: `tsm_time_pack`. Rama de trabajo: `18.0-mig-tsm_time_pack`. Fecha de revisión:
31 de octubre de 2026.

La petición autoriza revisar y corregir la migración conservando el comportamiento. Esta
revisión no constituye aprobación de funciones nuevas ni validación funcional. La
implementación cuenta con conformidad para commit y publicación de la rama; su
comprobación funcional en Odoo sigue pendiente.

## Alcance y fuentes

Se revisan manifiesto, modelos, seguridad, datos, correo, vistas, informes, dependencias
directas e historial del renombrado de horas contratadas. Se conserva el cambio previo
del usuario en el manifiesto.

Las guías OCA para [16.0], [17.0] y [18.0] cubren los saltos intermedios. Las APIs se
contrastan con la fuente local de Odoo 18, `tsm_base`, `tsm_task_timesheet`,
`tsm_task_material` y `web_notify`.

[16.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-16.0
[17.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-17.0
[18.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0

## Correcciones confirmadas

- La herencia de producto usa `type`; `detailed_type` ya no está en el formulario padre.
  El kanban usa el avatar nativo, sin `kanban_image` ni `image_small`.
- Los menús declaran los modos `list,form,kanban`. Mis bonos vincula la búsqueda con
  `search_view_id`, y los campos técnicos de listas usan `column_invisible`.
- El nombre mostrado se calcula con `_compute_display_name`; la compañía por defecto usa
  `env.company`, el progreso usa `aggregator="avg"` y la edición visual depende del
  usuario del contexto.
- Cantidad y descuento validan conjuntos de bonos. La copia admite varios registros y
  asigna códigos distintos, sin partes ni pedidos heredados.
- El alta de partes admite tarea omitida o predeterminada por contexto y respeta bonos
  explícitos o predeterminados. Se conserva la elección del primer bono activo accesible
  del cliente, sin añadir criterios de caducidad o saldo.
- El compositor usa `default_res_ids`; la plantilla usa `report_template_ids` y
  reutiliza la acción del informe detallado. El adjunto adopta su `print_report_name`,
  sin acción ni plantilla envolvente propias para el correo. El asunto usa el nombre
  disponible de compañía en lugar del campo inexistente `comercial`.
- La nota del pedido usa `message_post_with_source`. La creación comprueba en servidor
  el acceso de escritura, el grupo de gestores de ventas y la ausencia de pedido,
  conforme a las restricciones que ya expresaba el botón.
- El importe sin impuestos se convierte a la moneda de compañía que declara el campo
  monetario; antes se convertía a la tarifa del cliente y se etiquetaba con otra moneda.
  Sus dependencias incluyen importes, moneda, compañía y fecha.
- Los informes de bonos admiten notas vacías y muestran subtotales por tarea. El
  detallado no intenta imprimir una tarea inexistente de un parte sin tarea. Las
  cabeceras y leyendas de informes comprueban si hay algún parte con bono, sin depender
  del último parte. Se corrige un elemento HTML `di` en el proyecto. Las alineaciones
  usan las clases Bootstrap 5 correspondientes.
- Las horas del correo usan el formateador nativo `float_time`, incluido el saldo
  negativo; la fórmula anterior podía producir minutos incorrectos o `60`.
- Se aplican los ajustes de formato y los errores Ruff detectados por pre-commit.

## Compatibilidad y datos

El origen inmediato anterior al commit de migración es `15.0.1.0.1`. El commit `2e4a120`
ya había renombrado `contrated_hours` a `contracted_hours` mediante un script para
actualizar desde `15.0.1.0.0`. La eliminación del directorio de migración antiguo no
demuestra que una base concreta esté preparada. Antes de actualizar una copia migrada,
comprobar la columna y sus valores. Una base que aún conserve solo `contrated_hours`
requiere resolver ese cambio de datos por separado. No se añade una dependencia ni un
script nuevo sin una transición adicional demostrada.

Se conservan nombres de modelo/campo, XML IDs existentes, códigos, secuencia,
relaciones, precisión, ACL, reglas y datos `noupdate`. La plantilla de correo se
actualiza porque no es `noupdate`; revisar personalizaciones antes de aplicar el cambio
a una copia migrada. No se han exportado ni regenerado los catálogos completos; se
sincronizan únicamente los tres mensajes parametrizados afectados por los ajustes de
traducción, conservando el texto español.

## Comprobaciones técnicas

- Primera pasada de `pre-commit run --all-files --show-diff-on-failure --color=always`:
  detectó formato XML y dos errores Ruff `UP031` en el antiguo `name_get`.
- Comprobación estática correcta: 8 ficheros Python, 11 XML, 43 referencias XML, 8
  arquitecturas heredadas y fuentes disponibles de 27 módulos de la cadena de
  dependencias. Las rutas declaradas en los manifiestos existen.
- Estructura SDD completa copiada de los recursos canónicos, enlaces locales comprobados
  y diff revisado. Los documentos copiados usan permisos normales de lectura/escritura;
  se retira el permiso ejecutable heredado de las plantillas.
- Gate completo: `/home/bilbonet/.local/bin/pre-commit` 4.2.0, con el comando
  `run --all-files --show-diff-on-failure --color=always`, resultado correcto (salida
  0). Incluye Ruff, formato XML y pylint obligatorio y opcional; sin advertencias
  opcionales pendientes.
- Ficheros nuevos: pasada adicional
  `pre-commit run --files <rutas nuevas> --show-diff-on-failure --color=always`,
  resultado correcto (salida 0). `--all-files` solo incluye los archivos ya versionados;
  esta pasada cubre también los 10 ficheros nuevos de contexto, SDD y tests sin
  añadirlos al índice.
- `git diff --check`: correcto. Cambios limitados al módulo y su entrada en `AGENTS.md`
  del repositorio. Rama de trabajo: `18.0-mig-tsm_time_pack`.
- Pylint con la configuración del IDE (`/home/bilbonet/odoo18/.vscode/.pylintrc`): se
  reprodujeron las 16 advertencias aportadas y el fichero corregido termina sin
  diagnósticos (salida 0). Esa configuración habilita comprobaciones de traducción
  adicionales respecto de los hooks del repositorio. Se usa `env._` con parámetros y se
  conserva el texto estático de la restricción SQL, que Odoo traduce al presentar el
  error.
- Los dos diagnósticos Pyright sobre `_convert_to_write` se resuelven en código
  materializando `dict(record._cache)`, sin alterar la preparación de ventas.
  `RecordCache` es un mapping válido para la implementación, pero la anotación exige un
  diccionario. No hay CLI Pyright disponible: queda pendiente confirmar el resultado al
  refrescar el analizador del IDE.
- Comprobación estática de los tres mensajes parametrizados: presentes en código, POT y
  catálogo español, con interpolación válida en ambos idiomas.

Las comprobaciones estáticas de herencia aplican las especificaciones al padre con el
mecanismo de Odoo, sin registro ni base de datos. No validan todos los campos, permisos,
combinaciones de extensiones instaladas ni renderizado del cliente.

## Pruebas automatizadas y operaciones de base de datos

Se añade cobertura de regresión en `tests/test_tsm_time_pack.py` para alta,
restricciones y copia por lotes, compañía y nombres mostrados, partes sin tarea,
defaults, selección automática, recálculos de horas, ventas y confirmación,
restricciones de venta, moneda, compositor, asunto, adjuntos y HTML de informes.

**Ejecución:** tests de Odoo no solicitados expresamente y no ejecutados. La generación
PDF se simula en el caso del compositor y el adjunto; ese caso no acredita el motor PDF.
Las pruebas HTML tampoco acreditan impresión PDF. No se han instalado ni actualizado
módulos, creado/inicializado bases, ejecutado migraciones ni enviado correos. La
presencia de dependencias en disco no demuestra que estén instaladas y operativas.

Cuando se autorice, ejecutar la suite específica en una base Odoo 18 aislada y comprobar
por separado instalación limpia y actualización de una copia migrada. Comparar horas,
partes, clientes, compañías, responsables, códigos, vínculos, seguidores, actividades y
personalizaciones antes y después de la actualización.

## Pruebas manuales y aprobación

Marcar cada casilla solo después de realizar la comprobación y obtener el resultado
esperado. Una casilla marcada basta; las notas son opcionales.

- [ ] **Producto:** abrir un servicio y marcar Timepack → queda seleccionable en un
      bono; al cambiar a otro tipo se desmarca.
- [ ] **Alta y copia:** crear dos bonos y duplicarlos → códigos distintos, sin partes ni
      pedidos copiados y compañía activa correcta.
- [ ] **Vistas:** abrir Mis bonos y Todos los bonos en lista, formulario y kanban →
      búsqueda, avatares, saldos y navegación funcionan.
- [ ] **Selección de bono:** crear partes desde tarea y vistas de partes → se asigna el
      bono activo del cliente cuando no se indica otro; una selección manual se
      conserva. Comprobar también un parte sin tarea.
- [ ] **Horas:** cargar horas consumidas y de cortesía, modificar duración, cambiar bono
      y borrar un parte → se actualizan consumo, cortesía y saldo.
- [ ] **Aviso:** consumir el 90% o más → aparece el aviso previsto; superar las horas
      contratadas muestra saldo negativo sin impedir el registro.
- [ ] **Ventas:** crear pedido con y sin autoconfirmación → cantidades, precios,
      descuento, cliente, origen y estado coinciden con lo introducido. Intentar repetir
      la operación → no se crea otro pedido.
- [ ] **Moneda:** revisar una venta con tarifa en otra moneda → el total del bono
      corresponde a la moneda de compañía y cambia al editar el pedido.
- [ ] **Permisos:** comparar usuario TSM, gestor TSM y gestor de ventas, responsable y
      seguidor → se comprueban lectura, edición, creación, venta, archivo y restauración
      con las reglas heredadas.
- [ ] **Correo:** abrir el compositor → cliente, asunto, remitente, horas y adjunto
      detallado son correctos; el nombre del PDF coincide con el definido en la acción
      del informe detallado. Cancelar no envía.
- [ ] **Informes:** imprimir resumen y detalle con notas vacías/HTML y varias tareas →
      no hay error, las horas y subtotales son correctos. Revisar además informes de
      tarea y proyecto, con partes con y sin bono.

**Conformidad del usuario:** recibida para el resultado revisado y para realizar commit
y subir la rama. No acredita la ejecución de las pruebas sin marcar ni compatibilidad
funcional completa.

## Límites heredados pendientes de evaluación funcional

Las ACL y reglas no aíslan compañías ni propagan privacidad del bono a partes. Hay
lecturas elevadas en cálculos e informes. La restricción de archivo utiliza un grupo
distinto del que muestra sus botones y puede intervenir en el alta. La selección
automática no considera vencimiento ni saldo y la venta no convierte el precio unitario
entre la moneda del bono y la tarifa del cliente. Se conservan estas políticas
observadas; cualquier redefinición requiere acordar su comportamiento. Debe evaluarse su
adecuación al uso real antes de producción.
