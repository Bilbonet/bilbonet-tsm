---
id: change-2026-11-01-remove-pending-settlement-lines
title: "Edición nativa de líneas de liquidación sin facturar"
status: verified
module: "tsm_timesheet_commission"
created: 2026-11-01
---

# Especificación del cambio

## Cambio y límites

Usar la edición y la papelera nativas de las líneas de liquidación TSM mientras la hoja
esté en `settled`. Los demás estados dejan la lista en solo lectura. Se mantienen las
ACL OCA y el control original de la cabecera y de las liquidaciones no TSM. El ajuste
consiste únicamente en la condición XML `readonly` de `line_ids`.

Al guardar la eliminación se conserva el parte y su agente, se actualiza el total y la
comisión queda pendiente si no tiene otra liquidación activa. Al liquidar de nuevo se
mantiene la agrupación por fecha del parte: puede reutilizarse una hoja elegible o
crearse otra del mismo período si la anterior está facturada. No se aplaza al mes
siguiente ni se añaden botones, campos, métodos Python o validaciones específicas.

## Pruebas manuales y aprobación

- [x] Editar una hoja TSM sin facturar y borrar una línea con la papelera; guardar → se
      actualiza el total y se conservan el parte y su agente.
- [x] Volver a liquidar la comisión pendiente → se incorpora a una hoja elegible del
      período de su fecha, sin duplicar las comisiones que siguen liquidadas.
- [x] Abrir una hoja facturada o cancelada → las líneas están en solo lectura.
- [x] Revisar una liquidación manual y otra de facturas de venta → mantienen su
      comportamiento habitual y los permisos OCA.

**Resultado de la verificación manual:** correcto.

## Verificación técnica

Vista compuesta estáticamente con OCA y su extensión contable: correcta. Se conservan
`editable="top"`, la eliminación estándar y la condición original de cabecera. La
expresión de solo lectura se comprueba para tipos TSM, manual y factura de venta y sus
estados. Sintaxis Python y `git diff --check` correctos. No hay campos, acciones ni
validaciones de borrado específicos para esta operación. Pruebas Odoo y operaciones de
base de datos: no solicitadas ni ejecutadas.
