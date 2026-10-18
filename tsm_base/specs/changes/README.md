# Especificaciones de cambios

Guarda aquí una change spec por cada comportamiento nuevo o modificado intencionadamente
que constituya un cambio funcional coherente. Crea el fichero copiando
../templates/change.md y utiliza un nombre descriptivo como:

```text
change-2026-08-05-reversible-archive.md
```

## Qué representa un fichero

Una change spec representa un cambio funcional. No es:

- un registro de cada commit de Git;
- un registro de cada prompt enviado a la IA;
- una lista de tareas técnicas;
- un lugar para guardar ideas de funcionalidades no relacionadas.

Si utilizas varios prompts para aclarar o implementar la misma funcionalidad, continúa
utilizando la misma change spec. Crea un fichero nuevo solo para un comportamiento
separado o para un reemplazo que deje obsoleto el contrato anterior.

## Profundidad del documento

Sigue las reglas de proporcionalidad de [../README.md](../README.md): usa el núcleo
breve para cambios funcionales acotados y amplía la misma spec cuando el riesgo o la
incertidumbre lo requieran. No rellenes apartados opcionales con «No aplica» ni
conviertas la plantilla en una lista de preguntas.

No crees un fichero nuevo para mantenimiento que conserva o restaura un comportamiento
ya acordado: referencia o actualiza la spec existente cuando corresponda. Si el
comportamiento esperado de una corrección no está definido, documenta el acuerdo
necesario, sin dar por hecho que todo bugfix está exento.

## Flujo de trabajo

1. Describe el comportamiento deseado en un prompt o copia manualmente la plantilla.
2. Antes del primer borrador, acuerda las decisiones relevantes que falten tras
   comprobar los hechos accesibles. Pide a la IA que cree o refine el fichero en estado
   draft; conserva puntos abiertos solo si se acuerda aplazarlos o preparar un borrador
   parcial.
3. Revisa el comportamiento, los límites y los criterios de aceptación, junto con los
   escenarios, permisos y riesgos que correspondan al cambio.
4. Aprueba explícitamente los requisitos estableciendo status: approved o pidiendo a la
   IA que lo haga después de tu confirmación.
5. Pide a la IA que implemente únicamente esa spec aprobada.
6. Realiza los casos de `Pruebas manuales y aprobación` y marca los correctos: cada
   casilla marcada es evidencia suficiente, sin notas obligatorias. Comunica los fallos
   por chat o en `Ajustes pendientes` y expresa por separado tu conformidad con la
   implementación. Las comprobaciones técnicas conservan su autorización y resultado
   reales.
7. Revisa el encaje final con la spec y la vigencia de la evidencia. Marca verified solo
   con todos los criterios comprobados, conformidad explícita y pruebas automatizadas
   solicitadas, si existen, terminadas correctamente. Mientras falte alguna comprobación
   o conformidad, conserva implementing.
8. Si el comportamiento cambia intencionadamente, actualiza la spec o crea una sustituta
   y marca la anterior como superseded.

El usuario puede crear el fichero manualmente, pero el flujo recomendado es pedir a la
IA que lo redacte a partir de la petición funcional inicial. En ambos casos, el fichero
es la fuente de verdad una vez aprobado.

La aprobación y la petición de implementación pueden darse en el mismo mensaje; los
estados no requieren confirmaciones separadas ni repetir autorizaciones vigentes para el
mismo alcance. Las pruebas y operaciones Git o de base de datos siguen sus propias
autorizaciones y políticas. Conserva lo pendiente si los criterios no están comprobados;
una spec breve no tiene una verificación menor.

Sigue las reglas de [../README.md](../README.md) para elegir la solución más sencilla,
acordar ampliaciones de alcance y resolver ajustes menores sin documentar cada
iteración. Las pruebas automatizadas no se solicitan ni ejecutan por defecto; su
ausencia no bloquea el cierre si no se han solicitado y todos los criterios están
comprobados. Mantén el detalle de RPC, ORM e inspecciones internas en el plan técnico.

## Ejemplos de prompts

Crear un borrador:

```text
Quiero que el módulo permita archivar registros y restaurarlos después.

Crea o actualiza una change spec en specs/changes/ para esta funcionalidad.
Usa el núcleo breve de la plantilla y amplía solo las áreas relevantes según
el riesgo y la incertidumbre. Define criterios observables, agrupa las dudas
necesarias y deja el estado en draft. No escribas código todavía.
Antes del primer borrador, plantea las decisiones relevantes que falten.
Redacta criterios y pruebas manuales breves; deja puntos abiertos solo si
acordamos aplazarlos o preparar un borrador parcial.
```

Aprobar e implementar:

```text
He revisado la change spec y apruebo sus requisitos.

Cambia su estado a approved e implementa únicamente lo definido en esa spec.
No inventes comportamientos que no estén documentados.
```

Verificar:

```text
He realizado todas las pruebas de Pruebas manuales y aprobación y sus resultados
son correctos. Doy mi conformidad a la implementación. Registra esta confirmación.
No he solicitado pruebas automatizadas. Revisa el encaje final con la spec y la
vigencia de la evidencia. Marca verified solo si todos los criterios están
comprobados; conserva explícitamente cualquier comprobación pendiente.
```

## Nombre y estados

Utiliza el frontmatter definido en templates/change.md:

```yaml
id: change-YYYY-MM-DD-short-slug
title: "<Título de la funcionalidad>"
status: draft
module: "<nombre técnico del módulo>"
created: YYYY-MM-DD
```

Los estados del flujo son:

```text
draft -> approved -> implementing -> verified -> superseded
```

No marques una spec como approved simplemente porque se haya creado. La aprobación
significa que los requisitos están suficientemente claros para implementar y que el
usuario los ha aceptado expresamente.
