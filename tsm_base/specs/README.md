# Especificaciones del módulo

Esta carpeta contiene la fuente de verdad funcional del módulo. En ella se documenta qué
debe hacer el módulo, por qué existe cada comportamiento y qué decisiones condicionan su
implementación.

## Navegación del módulo

- [Contrato del módulo](module-contract.md): contexto estable, invariantes y
  restricciones de conservación.
- [Especificaciones de cambios](changes/README.md): instrucciones para cambios
  funcionales y su ciclo de estados.
- [Migración de tsm_base de Odoo 15 a Odoo 18](changes/change-2026-09-05-migrate-tsm-base-15-to-18.md):
  alcance acordado, escenarios, criterios y evidencia histórica; conserva status:
  verified. La comparación sobre una copia de producción y la actualización real de
  producción están aplazadas fuera de ese alcance.
- [Estado de la tarea](changes/change-2026-10-11-task-status.md): sustitución del
  indicador Kanban por `task_status`, con `status: verified` tras la confirmación manual
  de sus diez criterios; clasificación visual, seguimiento estándar y conservación de
  las reglas de etapas y archivado.
- [Decisiones arquitectónicas](decisions/README.md): cuándo documentar una elección
  duradera.
- Plantillas editables de [cambio](templates/change.md) y
  [decisión](templates/decision.md).

La especificación de migración conserva su estructura detallada y su texto original en
inglés. Sigue siendo válida; al actualizarla, redacta en español las partes afectadas y
conserva identificadores, estados, requisitos y evidencia. La evidencia histórica no
equivale a una nueva verificación del módulo.

## Preparación y evolución del método

La skill general `odoo-sdd` inicializa esta estructura en un módulo ya creado o adapta
una estructura existente al método compartido. Los generadores de módulos de cada
versión se encargan del esqueleto del addon.

Las plantillas canónicas están en el harness general, bajo
`.bbn/odoo-harness/skills/odoo-sdd/assets/specs/`. Los documentos del módulo son copias
editables propias. Actualizar el harness no los modifica automáticamente: aplica
`odoo-sdd` cuando quieras adaptarlos.

La adaptación conserva los requisitos, decisiones, identificadores, estados y evidencia
de verificación. Las diferencias que afecten a requisitos aprobados necesitan una
decisión explícita; actualizar el método no constituye una nueva aprobación ni una
verificación funcional.

Cuando la petición solo inicializa o adapta la documentación SDD de un addon existente
al método compartido, aplica la excepción de odoo-git-workflow: actualiza la
documentación directamente en la rama principal de la versión Odoo del repositorio, tras
comprobar la rama y el trabajo pendiente. No requiere una rama nueva, change spec, PR ni
ciclo de aprobación funcional. La petición autoriza esta adaptación documental; los
cambios quedan sin commit ni push salvo solicitud expresa. Si el usuario indica
expresamente que la preparación debe quedar en la rama actual, esa instrucción
prevalece: comprueba cuál es, conserva los cambios pendientes y no cambies de rama,
aunque contenga trabajo funcional. Conserva el trabajo ajeno y señala cualquier
impedimento sin moverlo ni descartarlo. Esta excepción no incluye crear el addon ni
definir cambios funcionales o modificar código.

SDD define el comportamiento antes de implementarlo. El ciclo TDD de escribir una prueba
que falle, implementar y refactorizar no se exige por este método. Las pruebas,
instalaciones, actualizaciones y operaciones de base de datos se ejecutan según la
autorización y política del workspace activo.

## Idioma de las especificaciones

Redacta en español el contrato, las especificaciones de cambios, los escenarios, los
criterios de aceptación, los planes y resultados de verificación y las decisiones
arquitectónicas, también al actualizar una especificación en inglés. El código y la
documentación del addon se redactan en inglés, incluidos los comentarios, docstrings,
textos fuente de Odoo, AGENTS.md y fragmentos readme/. Conserva los nombres técnicos,
rutas, claves del frontmatter y estados como status: draft o approved.

## Tipos de especificación

- module-contract.md documenta el contexto estable del módulo: propósito, límites,
  actores, conceptos de dominio, invariantes, integraciones y restricciones.
- Las change specs de changes/ definen el comportamiento de una funcionalidad nueva o
  modificada intencionadamente. Cada cambio funcional coherente se mantiene en una misma
  change spec, con profundidad proporcional a su impacto.
- Las decisiones de decisions/ documentan elecciones arquitectónicas relevantes,
  alternativas y consecuencias de compatibilidad. No sustituyen los requisitos
  funcionales.
