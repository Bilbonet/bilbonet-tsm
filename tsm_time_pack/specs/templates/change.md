---
id: change-YYYY-MM-DD-short-slug
title: "<Título de la funcionalidad>"
status: draft
module: "<nombre técnico del módulo>"
created: YYYY-MM-DD
---

# Especificación del cambio

<!-- Describe el acuerdo vigente. Si cambia una decisión, reescribe las partes
afectadas y elimina contradicciones y propuestas descartadas. No transcribas
respuestas ni añadas bitácoras o historiales fechados. Conserva los metadatos
mínimos y la evidencia útil; limita antecedentes necesarios a notas breves.
Consulta Especificación vigente en ../README.md. -->

<!-- Usa este núcleo para cambios acotados. Amplía la misma spec según el
riesgo y la incertidumbre siguiendo ../README.md; no rellenes secciones
opcionales con «No aplica» ni uses la plantilla como cuestionario. -->

<!-- Antes del primer borrador, plantea las decisiones relevantes que falten,
sus consecuencias y opciones; incorpora las respuestas al acuerdo. Deja puntos
abiertos solo si el usuario acuerda aplazarlos o pide un borrador parcial.
En ese caso, explica los puntos antes de Criterios de aceptación y delimita
el alcance pendiente; no uses recomendaciones sin decidir como requisitos.
Si el cambio ya está completamente definido, no fabriques preguntas. -->

## Cambio y límites

<!-- Explica brevemente la necesidad y el comportamiento esperado, incluidos
los límites que eviten ambigüedades. Aprovecha la petición y el contexto ya
conocidos, sin duplicarlos en apartados separados. -->

## Criterios de aceptación

- **CA1 — <Título breve>:** <Resultado que debe cumplirse>.

<!-- El usuario conoce la aplicación y el cambio. Expresa cada criterio en una
o dos frases claras; lleva el detalle de implementación a su sección técnica.
Añade los criterios necesarios, sin un número fijo. Usa Dado/Cuando/Entonces
solo cuando aclare el caso; no repitas el requisito en dos formatos. -->

## Impacto en Odoo

<!-- Parte de la solución más sencilla que cumpla el acuerdo y reutiliza los
mecanismos existentes de la versión activa de Odoo y del módulo. Explica el
mecanismo elegido y sus límites relevantes. Si un escenario exige piezas extra
o complejidad relevante, consulta primero su cobertura y coste de desarrollo,
mantenimiento y comprobación; incorpora solo lo acordado. Distingue ampliaciones
opcionales de garantías necesarias de seguridad e integridad. Consulta
Solución más sencilla y ampliaciones de alcance en ../README.md. -->

<!-- Resume las áreas afectadas y las restricciones relevantes verificadas.
Desglosa solo lo necesario: modelos/campos, vistas/acciones, seguridad y
multicompañía, datos, instalación/actualización/migraciones o integraciones.
No supongas ausencia de impacto porque el cambio tenga pocas líneas. -->

## Pruebas manuales y aprobación

Prueba cada caso y marca los que funcionen: la casilla marcada confirma que la prueba
está realizada y es correcta, sin añadir notas. Si algo falla, déjala sin marcar; puedes
contarlo por chat o en Ajustes pendientes. Cuando termines, confirma el resultado.

Los CA indican qué debe cumplirse; las pruebas M comprueban esos criterios.

- [ ] **M1 — <Caso breve>:** <Qué hacer> → <Qué debe ocurrir>. Comprueba: CA1.

**Conformidad del usuario:** pendiente.

<!-- Un caso claro por casilla, con solo los datos necesarios para reproducirlo.
Divide resultados comprobables por separado. Enumera cada referencia completa:
«Comprueba: CA1, CA3 y CA12». Una prueba puede cubrir parte de un criterio;
revisa la cobertura del conjunto. Las comprobaciones de RPC/ORM o datos internos
van en el plan técnico, no como instrucciones al usuario de la interfaz.
Cada casilla marcada por el usuario es evidencia suficiente de realización
correcta. No añadas campos Resultado/Evidencia ni exijas valoraciones,
justificaciones o notas; las observaciones son opcionales y pueden comunicarse
por chat o en Ajustes pendientes. Si falla o no se ha realizado, déjala sin
marcar. Una declaración del usuario también es evidencia válida: marca solo
las pruebas que confirme como realizadas y correctas, sin inventar datos ni
exigir capturas o logs por defecto. No dupliques el plan y sus resultados en otros
apartados. La aprobación de requisitos previa no acredita estas pruebas.
Al continuar, lee este apartado y las incidencias comunicadas: mantén implementing
si falta alguna prueba o la conformidad explícita del usuario. Una casilla
marcada no queda pendiente por carecer de nota. No vuelvas a pedir conformidad
si ya está registrada para el mismo alcance. -->

## Pruebas automatizadas

**Decisión:** no solicitadas; no se ejecutan por defecto. **Resultado:** no ejecutadas.

<!-- Ejecuta pruebas automatizadas solo con autorización explícita aplicable.
Si se solicitan, registra aquí cuáles, su resultado y evidencia; mientras estén
pendientes o fallen, no marques verified. Si no se solicitan, su ausencia no
bloquea el cierre cuando todos los criterios estén comprobados y exista
conformidad manual. Si algún criterio no puede comprobarse manualmente,
señala qué comprobación falta; no lo des por verificado. Conserva aquí también
otras comprobaciones técnicas realmente realizadas y su evidencia, si existen.
Completar estos apartados no autoriza operaciones de base de datos. -->

<!-- Añade secciones solo cuando sean útiles: Actores y permisos, Escenarios
funcionales, Riesgos o una referencia a decisions/. Los puntos abiertos acordados
se explican antes de los criterios. Conserva el detalle técnico necesario y los
límites de lo comprobado sin trasladarlos a cada prueba manual. -->

## Ajustes pendientes

<!-- Espacio libre para notas o dictados del usuario durante la implementación
y las pruebas. No requiere buena redacción, identificadores ni campos fijos.
Al pedir revisar estos ajustes, la IA debe interpretarlos y contrastarlos con
la especificación y el código pertinente, aclarando solo dudas relevantes.
Debe incorporar cada punto a los requisitos, criterios, escenarios, Puntos
abiertos o los apartados de pruebas, según corresponda, y retirarlo de esta bandeja una
vez trasladado fielmente. Trasladar una nota no implica aprobarla, implementarla
ni verificarla: su situación debe quedar explícita en el apartado de destino.
Para notas que solo describan ajustes menores ya realizados y mantengan el acuerdo,
aplica la regla de ajustes menores de ../README.md: informa de su resolución al
retirarlas, sin convertirlas en requisitos ni en un historial de iteraciones.
Conserva aquí únicamente las notas aún no procesadas. Consulta ../README.md. -->
