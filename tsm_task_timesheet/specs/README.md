# Especificaciones del módulo

Esta carpeta contiene la fuente de verdad funcional del módulo. En ella se documenta qué
debe hacer el módulo, por qué existe cada comportamiento y qué decisiones condicionan su
implementación.

## Navegación del módulo

- [Contrato del módulo](module-contract.md).
- [Revisión de migración y verificación pendiente](migration-review.md).
- [Especificaciones de cambios](changes/README.md).
- [Decisiones arquitectónicas](decisions/README.md).
- Plantillas editables de [cambio](templates/change.md) y
  [decisión](templates/decision.md).

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
cambios quedan sin commit ni push salvo solicitud expresa. Conserva el trabajo ajeno y
señala cualquier impedimento para usar esa rama sin afectarlo. Esta excepción no incluye
crear el addon ni definir cambios funcionales o modificar código.

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
breve junto al resultado afectado y señala qué requiere nueva comprobación. Resume
antecedentes solo cuando expliquen una restricción de datos, compatibilidad o migración.
Las decisiones arquitectónicas conservan la opción vigente, su justificación y
consecuencias útiles, con alternativas solo cuando ayuden al mantenimiento; no son un
registro de quién dijo qué.

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
- **Pruebas manuales y aprobación:** lista única de pruebas ligadas a los criterios, con
  acción, resultado esperado y casilla de realización correcta, suficiente como
  evidencia por sí sola, seguida de la conformidad del usuario. En draft deja las
  casillas sin marcar salvo evidencia previa aplicable, identificada sin inventar
  verificaciones.
- **Pruebas automatizadas:** decisión y resultados. Por defecto, no solicitadas y no
  ejecutadas; solo se ejecutan con autorización explícita aplicable.

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
- Riesgos, medidas necesarias y puntos abiertos cuyo aplazamiento se haya acordado.
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

- Cada fila muestra la referencia del registro; si está vacía, queda vacía.
- Se mantienen la edición existente y los permisos de acceso vigentes.

## Impacto en Odoo

Vista de listado existente; campo ya disponible. Sin nuevos modelos ni permisos.

## Pruebas manuales y aprobación

Marca cada casilla tras realizar la prueba y comprobar el resultado esperado. La casilla
marcada basta para confirmar el resultado correcto; no requiere notas.

- [ ] Abrir el listado con referencias rellenas y vacías → cada fila muestra su valor
      correspondiente.
- [ ] Editar la referencia como antes → la edición conserva su funcionamiento.
- [ ] Acceder con los roles afectados → se mantienen los permisos vigentes.

**Conformidad del usuario:** pendiente.

## Pruebas automatizadas