- Los ficheros de templates/ son puntos de partida para crear nuevas change specs y
  decisiones. Deben copiarse antes de rellenarse.

## Qué debe guardarse en changes/

Una change spec es un acuerdo sobre los requisitos funcionales y la implementación de un
cambio coherente. No es un historial de commits de Git, una lista de tareas técnicas ni
una copia de todas las conversaciones con la IA.

Crea o actualiza una change spec cuando cambie el comportamiento previsto, por ejemplo:

- añadir una nueva capacidad para usuarios o integraciones;
- cambiar un flujo de negocio o un resultado observable;
- cambiar permisos, límites de seguridad o reglas de datos;
- cambiar un contrato de integración, una migración o una restricción de compatibilidad;
- corregir un defecto cambiando intencionadamente el comportamiento descrito por la
  especificación actual.

No crees una nueva change spec para cambios de formato, documentación aislada,
refactorizaciones internas que mantengan el comportamiento o cambios únicamente de
tests. Si una corrección restaura un comportamiento que ya está descrito en una spec
existente, actualiza o referencia esa spec en lugar de crear un registro duplicado.

Una corrección sin acuerdo funcional previo no queda exenta por llamarse «bugfix»: si el
comportamiento esperado no está definido, documenta el acuerdo necesario con el núcleo
breve o ampliado según su riesgo.

## Especificación vigente

Mantén cada spec como una definición coherente del acuerdo vigente. La conversación
sirve para afinar ese acuerdo: incorpora sus conclusiones como requisitos claros, sin
transcribir respuestas ni atribuir opiniones al usuario. Cuando una decisión cambie de
forma acordada, reescribe los requisitos, criterios, escenarios y plan afectados,
elimina contradicciones y retira propuestas descartadas. No añadas una corrección al
final dejando vigente el texto anterior. Los cambios de alcance aprobado siguen las
reglas de aprobación del método.

No añadas bitácoras de conversación, cronologías de cambios de opinión ni secciones de
historial con una fecha por modificación. Conserva los metadatos mínimos de la
plantilla, incluida created, y los identificadores y estados útiles. El historial de
edición puede consultarse en Git cuando esté disponible.

Conserva la evidencia de verificación necesaria para distinguir lo comprobado de lo
pendiente. Si una comprobación anterior deja de ser aplicable, indícalo con una nota
breve en Verificación y señala qué requiere nueva comprobación. Resume antecedentes solo
cuando expliquen una restricción de datos, compatibilidad o migración. Las decisiones
arquitectónicas conservan la opción vigente, su justificación y consecuencias útiles,
con alternativas solo cuando ayuden al mantenimiento; no son un registro de quién dijo
qué.

Al adaptar documentos existentes dentro del alcance solicitado, consolida el texto
afectado con estas reglas sin perder requisitos vigentes ni evidencia útil. No limpies
todo el archivo histórico de specs como efecto de actualizar el método.

## Profundidad proporcional al cambio

Mantén un único método y una única plantilla adaptable. El objetivo es acordar,
implementar y verificar el cambio, no completar todos los apartados. Ajusta la
profundidad al riesgo y a la incertidumbre, no al número de líneas de código.

| Situación                                                           | Tratamiento                                                                                                               |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Mantenimiento que conserva o restaura un comportamiento ya acordado | No crear una spec nueva; referenciar o actualizar la existente cuando corresponda y registrar la verificación pertinente. |
| Cambio funcional acotado, conocido y de bajo riesgo                 | Usar el núcleo breve de templates/change.md.                                                                              |
| Cambio con incertidumbre o impacto significativo                    | Ampliar la misma spec con las secciones y escenarios necesarios.                                                          |

La IA elige la profundidad a partir de la petición y del contexto comprobado, sin exigir
una clasificación formal ni una aprobación adicional del formato. Si aparece un riesgo o
una duda relevante, amplía el mismo documento antes de implementar la parte afectada. Si
cambian los requisitos aprobados, vuelve a obtener aprobación para ese cambio de
alcance.

### Núcleo breve

Todas las change specs conservan el frontmatter de la plantilla y contienen:

- **Cambio y límites:** necesidad, comportamiento esperado y límites relevantes, sin
  repetirlos como problema, objetivo y alcance separados.
- **Criterios de aceptación:** resultados observables suficientes para comprobar el
  cambio; sin un número fijo ni duplicación obligatoria en escenarios.
- **Impacto en Odoo:** áreas afectadas y restricciones pertinentes comprobadas, sin un
  formulario de modelos, campos, vistas y demás áreas no afectadas.
