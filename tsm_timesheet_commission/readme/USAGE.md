1. Open a task under **T.S.M > Tasks** and add time entries. Customer agents
   are proposed using their TSM commission.
2. Use the people icon on a time entry to edit its agents and commissions.
   Commission managers can also use the additional icon for entries without a
   time pack or without consumed pack hours.
3. Automatic hourly prices use the time pack price for consumed hours and zero
   for complimentary pack hours. Without a pack, they use the commission's
   hourly product price. A nonzero specific price overrides automatic pricing;
   zero keeps automatic pricing.
4. **Regenerate agents** replaces the task's current agent assignments from
   the customer setup. Settled agents cannot be deleted or regenerated.

![Task with timesheet and commissions](static/description/task_timesheet_commission.png)

To settle commissions, open the OCA **Settle Commissions** action, choose
**Timesheet**, agents and the cutoff date. The wizard processes completed
settlement periods. Commissions configured for closed tasks wait until the task
is closed. Entries without a task are skipped.

Open **Commissions > Settlements** to review TSM settlements and their source
time entries. The **Invoices Settlements** list is filtered to sales-invoice
commissions and does not list TSM settlements. Cancelling a TSM settlement makes
its agent lines available for settlement again.

For external agents, use **Make invoice** on a settlement, or the OCA
**Create Commission Invoices** action, with the appropriate accounting access.
Select the purchase journal, service product, optional invoice date and the
settlements to invoice.

Assigning agents does not lock the timesheet fields controlled by this addon.
Those fields become read-only when any agent has a non-cancelled settlement.
Cancelling all settlements for the entry releases those fields again.

Commission managers can edit TSM settlement lines in **Settled** state and remove
rows using the standard trash icon. Save the sheet to apply the changes. Removing
a settlement row preserves its time entry and agent, updates the sheet total and
leaves the source commission pending unless it has another active settlement.
Other settlement states keep the lines read-only.

Running the settlement wizard again uses the time-entry date. It can reinsert
the commission into an eligible sheet for that period, or create another sheet
if the previous sheet has been invoiced. It does not defer it to the following
month. A time entry remains locked while any agent has a non-cancelled settlement.
