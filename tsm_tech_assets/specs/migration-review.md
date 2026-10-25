# Revisión de migración 15.0 → 18.0

## Alcance y estado

Revisión de `tsm_tech_assets` en `18.0-mig-tsm_tech_assets`. El manifiesto anterior al
port (`0f01ec1`) declara `15.0.1.0.0`; el port automatizado `2e6155a` cambia a
`18.0.1.0.0`. La petición autoriza corregir problemas confirmados y preparar el módulo
para el harness conservando su comportamiento.

Se mantienen los cambios previos del manifiesto, icono y formato de vistas. Este
documento registra mantenimiento técnico y evidencia; no reconstruye requisitos
históricos ni acredita compatibilidad funcional sin pruebas.

## Correcciones confirmadas

| Área             | Defecto                                                                                                          | Adaptación                                                                                                                         |
| ---------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Contador         | `search(count=True)` no existe en Odoo 18.                                                                       | Usar `search_count`, incluyendo archivadas con `active_test=False`, sin elevar permisos. Invalidar el cálculo al cambiar vínculos. |
| Edición          | `self.user_id.id` falla cuando hay varios responsables.                                                          | Calcular por activo con dependencias de responsable y usuario del contexto. Conservar gerente o responsable.                       |
| Compañía         | `_company_default_get` emite una advertencia de deprecación.                                                     | Usar `env.company`, equivalente en el core 18.                                                                                     |
| Correo           | El compositor rechaza `default_res_id`.                                                                          | Usar `default_res_ids`.                                                                                                            |
| Adjunto          | `mail.template.report_template` y `report_name` ya no existen.                                                   | Configurar `report_template_ids` y reutilizar el nombre existente del informe.                                                     |
| Seguidores       | El asistente de `tsm_base` limita los modelos admitidos y excluye los activos; la acción existente no hace nada. | Extender su lista desde este addon con `tsm.tech.asset`, manteniendo los modelos base y los permisos del usuario.                  |
| Kanban           | La tarjeta `card` llama a `kanban_image`, disponible solo en modo antiguo, y usa `image_small`, eliminado.       | Avatar nativo de usuario, de solo lectura, y menú `menu` con abrir, archivar/restaurar y borrar.                                   |
| Directivas       | `t-raw` y `type="edit"` están obsoletos.                                                                         | `t-out` para el contador numérico y `type="open"`.                                                                                 |
| Lista y acciones | Campos técnicos usan invisibilidad de celda; atributos `Help` y `view_type` son antiguos.                        | Ocultar columnas técnicas, usar `help` y retirar la clave de acción obsoleta.                                                      |
| Prioridad        | El filtro usa enteros 1 y 2 para una selección con cadenas `0` y `1`.                                            | Filtrar la prioridad existente `1`.                                                                                                |
| Calidad          | Ruff detecta E501 en el resumen del manifiesto.                                                                  | Dividir el literal sin cambiar el texto. Normalizar el formato con los hooks del repositorio.                                      |

## Comportamiento final aceptado

- Los tipos se crean y editan por su nombre directamente en la lista de configuración.
- En la tarea se conserva una tarjeta compacta por elemento, mostrando solo el nombre.
  Pulsar la tarjeta abre el formulario en ventana; el triángulo diagonal ampliado abre
  la ficha completa; la X roja desvincula sin eliminar el activo.
- Los iconos se disponen verticalmente sin posiciones absolutas. El enlace de
  desvinculación incluye `role="button"`, corrigiendo el aviso de accesibilidad del
  validador de vistas de Odoo 18.
- El mensaje de la restricción SQL conserva su literal, que Odoo traduce
  automáticamente. La declaración de clase no utiliza `self.env` ni traducción
  anticipada.
- Estos ajustes de interfaz usan únicamente la vista y los mecanismos existentes, sin
  añadir campos, JavaScript ni hojas de estilo propias.

Se conservan dependencias, metadatos de autoría/licencia, modelos, campos, XML IDs,
tabla relacional, ACL, reglas y secuencia `noupdate`. No se añaden restricciones de
cliente, compañía ni de escritura de campos.

## Verificación técnica

- Contraste con el core local Odoo 18: ORM, compañía, compositor, plantillas, Kanban,
  avatar, relación Many2many y vista heredada de `tsm_base`.
- Primera ejecución de pre-commit compartido 4.2.0 sobre todo el repositorio: fallo E501
  confirmado; los demás hooks pasan, incluidos los opcionales de Pylint. Su salida no
  detecta los bloqueos funcionales encontrados al leer el core.
- Gate final: pre-commit compartido 4.2.0, ejecutado después de incluir todos los
  archivos nuevos en el índice con
  `pre-commit run --all-files --show-diff-on-failure --color=always`. Los resultados se
  revisan antes del commit y del PR, incluidos los avisos opcionales. Las copias de las
  plantillas SDD conservan permisos documentales `0644`. Resultado: todos los hooks
  aplicables correctos, sin avisos, incluidos Pylint obligatorio y opcional.
- Sintaxis Python correcta en 8 archivos y XML bien formado en 6. Se revisan los
  esquemas RNG de Odoo 18 para las listas y búsquedas, los controles compactos, el
  selector nativo y sus referencias. Son comprobaciones estáticas; no cargan el módulo.
- El README se regenera mediante el hook del repositorio desde sus fragmentos en inglés.
  El contexto estable y el contrato recogen exclusivamente las opciones finales.
- Ficheros del manifiesto, ancla heredada `date_deadline`, referencias al diseño,
  formato de papel y asistente base, expresiones de dominios/modificadores y cinco
  enlaces documentales relativos comprobados. Cuatro vistas pasan sus esquemas RNG (dos
  listas y dos búsquedas). `git diff --check` correcto.

