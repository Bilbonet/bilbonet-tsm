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
2. Pide a la IA que cree o refine el fichero en estado draft.
3. Revisa el comportamiento, los límites y los criterios de aceptación, junto con los
   escenarios, permisos y riesgos que correspondan al cambio.
4. Aprueba explícitamente los requisitos estableciendo status: approved o pidiendo a la
   IA que lo haga después de tu confirmación.
5. Pide a la IA que implemente únicamente esa spec aprobada.
6. Verifica los criterios de aceptación y registra el resultado.
7. Marca la spec como verified solo cuando el comportamiento se haya comprobado
   realmente.
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

## Ejemplos de prompts

Crear un borrador:

```text
Quiero que el módulo permita archivar registros y restaurarlos después.

Crea o actualiza una change spec en specs/changes/ para esta funcionalidad.
Usa el núcleo breve de la plantilla y amplía solo las áreas relevantes según
el riesgo y la incertidumbre. Define criterios observables, agrupa las dudas
necesarias y deja el estado en draft. No escribas código todavía.
```

Aprobar e implementar:

```text
He revisado la change spec y apruebo sus requisitos.

Cambia su estado a approved e implementa únicamente lo definido en esa spec.
No inventes comportamientos que no estén documentados.
```

Verificar:

```text
Comprueba la implementación contra los criterios de aceptación de la change
spec. Documenta el resultado y marca la spec como verified solo si todo está
comprobado.
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
