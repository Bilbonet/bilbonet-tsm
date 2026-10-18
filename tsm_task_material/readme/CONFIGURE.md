## User permissions

Assign users the appropriate *T.S.M* access rights:

- *User*: read materials on visible tasks and manage materials on tasks assigned
  to them, within their allowed companies.
- *Manager*: manage materials on tasks within their allowed companies.

Creating a sales document additionally requires *Sales / Administrator* access
and permission to modify the task. Opening the linked sales document requires
Sales access and remains subject to the usual Sales permissions.

## Task stages

As a T.S.M manager, go to *T.S.M > Configuration > Stages* and enable *Create Sale
Order* on each stage from which users should be able to create sales documents.
This setting is independent of whether the stage is considered closed.

## Products and customer settings

Configure the products or services, sales prices, units of measure and sales taxes
to use on tasks. Units selected on a material line must belong to the product's
unit category.

Configure customer invoice and delivery addresses, payment terms, fiscal position
and pricelist in the task's company. Sales uses these settings when creating the
document. The customer's pricelist determines the order currency; prices and
discounts come from the material lines.

Maintain exchange rates when the task company and order use different currencies.
On each task, *Sale autoconfirm* is enabled by default. Disable it before creating
the sales document if it should remain a quotation for review.