**Decisión:** no solicitadas; no se ejecutan por defecto. **Resultado:** no ejecutadas.
```

En cambio, una aprobación con distintos roles y compañías ampliaría ese mismo núcleo con
actores y permisos, escenarios de aprobación y denegación, aislamiento entre compañías y
efectos sobre el estado o los datos. El plan comprobaría esos criterios, no solo que
aparezca el botón. Una decisión aparte sería necesaria únicamente si hay una elección
arquitectónica que conservar.

## Solución más sencilla y ampliaciones de alcance

Por defecto, busca y recomienda la solución más sencilla, mantenible y comprensible que
cumpla el alcance acordado. Comprueba primero qué ofrecen la versión activa de Odoo y el
módulo: ORM, campos y sus atributos, restricciones, permisos, reglas de registro,
vistas, acciones y puntos de extensión existentes. Reutiliza el mecanismo adecuado antes
de añadir lógica propia, dependencias, capas o abstracciones. Valora la claridad y el
mantenimiento del conjunto; tener menos líneas no demuestra que una solución sea más
sencilla.

Delimita los usos y vías de entrada que necesita el cambio. Una petición sobre la
interfaz no incorpora automáticamente una integración externa ni obliga a crear una API.
Detectar una variante posible tampoco la convierte en requisito. Propón cobertura
adicional solo ante un caso relevante o un riesgo concreto, sin enumerar escenarios
hipotéticos para justificar más desarrollo.

Si los mecanismos existentes no bastan y cubrir un escenario exige piezas propias
adicionales o una complejidad relevante, plantea la decisión antes de incorporarlas como
requisitos o implementarlas, también si se descubre durante la implementación. Explica
brevemente:

- Qué resuelve la opción más sencilla y cuál es su límite concreto.
- Qué escenario exige ampliarla, si forma parte del alcance acordado y qué consecuencia
  tiene dejarlo sin cubrir.
- Qué piezas adicionales harían falta y su coste de desarrollo, mantenimiento y
  comprobación. Describe el esfuerzo cualitativamente si no hay base para estimar horas
  o importes; no inventes cifras.
- Qué opción recomiendas y qué decisión necesita el usuario: asumir ese coste, acotar o
  aplazar el escenario, o revisar el requisito cuando sea necesario.

Espera esa decisión para la parte afectada y continúa el trabajo independiente ya
autorizado. Aprovecha decisiones y autorizaciones previas para el mismo alcance y coste;
no pidas aprobar cada elección técnica rutinaria ni cada uso normal del ORM. Documenta
el alcance elegido en Cambio y límites y el mecanismo y las ampliaciones acordadas en
Impacto en Odoo, sin añadir un formulario nuevo. Amplía criterios y comprobaciones
únicamente para la cobertura acordada.

La sencillez debe respetar los permisos, la seguridad y la integridad exigidos por el
acuerdo. Un comportamiento de la vista o un onchange no acredita por sí solo una
garantía del modelo. Si una regla debe cumplirse también desde importaciones, RPC u
otras vías existentes, busca primero el mecanismo de servidor de Odoo que la garantice;
esto no implica crear una integración nueva. Si hace falta desarrollo adicional, explica
la carencia y consulta su coste y el alcance antes de continuar. Si se descarta esa
ampliación, acuerda un alcance viable y declara sus límites; no presentes la garantía
original como cumplida ni conviertas una protección necesaria en una mejora opcional.

Aplica este criterio al preparar, revisar e implementar specs y al procesar Ajustes
pendientes. Conserva los acuerdos funcionales existentes; simplificar o ampliar su
comportamiento requiere resolver la diferencia con el usuario.

## Ciclo de estados recomendado

draft -> approved -> implementing -> verified -> superseded

El ciclo representa el flujo de colaboración:

1. El usuario describe el cambio en un prompt o copia la plantilla templates/change.md.
2. La IA lee module-contract.md y solo las specs relevantes, comprueba los hechos
   accesibles y conversa sobre las decisiones necesarias antes del primer borrador. Con
   las respuestas, crea o ajusta una change spec con estado draft.
3. El usuario revisa el comportamiento, los límites y los criterios de aceptación, junto
   con los escenarios y riesgos cuando sean necesarios. Puede editar el fichero
   directamente o pedir a la IA que lo revise.
4. El usuario aprueba explícitamente los requisitos. Solo entonces el estado debe pasar
   a approved.
5. La IA implementa el comportamiento aprobado y puede establecer el estado
   implementing.
6. El usuario realiza y registra las pruebas de Pruebas manuales y aprobación, y da su
   conformidad explícita. La IA revisa el encaje final con la spec y la vigencia de la
   evidencia. Solo pasa a verified si todos los criterios están comprobados y las
   pruebas automatizadas solicitadas, si existen, han terminado correctamente. Si no,
   conserva implementing y lo pendiente.
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
Antes del primer borrador, plantéame las decisiones que falten para acordarlas.
Redacta los criterios y las pruebas manuales de forma breve y práctica.

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
Todavía no implementes el código.
```

Después de implementar y realizar las pruebas manuales:

```text
He realizado todas las pruebas de Pruebas manuales y aprobación de
change-2026-08-05-reversible-archive.md y sus resultados son correctos.
Doy mi conformidad a la implementación. Registra esta confirmación como evidencia.
No he solicitado pruebas automatizadas. Revisa el encaje de la implementación final
con la spec y actualiza solo las diferencias acordadas que sea necesario reflejar.
Comprueba si algún ajuste requiere repetir una prueba o queda algún criterio pendiente
antes de marcar la spec como verified y continuar con el siguiente paso autorizado.
```

