## Record materials

1. Go to *T.S.M > Tasks* and open or create a task you can modify.
2. Select the customer and check the task's company.
3. Open the *Material* tab and add a line for each product or service used.
4. Review its description, quantity, unit, unit price and discount. Drag the line
   handle to change the display order.
5. Save the task.

Selecting a product fills its sales description, unit and sales price, including
variant price extras. Changing the unit converts the default unit price. You can
edit the description and price, and enter any agreed customer discount directly
on the line. Review the price again after changing the product or unit.

Quantities must be greater than zero and discounts cannot exceed 100%. Prices and
material totals use the task company's currency. Each subtotal is the quantity
multiplied by the unit price after discount.

## Create a sales document

1. Move the task to a stage with *Create Sale Order* enabled.
2. As a Sales administrator with permission to modify the task, check that a
   customer and at least one material line are present.
3. Review *Sale autoconfirm*: leave it enabled to confirm the order immediately,
   or disable it to create a draft quotation.
4. Click *Create sale*.

The button is available when the task has material lines, its stage permits sales
and no sales document is already linked. A customer is required to complete the
operation.

The document uses the task's company and customer. Lines preserve their order,
descriptions, products, units, quantities, entered prices and discounts. Prices
are converted to the order currency at the exchange rate for the order date when
necessary. Sales computes taxes using the product taxes and customer's fiscal
position.

The task code is recorded as the source document, and the customer reference
contains the task code and title. The order chatter includes a link to the source
task.

## Review the order and reports

Sales users can use the task's sales smart button to open the linked document,
subject to their Sales permissions. It displays the untaxed order amount in the
task company's currency and updates when the order amount changes.

Use *Print Task* on a task or *Print Project Report* on its project to include the
recorded materials. Reports show quantities, units where enabled, prices,
subtotals and totals. The discount column appears when at least one line has a
nonzero discount. Each task's materials use that task company's currency.

## Editing, archiving and deletion

- A task can have one linked sales document. While it is linked, creating another
  document and adding, changing or deleting materials are blocked. This also
  applies when the linked document is cancelled.
- Review subsequent sales changes on the sales document; they do not update the
  task's recorded material lines.
- A task with a linked sales document cannot be deleted. If the sales document
  can be deleted under Sales rules, deleting it removes the link and unlocks the
  materials.
- Archiving requires a stage marked as closed, as in `tsm_base`. Tasks with
  materials and no linked sales document additionally require Sales
  administrator rights to archive.

![Task with material](static/description/task_material.png)