- **Verificación:** plan ligado a los criterios y resultados con evidencia real,
  indicando lo pendiente y lo no ejecutado. En draft deja los resultados pendientes
  salvo que haya evidencia previa aplicable, identificada sin inventar verificaciones.

### Cuándo ampliar

Revisa especialmente permisos y reglas de registro, uso de sudo(), aislamiento
multicompañía, integridad o conservación de datos, cálculos contables o de stock,
instalación/actualización/migraciones, integraciones, contratos externos y cambios
transversales. Una modificación mínima en estas áreas puede necesitar una spec ampliada.
El alcance ambiguo y las alternativas con consecuencias distintas también requieren más
detalle.

Añade solo los apartados que aclaren el acuerdo o sus riesgos:

- Actores y permisos, con acciones permitidas y denegadas relevantes.
- Escenarios funcionales Dado/Cuando/Entonces para precondiciones, variantes, errores o
  límites que no queden claros en los criterios.
- Desglose del impacto en seguridad/multicompañía, datos, migraciones, integraciones u
  otras áreas afectadas.
- Riesgos, medidas necesarias y puntos abiertos que requieran una decisión.
- Referencias a decisions/ cuando exista una elección arquitectónica duradera, no para
  cada elección técnica rutinaria.

Puedes separar problema, objetivo o fuera de alcance si mejora la comprensión. No añadas
apartados vacíos ni cadenas de «No aplica», ni dupliques un requisito solo para cubrir
dos formatos. La concisión nunca justifica omitir una regla relevante o afirmar que no
hay impacto sin comprobarlo.

### Ejemplos de profundidad

Ejemplo ilustrativo de spec breve, suponiendo que ya se ha comprobado la existencia del
campo y el alcance de la vista:

```markdown
---
id: change-2026-10-06-show-reference
title: "Mostrar la referencia existente en el listado"
status: draft
module: "<module_name>"
created: 2026-10-06
---

## Cambio y límites

Mostrar la referencia existente en el listado para identificar los registros. No añadir
campos ni modificar cómo se guarda o edita la referencia.

## Criterios de aceptación

- [ ] Cada fila muestra la referencia del registro; si está vacía, queda vacía.
- [ ] Se mantienen la edición existente y los permisos de acceso vigentes.

## Impacto en Odoo

Vista de listado existente; campo ya disponible. Sin nuevos modelos ni permisos.

## Verificación

Plan: comprobar registros con y sin referencia, la edición existente y el acceso con los
roles afectados, según las autorizaciones vigentes.

Resultados: pendiente; no se han ejecutado comprobaciones.
```

En cambio, una aprobación con distintos roles y compañías ampliaría ese mismo núcleo con
actores y permisos, escenarios de aprobación y denegación, aislamiento entre compañías y
efectos sobre el estado o los datos. El plan comprobaría esos criterios, no solo que
aparezca el botón. Una decisión aparte sería necesaria únicamente si hay una elección
arquitectónica que conservar.

## Ciclo de estados recomendado

draft -> approved -> implementing -> verified -> superseded

El ciclo representa el flujo de colaboración:

1. El usuario describe el cambio en un prompt o copia la plantilla templates/change.md.
2. La IA lee module-contract.md y solo las specs relevantes, y crea o ajusta una change
   spec con estado draft.
3. El usuario revisa el comportamiento, los límites y los criterios de aceptación, junto
   con los escenarios y riesgos cuando sean necesarios. Puede editar el fichero
   directamente o pedir a la IA que lo revise.
4. El usuario aprueba explícitamente los requisitos. Solo entonces el estado debe pasar
   a approved.
5. La IA implementa el comportamiento aprobado y puede establecer el estado
   implementing.
6. Se verifican los criterios de aceptación según la autorización y política vigentes.
   Registra los resultados; solo pasa a verified si todos los criterios están realmente
   comprobados. Si no, conserva implementing y lo pendiente.
7. Si un cambio posterior sustituye ese comportamiento, se crea la nueva spec y la
   anterior pasa a superseded.

Normalmente una misma change spec se mantiene durante todo su ciclo de vida. No crees un
fichero nuevo para cada prompt, cada paso de implementación, cada commit o cada
comentario de revisión.

Los estados describen el trabajo, no imponen una ronda de preguntas por cada transición.
El usuario puede aprobar los requisitos e indicar que se implementen en un mismo
mensaje. No repitas la aprobación para el mismo alcance ni las autorizaciones ya
concedidas. La preparación de una spec no autoriza su implementación; tampoco la
aprobación autoriza por sí sola pruebas, operaciones de base de datos o mutaciones Git
fuera de lo solicitado y la política vigente.