## Criterios y pruebas para el responsable del cambio

Asume que el usuario conoce la aplicación y la modificación solicitada. Redacta estos
apartados con lenguaje natural y breve, suficiente para revisar el acuerdo y probarlo.
Conserva el detalle necesario de diseño, restricciones y diagnóstico en las secciones
técnicas; no lo reproduzcas dentro de cada criterio o prueba.

Un criterio dice **qué debe cumplirse**; una prueba dice **qué hacer y qué resultado
comprobar**. Si numeras, usa CA1, CA2, etc. para los criterios y M1, M2, etc. para las
pruebas. Explica esa relación una sola vez en una frase y escribe cada referencia
completa: «Comprueba: CA1, CA3 y CA12», evitando «CA1,3,12». Los identificadores
acompañan a títulos comprensibles. Una prueba puede cubrir varios criterios y un
criterio puede necesitar varias pruebas; superar una prueba no acredita todas las
variantes del criterio.

Cada criterio expresa un resultado concreto en una o dos frases. Cada prueba tiene un
caso reconocible, una acción y un resultado observable. Por ejemplo:

```markdown
- **CA1 — Guardar antes de añadir:** al añadir un parte, la hoja se guarda y mantiene su
  estado.

- [ ] **M1 — Añadir a una hoja nueva:** crea una hoja y pulsa Añadir parte → la hoja
      queda guardada y se abre el alta del parte. Comprueba: CA1.
```

Indica solo los datos o condiciones necesarios para reproducir el caso. Divide una
prueba cuando reúna resultados que puedan fallar o corregirse por separado; no combines
altas, cancelaciones, permisos y concurrencia en una sola casilla. Incluye las variantes
pertinentes, sin multiplicar todas las combinaciones de roles, estados, empresas y
dispositivos por defecto. La brevedad no elimina cobertura: comprueba la correspondencia
con los criterios al preparar el plan.

Pide comprobaciones que el usuario pueda realizar y reconocer en la interfaz. Las que
necesiten inspeccionar RPC, comandos ORM o datos internos pertenecen al plan técnico,
con su autorización y resultado reales. No sustituyas una garantía técnica por una
prueba visual que no la demuestra. Si afecta al cierre, explica brevemente qué
comprobación falta y acuerda cómo realizarla.

La indicación de uso puede limitarse a: «Prueba cada caso y marca los que funcionen: la
casilla marcada confirma que la prueba está realizada y es correcta, sin añadir notas.
Si algo falla, déjala sin marcar; puedes contarlo por chat o en Ajustes pendientes.
Cuando termines, confirma el resultado». Mantén las reglas completas del método en este
README; no copies en cada especificación un tutorial de estados, autorizaciones o
colaboración.

## Pruebas manuales y aprobación

La aprobación de requisitos (approved) permite implementar el alcance acordado. La
conformidad posterior confirma el resultado de las pruebas manuales; son momentos
distintos y una no sustituye a la otra.

Mantén en la spec un único apartado visible con este título, inmediatamente después de
Impacto en Odoo y antes de las pruebas automatizadas. Cada casilla contiene qué hacer y
qué resultado esperar. Usa listas ordinarias en Criterios de aceptación para que las
casillas de pruebas sean el lugar inequívoco donde registrar su realización. No
distribuyas las instrucciones y los resultados manuales entre varios apartados.

El usuario marca [x] solo cuando la prueba se ha realizado y es correcta. La casilla
marcada es evidencia suficiente: no necesita añadir una valoración, justificación,
resultado observado ni confirmación escrita por prueba. No añadas campos «Resultado» o
«Evidencia» a cada caso ni bloquees una prueba marcada porque carezca de nota. Las notas
y observaciones son opcionales. Si falla o no se ha realizado, conserva [ ]. El usuario puede
comunicar fallos, dudas o ajustes por chat o en Ajustes pendientes, sin rellenar una nota
por caso. No exijas capturas, logs ni campos adicionales por defecto. Si el usuario confirma
las pruebas por chat, la IA marca las que confirme como realizadas y correctas y registra
su conformidad cuando la haya expresado; no exige editar el fichero además de responder ni
genera notas redundantes. Una confirmación general cubre toda la lista solo si dice expresamente
que se han realizado todas las pruebas y son correctas. Una frase como «está bien» o «continúa»
no acredita por sí sola su ejecución.

