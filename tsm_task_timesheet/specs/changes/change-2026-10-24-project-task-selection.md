---
id: change-2026-10-24-project-task-selection
title: "Seleccionar proyecto o tarea al registrar partes"
status: implementing
module: "tsm_task_timesheet"
created: 2026-10-24
---

## Cambio y límites

Permitir elegir primero el proyecto o primero la tarea en Mis partes de horas y Todos
los partes de horas, y mantener el mismo comportamiento en el formulario del parte. La
petición autoriza implementar esta selección bidireccional.

Seleccionar proyecto filtra las tareas de ese proyecto. Sin proyecto elegido, se pueden
buscar las tareas accesibles al usuario. Seleccionar una tarea rellena su proyecto y su
cliente; el selector de proyecto queda limitado al proyecto de esa tarea. Para elegir
otro proyecto se retira primero la tarea. Retirar la tarea conserva el proyecto como
filtro; quitar el proyecto limpia una tarea incompatible.

Editar el proyecto de un parte nunca traslada la tarea a otro proyecto. El cliente sigue
procediendo de la tarea, como antes. La tarea continúa siendo obligatoria en las vistas
de edición existentes y opcional en el modelo. La columna Proyecto sigue oculta dentro
de la pestaña de partes de la propia tarea.

## Criterios de aceptación

- **CA1 — Proyecto primero:** se puede seleccionar un proyecto y el selector de tareas
  sólo ofrece las tareas accesibles de ese proyecto.
- **CA2 — Tarea primero:** sin proyecto, se puede seleccionar una tarea; proyecto y
  cliente se completan con sus valores y no se ofrece otro proyecto incompatible.
- **CA3 — Cambiar la selección:** retirar la tarea permite elegir otro proyecto y otra
  tarea, sin mover la tarea anterior ni alterar sus otros partes.
- **CA4 — Coherencia:** no se puede guardar por ORM una combinación de tarea y proyecto
  diferentes. Al cambiar el proyecto de la propia tarea, sus partes conservan el vínculo
  y reflejan el nuevo proyecto.
- **CA5 — Conservar datos y permisos:** se mantienen partes, horas, etiquetas, campos e
  identificadores, las restricciones de acceso existentes y la columna oculta dentro de
  la tarea.

## Impacto en Odoo

`project_id` pasa de relacionado a calculado, almacenado y editable, con cálculo previo
a la inserción. Mantiene columna, tipo, índice y `copy=False`. Depende de
`task_id.project_id`, conserva la selección previa sin tarea y copia el proyecto de una
tarea seleccionada. Un onchange de proyecto limpia la tarea incompatible. Una
restricción de servidor rechaza combinaciones inconsistentes.

Los dominios de tarea y proyecto se aplican en la lista común y en el formulario; Todos
los partes hereda esa lista. Se utiliza el patrón del ORM de Odoo 18 sin añadir
dependencia de HR Timesheets ni escrituras inversas sobre tareas. Se elimina la
asignación redundante de proyectos a partes desde el onchange de la tarea.

Los valores históricos del antiguo relacionado ya corresponden a la tarea. No se
identifica una transformación de datos necesaria; queda pendiente comprobar la
actualización sobre una copia de datos migrados. No se ejecutan operaciones de BD ni se
modifica la política de seguridad como parte de este cambio.

## Pruebas manuales y aprobación

Marca cada caso tras comprobarlo. Los CA indican qué debe cumplirse y las pruebas M
comprueban esos criterios. La columna opcional Proyecto debe estar visible en los
listados para realizar estas comprobaciones.

- [ ] **M1 — Proyecto primero:** en Mis partes, elegir proyecto y abrir el selector de
      tareas → sólo aparecen sus tareas accesibles. Comprueba: CA1.
- [ ] **M2 — Tarea primero:** en un parte nuevo sin proyecto, elegir una tarea → se
      completan proyecto y cliente, y el selector de proyecto sólo ofrece el de esa
      tarea. Comprueba: CA2.
- [ ] **M3 — Cambiar de proyecto:** retirar la tarea, elegir otro proyecto y una tarea
      suya → se guarda la nueva selección y la tarea anterior conserva su proyecto.
      Comprueba: CA3.
- [ ] **M4 — Todos los partes:** repetir las selecciones anteriores en Todos los partes
      y en el formulario → se mantienen los mismos filtros y asignaciones. Comprueba:
      CA1, CA2 y CA3.
- [ ] **M5 — Mover la tarea:** cambiar de proyecto la propia tarea → sus partes siguen
      vinculados y reflejan el nuevo proyecto. Comprueba: CA4.
- [ ] **M6 — Partes existentes:** revisar horas, etiquetas y cliente de un parte previo
      y abrir la pestaña de partes de su tarea → los datos se conservan y Proyecto sigue
      oculto en esa pestaña. Comprueba: CA5.

**Conformidad del usuario:** autoriza el cierre de la migración tras superar pre-commit
y tests; los casos manuales no se han confirmado individualmente.

## Pruebas automatizadas y verificación técnica

**Decisión:** ejecución solicitada para cerrar la migración. **Resultado:** los 7 tests
específicos de selección proyecto/tarea pasan en la instalación limpia, dentro de los 20
tests del módulo. La suite completa TSM termina con 45 tests Python correctos y la suite
Kanban con 4 tests Hoot correctos.

Se comprueban ambos órdenes de selección con `Form`, cambio y retirada de la selección,
creación por lotes, rechazo de combinaciones incompatibles y propagación al mover el
proyecto de la tarea. La comprobación ORM de CA4 está superada. La actualización sobre
datos migrados desde 15.0 y la revisión visual de los desplegables continúan pendientes;
no se marcan casillas manuales como efecto de ejecutar estos tests.

Pre-commit sobre todos los archivos del módulo: correcto, incluidos los tests nuevos y
la generación de documentación. Sintaxis XML y esquema de lista de Odoo 18 correctos;
los dominios de lista y formulario se evaluaron estáticamente sin selección, con
proyecto y con proyecto/tarea. La columna Proyecto continúa oculta en la pestaña de la
tarea. `git diff --check` correcto.

Pylint con la configuración del editor mantiene únicamente el aviso previo `R0801` por
código duplicado en las validaciones de cierre de tarea. No se ha suprimido ni
modificado esa lógica como parte de esta selección.

## Ajustes pendientes