## Flujo mediante prompts o manual

Ambas formas son válidas.

### Opción recomendada: pedir a la IA que cree el borrador

Por ejemplo:

```text
Quiero añadir una funcionalidad para que los usuarios puedan archivar
registros de forma reversible.

Crea una change spec en specs/changes/ usando templates/change.md.
Parte del núcleo breve y amplía solo lo que requieran el riesgo y las dudas
reales. Aprovecha el contexto existente y agrupa las preguntas necesarias.

Déjala en status: draft. No implementes todavía el código.
```

La IA puede crear un fichero como:

```text
specs/changes/change-2026-08-05-reversible-archive.md
```

Después, el usuario revisa el fichero y puede editarlo directamente o pedir cambios a la
IA.

### Opción alternativa: crear o editar el fichero manualmente

El usuario puede copiar templates/change.md dentro de changes/, rellenar los requisitos
y pedir después a la IA que revise la spec. La IA no debe implementarla hasta que el
frontmatter tenga status: approved.

Lo importante no es quién crea el fichero. Lo importante es que el fichero aprobado sea
la fuente de verdad antes de comenzar la implementación.

## Ejemplos de prompts de aprobación e implementación

Después de revisar el borrador:

```text
He revisado specs/changes/change-2026-08-05-reversible-archive.md.
La funcionalidad y los criterios de aceptación son correctos.

Actualiza su estado a approved y, a continuación, implementa únicamente
lo definido en esa spec. Lee también module-contract.md, pero no cargues
toda la carpeta specs/.
```

Si la spec está aprobada pero todavía no se quiere programar:

```text
La spec change-2026-08-05-reversible-archive.md está aprobada.
Todavía no implementes el código. Revisa si hay puntos abiertos o decisiones
arquitectónicas que debamos resolver antes de programar.
```

Después de implementar:

```text
Verifica la implementación de change-2026-08-05-reversible-archive.md contra
todos sus criterios de aceptación. Indica qué se ha verificado, qué no se ha
ejecutado y qué puntos quedan abiertos. Marca la spec como verified solo si
los criterios están realmente comprobados.
```

## Cuando el comportamiento vuelve a cambiar

- Si el cambio todavía se está diseñando, continúa refinando el mismo borrador.
- Si el cambio aprobado se amplía intencionadamente antes de verificarse, actualiza la
  misma spec y vuelve a revisarla antes de continuar.
- Si se trata de una capacidad nueva y distinta, crea una nueva change spec.
- Si el nuevo comportamiento sustituye al contrato anterior, crea una nueva spec y marca
  la antigua como superseded.
- No cambies silenciosamente el código dejando desactualizada la spec aprobada.

## Ajustes pendientes

La plantilla termina con un apartado **Ajustes pendientes** para recoger notas o
dictados del usuario durante la implementación y las pruebas. Es una bandeja de entrada
libre: no exige redacción formal, identificadores, estados por entrada ni campos
obligatorios. El usuario puede añadir observaciones según las descubre y pedir después:
«Revisa los ajustes pendientes de esta especificación».

Cuando reciba esa petición, la IA debe leer la bandeja de la spec relevante, interpretar
las ideas y contrastarlas con los requisitos y el código afectados. Preguntará solo por
ambigüedades relevantes que no pueda resolver con el contexto. Revisar notas autoriza su
incorporación documental; implementar requiere que la petición o los acuerdos vigentes
también autoricen esa acción y ese alcance. Una nota informal no constituye por sí sola
aprobación de nuevos requisitos.

Integra cada punto en el lugar adecuado del mismo documento:

- Los comportamientos acordados, en Cambio y límites, Criterios de aceptación y los
  escenarios afectados, resolviendo contradicciones con el texto anterior.
- Las propuestas sin aprobar y dudas por resolver, en Puntos abiertos, indicando qué
  decisión falta y sin sustituir silenciosamente los requisitos aprobados.
- Los ajustes acordados pendientes de implementación, junto a los requisitos afectados o
  en un apartado de trabajo pendiente cuando ayude a su seguimiento.
- Las comprobaciones necesarias y los resultados reales, en Verificación. Conserva la
  evidencia anterior e indica qué deja de ser aplicable o necesita repetirse;
  implementar un ajuste no demuestra que esté verificado.

Retira de Ajustes pendientes cada nota una vez incorporada fielmente, aunque su
resolución continúe pendiente en el apartado de destino. Si solo se procesa una parte,
conserva únicamente la parte no trasladada. Las dudas pueden salir de la bandeja al
quedar recogidas explícitamente en Puntos abiertos. No borres una idea sin haberla
incorporado ni mantengas una copia redundante de las notas procesadas. Una bandeja vacía
significa que no quedan notas por procesar; puede haber decisiones, implementación o
verificación pendientes en el cuerpo de la especificación.