Tras implementar, enlaza directamente este apartado e indica que queda pendiente de
pruebas y conformidad del usuario. Al recibir «continúa», lee lo registrado: si faltan
pruebas o conformidad, señala únicamente lo pendiente y mantén implementing. Puedes
continuar trabajo independiente autorizado, pero no cerrar la verificación ni avanzar a
un paso que dependa de esa conformidad. Si la conformidad ya consta para el mismo
alcance, no vuelvas a solicitarla.

En Pruebas automatizadas deja explícita la decisión: no solicitadas y no ejecutadas por
defecto. No conviertas su ejecución en requisito de cierre si no se ha solicitado;
tampoco presentes esa ausencia como un resultado correcto. Si se autorizan, registra las
pruebas concretas, resultados y evidencia, y mantén implementing mientras estén
pendientes o fallen. Si algún criterio necesita una comprobación que las pruebas
manuales no cubren, señala la carencia y acuerda cómo comprobarlo antes de declarar
verified. Conserva los controles técnicos o de repositorio exigidos por la política
aplicable y sus resultados; esta regla no los sustituye ni autoriza operaciones de base
de datos o Git.

Al adaptar specs anteriores, reúne la verificación manual en este apartado conservando
la evidencia y el estado reales. No marques pruebas ni atribuyas conformidad como efecto
de reorganizar el documento. Aplica también la suficiencia de la casilla al continuar
con specs anteriores: una prueba marcada no necesita una nota adicional. Al adaptar el
método, retira los campos pendientes de resultado por caso que hayan quedado obsoletos y
conserva las observaciones útiles existentes. Si un ajuste afecta a una prueba ya
superada, señala que necesita repetirse y mantén las demás evidencias.

## Ajustes menores durante la implementación y las pruebas

Durante estas iteraciones, aplica los ajustes solicitados que conserven el
comportamiento acordado sin actualizar la spec por cada petición ni preguntar si deben
registrarse. Las consultas por sí solas tampoco generan cambios documentales. Valora el
efecto funcional, no las líneas de código: márgenes, colores, etiquetas o disposición de
campos suelen ser ajustes menores; cambiar su obligatoriedad, permisos, datos guardados
o resultados puede alterar el acuerdo. Si el ajuste contradice un requisito explícito,
trátalo como cambio de alcance.

Cuando cambien requisitos, límites o criterios de aceptación, señala la diferencia y
resuelve el alcance antes de implementar la parte afectada. Aprovecha las decisiones y
autorizaciones ya expresadas; pregunta solo si queda algo sin acordar.

Antes de cerrar la validación y continuar con un paso que dependa de ella, revisa que la
implementación final encaje con la spec. Consolida únicamente las diferencias acordadas
que necesiten reflejarse en requisitos, criterios o instrucciones de prueba; no añadas
un inventario de ajustes ni un historial. Si sigue encajando, deja la spec como está.
Esta revisión pertenece al cierre existente, sin una nueva fase ni otra aprobación para
el mismo alcance. Una diferencia funcional sin acordar requiere aclaración y no puede
aprobarse por haber pasado las pruebas.

Comprueba también la vigencia de la evidencia: si un ajuste afecta a una prueba
superada, señala en ese punto que debe repetirse y conserva las demás evidencias. No
esperes al cierre para advertir una invalidación ya conocida ni exijas repetir toda la
lista por un ajuste que no afecta a sus resultados.

