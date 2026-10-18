# tsm_task_material

Extends `tsm_base` tasks with consumed products and a single linked sale order. Targets
Odoo 18 and depends on `tsm_base`, `sale` and `product`.

## Behavior and boundaries

- Material prices use the task company's currency. Preserve manually entered
  descriptions, units, prices and discounts when generating the order; convert prices to
  the order currency using its date. Let Sales compute commercial defaults and taxes in
  the task's company.
- Order creation requires task write access, the sales manager group and a stage that
  permits sales. Automatic confirmation is controlled on the task.
- Materials become immutable while an order is linked. Tasks with a linked order cannot
  be deleted. Deletion safeguards must permit module uninstallation.
- Material record rules mirror task company, privacy, follower and assignment rules in
  `tsm_base`. Review both together when changing task permissions.
- Project-report material sections belong inside the task loop. Use each task's currency
  rather than the project's currency.

## Validation focus

Cover ORM creation without onchanges, compatible units and variant prices, order
defaults and taxes, currency conversion, confirmation, duplicate-order prevention,
private tasks, company boundaries and material changes through RPC. Render both
inherited reports. Database tests and module upgrades require explicit authorization
under the workspace policy.
