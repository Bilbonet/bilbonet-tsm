/* @odoo-module */

// Copyright 2026 Bilbonet <jesus@bilbonet.net>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import {
    contains,
    createKanbanRecord,
    defineModels,
    editKanbanRecordQuickCreateInput,
    fields,
    models,
    mountView,
    onRpc,
} from "@web/../tests/web_test_helpers";
import {describe, expect, test} from "@odoo/hoot";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

class Customer extends models.Model {
    _name = "tsm.start.customer";

    name = fields.Char();
    _records = [{id: 1, name: "Customer"}];
}

class TsmTask extends models.Model {
    _name = "tsm.task";

    name = fields.Char({string: "Task Title", required: true});
    partner_id = fields.Many2one({string: "Customer", relation: "tsm.start.customer"});
    state = fields.Selection({selection: [["open", "Open"]], default: "open"});
    _records = [{id: 1, name: "Existing task", partner_id: 1, state: "open"}];
    _views = {
        "form,tsm_start_quick_create": `
            <form>
                <field name="name"/>
                <field name="partner_id" required="1"/>
                <button name="create_and_start" type="object" string="Start"/>
            </form>`,
    };
}

defineMailModels();
defineModels({Customer, TsmTask});
describe.current.tags("desktop");

async function openQuickCreate(context = {}) {
    await mountView({
        type: "kanban",
        resModel: "tsm.task",
        context,
        groupBy: ["state"],
        arch: `
            <kanban on_create="quick_create" quick_create_view="tsm_start_quick_create">
                <templates>
                    <t t-name="card"><field name="name"/></t>
                </templates>
            </kanban>`,
    });
    await createKanbanRecord();
}

for (const {label, context, missing} of [
    {label: "title and customer", context: {}, missing: ["name", "partner_id"]},
    {label: "customer", context: {default_name: "New task"}, missing: ["partner_id"]},
    {label: "title", context: {default_partner_id: 1}, missing: ["name"]},
]) {
    test(`Start requires ${label} before saving or calling the server`, async () => {
        onRpc("tsm.task", "web_save", () => expect.step("save"));
        onRpc("tsm.task", "create_and_start", () => {
            expect.step("start");
            return false;
        });
        await openQuickCreate(context);
        await contains(".o_kanban_quick_create button[name=create_and_start]").click();

        for (const name of missing) {
            expect(`.o_kanban_quick_create .o_field_widget[name=${name}]`).toHaveClass(
                "o_field_invalid"
            );
        }
        expect(".o_notification").toHaveText(/Invalid fields:/);
        expect.verifySteps([]);
    });
}

test("Start saves the task before calling the method with its new ID", async () => {
    onRpc("tsm.task", "web_save", ({args}) => {
        expect.step("save");
        expect(args[1].name).toBe("New task");
        expect(args[1].partner_id).toBe(1);
    });
    onRpc("tsm.task", "create_and_start", ({args}) => {
        expect.step("start");
        expect(args[0]).toEqual([2]);
        return false;
    });

    await openQuickCreate();
    await editKanbanRecordQuickCreateInput("name", "New task");
    await contains(
        ".o_kanban_quick_create .o_field_widget[name=partner_id] input"
    ).click();
    await contains(".o-autocomplete--dropdown-item").click();
    await contains(".o_kanban_quick_create button[name=create_and_start]").click();
    expect.verifySteps(["save", "start"]);
});