Si el usuario escribió en Ajustes pendientes una nota sobre un ajuste menor ya realizado
que conserva el acuerdo, puedes retirarla al procesarla e informar de su resolución, sin
trasladarla al cuerpo como requisito o historial. Mantén las notas sin resolver y
conserva cualquier decisión funcional o evidencia pertinente. Una petición expresa de
documentar un ajuste prevalece sobre esta regla por defecto.

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
- Las propuestas sin aprobar y dudas por resolver, en la conversación antes de
  incorporarlas como requisitos. Déjalas en Puntos abiertos solo si el usuario acuerda
  aplazarlas o pide conservar un borrador parcial; indica qué decisión falta sin
  sustituir silenciosamente los requisitos aprobados.
- Los ajustes acordados pendientes de implementación, junto a los requisitos afectados o
  en un apartado de trabajo pendiente cuando ayude a su seguimiento.
- Las comprobaciones manuales y sus resultados, en Pruebas manuales y aprobación; las
  automatizadas y otras comprobaciones técnicas, en Pruebas automatizadas. Conserva la
  evidencia anterior e indica qué deja de ser aplicable o necesita repetirse;
  implementar un ajuste no demuestra que esté verificado.

Retira de Ajustes pendientes cada nota una vez incorporada fielmente, aunque su
resolución continúe pendiente en el apartado de destino. Si solo se procesa una parte,
conserva únicamente la parte no trasladada. Las dudas pueden salir de la bandeja cuando
se resuelvan o se acuerde dejarlas en Puntos abiertos. Para ajustes menores ya
realizados que conservan el acuerdo, aplica la excepción descrita arriba e informa de su
resolución. Para las demás notas, no borres una idea sin haberla incorporado ni
mantengas una copia redundante de las notas procesadas. Una bandeja vacía significa que
no quedan notas por procesar; puede haber decisiones, implementación o verificación
pendientes en el cuerpo de la especificación.

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

Antes de redactar o entregar el primer borrador de un cambio, conversa sobre las
decisiones abiertas relevantes, los supuestos funcionales que necesiten su aceptación y
las debilidades detectadas en la propuesta. Revisa internamente las áreas pertinentes;
lleva a la conversación las que requieren una decisión. No dejes estas cuestiones
únicamente dentro del documento esperando que el usuario las descubra al leerlo.

Agrupa cuestiones relacionadas en rondas breves. Explica el caso concreto, sus
consecuencias y las opciones útiles; recomienda una cuando el contexto lo permita.
Distingue aclaraciones necesarias, problemas que conviene cubrir y mejoras opcionales
que amplían el alcance. Propón mejoras solo cuando estén directamente relacionadas y
aporten valor claro o eviten un problema probable.

Incorpora las respuestas a los requisitos, criterios y pruebas y continúa preguntando
solo si revelan nuevas decisiones relevantes. No recorras los apartados pidiendo
confirmación ni repitas acuerdos. Si la petición está completamente definida, presenta
el borrador directamente, sin fabricar preguntas.

Por defecto, el primer borrador recoge las decisiones ya tratadas y resueltas. La
petición de una especificación no implica querer un borrador con decisiones pendientes.
Puedes conservar puntos abiertos cuando el usuario lo pida o acuerde explícitamente
aplazarlos, incluido un borrador parcial solicitado para discutirlos. Resolver estas
decisiones no equivale a aprobar la especificación completa.

Si se acuerda dejar puntos abiertos, sitúa su apartado antes de Criterios de aceptación,
explica cada cuestión antes de referenciarla e indica qué parte queda condicionada. Los
criterios deben describir el acuerdo vigente; no conviertas opciones recomendadas sin
decidir en requisitos aparentemente cerrados. Conserva las dudas técnicas no comprobadas
con su límite de evidencia; compruébalas cuando sea posible y plantea al usuario las
decisiones funcionales que se deriven.

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

No inventes información funcional que no haya sido especificada. Plantea las dudas
relevantes durante el análisis y resuélvelas antes del primer borrador; registra Puntos
abiertos solo con el aplazamiento o borrador parcial acordado. Si aparecen nuevas dudas
en fases posteriores, resuélvelas antes de implementar la parte afectada. Los
desconocidos ajenos al cambio en module-contract.md no obligan a abrir un cuestionario
ni a bloquear esta preparación.