Cuando se solicite implementar los ajustes acordados, actualiza también la documentación
del addon afectada. Actualiza module-contract.md y AGENTS.md solo si cambia su contexto
estable. Aplica las reglas de aprobación, estados y nuevas specs descritas arriba: una
capacidad independiente o un comportamiento que sustituye al contrato anterior puede
requerir otra spec, referenciada desde esta. Mantén implementing mientras falten
criterios por comprobar; si una corrección reabre la verificación de una spec verified,
conserva su evidencia histórica y establece implementing hasta completar las
comprobaciones pertinentes.

Puedes revisar los ajustes por grupos relacionados o individualmente cuando un fallo
impida continuar. Al terminar, informa qué notas se han incorporado, qué se ha
implementado y qué decisiones o comprobaciones siguen pendientes.

## Preparación guiada de la especificación

Antes de presentar la spec para aprobación, conversa con el usuario sobre las decisiones
abiertas relevantes, los supuestos funcionales que necesiten su aceptación y las
debilidades detectadas en la propuesta. Revisa internamente las áreas pertinentes; lleva
a la conversación las que requieren una decisión. No dejes estas cuestiones únicamente
dentro del documento esperando que el usuario las descubra al leerlo.

Agrupa cuestiones relacionadas en rondas breves. Explica el caso concreto, sus
consecuencias y las opciones útiles; recomienda una cuando el contexto lo permita.
Distingue aclaraciones necesarias, problemas que conviene cubrir y mejoras opcionales
que amplían el alcance. Propón mejoras solo cuando estén directamente relacionadas y
aporten valor claro o eviten un problema probable.

Incorpora las respuestas al mismo borrador y continúa preguntando solo si revelan nuevas
decisiones relevantes. No recorras todos los apartados pidiendo confirmación ni repitas
acuerdos. Si la petición está completamente definida, presenta el borrador directamente,
sin fabricar preguntas.

Puedes preparar y guardar un borrador parcial dentro de la autorización vigente,
identificando lo pendiente. Para entregar la spec para aprobación, resuelve las
decisiones que condicionan el comportamiento de la parte afectada o acuerda
explícitamente su aplazamiento y límites. No presentes como cerrado un cambio con
decisiones funcionales pendientes.

Acompaña el documento con un resumen breve del comportamiento y los límites acordados,
las decisiones tomadas y cualquier punto todavía abierto, indicando su efecto sobre la
implementación. El resumen facilita la revisión; el documento conserva el acuerdo
completo. La conversación no aprueba requisitos por sí sola: mantén las reglas de
aprobación explícita del método.

## Reglas de lectura y preguntas para la IA

La IA debe leer únicamente la especificación relevante para la tarea actual. No debe
cargar automáticamente toda la carpeta specs/.

Antes de preguntar, aprovecha la petición, el contrato, los acuerdos anteriores y el
código relevante. Comprueba los hechos técnicos accesibles en el módulo; no traslades al
usuario preguntas que puedas resolver con esa lectura. El código describe la
implementación actual, pero no demuestra por sí solo aprobación de los requisitos ni
verificación funcional.

Pregunta solo por dudas cuya respuesta pueda cambiar el comportamiento, el alcance, la
seguridad, la integridad de datos, la compatibilidad o la solución. Agrupa las dudas
relacionadas en una ronda cuando sea posible, sin una pregunta por cada apartado ni
preguntas redundantes. Si hay información suficiente, redacta directamente el borrador
dentro del alcance autorizado. No inventes reglas de negocio ni ocultes incertidumbres
para mantener la spec breve.

Construye module-contract.md progresivamente con hechos estables útiles. No reconstruyas
todo el módulo ni exijas resolver información ajena al cambio. Actualízalo solo cuando
cambie el contexto estable relevante.

Mantén AGENTS.md centrado en contexto estable y reutilizable del módulo, restricciones,
invariantes, riesgos e instrucciones de trabajo. Actualízalo solo cuando cambie ese
contexto estable o la navegación del módulo. No copies en AGENTS.md el contrato
funcional, las especificaciones de funcionalidades ni el historial de cambios.

No inventes información funcional que no haya sido especificada. Registra las dudas bajo
Puntos abiertos y acláralas antes de implementar cuando afecten al comportamiento, los
permisos, la integridad de los datos o la compatibilidad.
