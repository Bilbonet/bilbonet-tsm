---
id: change-2026-11-01-timesheet-edit-until-settlement
title: "Editar partes con agentes hasta su liquidación"
status: verified
module: "tsm_timesheet_commission"
created: 2026-11-01
---

# Especificación del cambio

## Cambio y límites

La asignación de comisionistas no debe impedir continuar registrando el trabajo. Los
campos que este módulo bloqueaba por tener agentes pasan a bloquearse cuando alguno de
esos agentes tenga una liquidación no cancelada. Se aplica a los campos de las vistas de
tarea, partes y bonos: fecha, técnico, duración, tarea, bono y consumo de horas según
los campos presentes en cada vista. En los partes dentro de la tarea se incluyen
expresamente `timepack_id` (Time Pack) y `discount_time` (descontar tiempo de la bolsa).

Se reutiliza la definición actual de liquidación: cualquier estado distinto de `cancel`.
Con varios agentes, cancelar solo una liquidación no libera la edición si queda otra
activa. Cancelarlas todas vuelve a permitir editar.

El alcance son los bloqueos de interfaz existentes. No se cambian ACL, reglas de
registro ni restricciones ORM; tampoco se redefine el estado de las liquidaciones.

## Criterios de aceptación

- **CA1 — Trabajo en curso:** asignar uno o varios agentes sin liquidar permite editar
  los campos anteriores y recalcular las comisiones según los datos del parte.
- **CA2 — Liquidación:** si algún agente tiene una liquidación no cancelada, esos campos
  quedan en solo lectura en las vistas afectadas.
- **CA3 — Cancelación:** cancelar una parte de las liquidaciones conserva el bloqueo
  mientras quede alguna activa; cancelar todas libera los campos.

## Impacto en Odoo

Los once atributos `readonly` que usaban `agent_ids` pasan a usar `any_settled`. Se
añaden dos atributos con la misma condición para Time Pack y descuento de tiempo
mediante una vista heredada de `tsm_time_pack.tsm_task_form_time_pack_view`, que es la
que inserta esos campos en la tarea. Se declara ese campo técnico en la lista base de
partes y en los partes del bono; la tarea ya lo incluía. Se conservan las subvistas
internas de agentes necesarias para no perder datos durante onchange. No se cambia el
código de cálculo ni se requiere una migración de datos; las vistas requieren
actualización del módulo.

## Pruebas manuales y aprobación

Las pruebas M verifican los criterios CA indicados. Comprobaciones manuales realizadas
con resultado correcto.

- [x] **M1 — Edición antes de liquidar:** añadir agentes y modificar fecha, técnico y
      duración, Time Pack y descuento de tiempo desde la tarea → permite guardar y las
      comisiones corresponden a los nuevos datos. Comprueba CA1.
- [x] **M2 — Otras vistas:** editar los campos disponibles desde listas de partes y
      bonos antes de liquidar → permite guardar. Comprueba CA1.
- [x] **M3 — Parte liquidado:** liquidar un agente y volver a abrir tarea, partes y bono
      → los campos afectados, incluidos Time Pack y descuento de tiempo en la tarea,
      quedan en solo lectura. Comprueba CA2.
- [x] **M4 — Cancelación parcial:** con dos agentes liquidados, cancelar solo una
      liquidación → los campos continúan bloqueados. Comprueba CA3.
- [x] **M5 — Cancelación completa:** cancelar las liquidaciones restantes → se puede
      volver a editar y guardar el parte. Comprueba CA3.

**Resultado de la verificación manual:** correcto.

## Verificación técnica

Se amplía el caso de regresión de liquidación/cancelación para comprobar edición previa,
recálculo, cancelación parcial y edición posterior a cancelar todas. Las comprobaciones
estáticas de XML, herencia y pre-commit quedan registradas en `../migration-review.md`.
No acreditan comportamiento del cliente ni una actualización real de vistas en base de
datos.

## Pruebas automatizadas

**Resultado:** suite local del módulo ejecutada en base temporal aislada: nueve pruebas
correctas, sin fallos ni errores. La verificación del cliente se mantiene en las pruebas
manuales. Véase `../migration-review.md`.