El contador separa su caché por usuario y compañías permitidas, conforme a
`Environment.cache_key` del core 18, para conservar el respeto a reglas de tareas al
cambiar el contexto. Las ACL y reglas no se modifican.

Se consultaron las guías oficiales OCA de migración a [16.0], [17.0] y [18.0] para
cubrir los saltos intermedios; las APIs se contrastaron con el código local.

[16.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-16.0
[17.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-17.0
[18.0]: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0

## Pruebas manuales y aprobación

Marca cada casilla solo tras realizar la comprobación y obtener el resultado esperado.
Una casilla marcada es evidencia suficiente; las notas son opcionales.

- [x] **Apertura en ventana:** pulsar una tarjeta abre el formulario en ventana.
- [x] **Ficha completa:** pulsar el triángulo abre el formulario completo.
- [x] **Desvinculación:** pulsar la X roja retira el elemento de la tarea.
- [x] **Revisión final:** el usuario confirma que su revisión está realizada y es
      correcta, y autoriza consolidar la documentación, hacer commit y abrir el PR.

Las tres acciones fueron confirmadas expresamente como correctas durante la revisión. La
conformidad final no acredita por sí sola cada variante del plan adicional siguiente; se
conserva sin marcar aquello cuya ejecución individual no consta.

- [ ] **Alta y copia:** crear y duplicar un activo → códigos diferentes, título de copia
      y ausencia de vínculos heredados a tareas.
- [ ] **Historial:** vincular tareas activas y archivadas → el contador y la acción
      muestran las tareas relacionadas que el usuario puede consultar.
- [ ] **Formulario:** comparar gerente, responsable y otro usuario autorizado → se
      conserva la edición visual prevista de cliente, responsable, fecha y privacidad.
- [ ] **Kanban:** abrir tarjetas con distintos responsables → avatares y actividades
      visibles; el menú permite abrir, archivar/restaurar y borrar según permisos.
- [ ] **Tarea:** añadir y quitar activos desde su formulario → se conserva la relación
      recíproca y el filtro de cliente. Copiar la tarea no copia activos.
- [ ] **Búsqueda:** marcar prioridad y usar Destacados, Mis activos y filtros de
      actividades → aparecen los registros correspondientes; comprobar también
      archivados.
- [ ] **Seguidores:** asignar y retirar seguidores con el asistente → cambia el acceso
      según privacidad y las reglas existentes.
- [ ] **Correo con notas:** abrir Enviar por correo → destinatario, plantilla y notas
      del activo seleccionado son correctos; cancelar no envía ningún mensaje.
- [ ] **Correo con adjunto:** elegir la plantilla de informe adjunto → aparece el PDF
      del activo con nombre `(código)_título.pdf`, sustituyendo espacios por guiones.
- [ ] **Informes:** imprimir informe resumido y detallado → se ven datos, notas HTML y
      tareas; revisar ambos con usuarios que tengan acceso limitado a tareas.

**Conformidad del usuario:** recibida el 25 de octubre de 2026 para el resultado
revisado y la publicación del PR. No se atribuye ejecución a las comprobaciones
adicionales sin marcar ni a los tests automatizados.

## Pruebas automatizadas y datos

**Ejecución:** no se han ejecutado tests ni operaciones de base de datos locales. El
workflow `tests` del PR ejecuta la suite sobre OCB 18.0 en una base aislada de CI. El
resultado del commit vigente se consulta en las
[verificaciones del PR](https://github.com/Bilbonet/bilbonet-tsm/pull/8/checks). La
suite incluye diez casos de `tsm_tech_assets`, con cobertura para alta por lotes,
compañía activa, edición con responsables distintos y cambio de usuario, contadores con
archivados, acceso restringido y cambios de vínculos, copia, inicialización del
compositor, asignación y retirada de seguidores, rechazo de modelos no admitidos y
generación/nombre de adjuntos. El renderizador PDF se simula en el test de adjuntos: no
valida el motor PDF ni el contenido de los informes.

La revisión estática de los datos de prueba incluye una etapa cerrada explícita para la
tarea archivada, conforme a la restricción de archivo de `tsm_base`.

La primera ejecución de CI registró 55 tests con un error en el caso de compañía
predeterminada: la compañía nueva del test no tenía secuencia aplicable y el código
quedaba vacío. Ese caso usa ahora un código explícito para aislar el valor por defecto
de compañía; la numeración se comprueba en el caso de alta por lotes. No se altera la
secuencia productiva ni su política `noupdate`.

El usuario ha actualizado el módulo en su base y ha realizado su revisión de interfaz.
El agente no ha ejecutado instalaciones, actualizaciones ni operaciones de base de datos
locales. La CI instala dependencias, inicializa su base y ejecuta tests; no equivale a
actualizar una base de cliente. Quedan sin validar el renderizado QWeb/PDF real y el
envío de correo. La actualización de una copia migrada desde Odoo 15 debe comprobar por
separado activos, notas, compañías, responsables, códigos, secuencia, tipos, tareas
archivadas, relaciones, seguidores, actividades, reglas y plantillas. No se identifica
una transición propia de datos que justifique un script adicional; la lectura de fuentes
no demuestra la conservación de una base real.

## Límites heredados

Las ACL y reglas no garantizan aislamiento por compañía. `can_edit` es una ayuda de
interfaz; los dominios de cliente tampoco restringen escrituras ORM. El informe
detallado puede encontrar tareas relacionadas sin acceso para el usuario. Son límites
observados que requieren comprobar permisos y, si se quiere cambiarlos, acordar una
política funcional aparte.
