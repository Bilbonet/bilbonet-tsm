/* @odoo-module */

// Copyright 2026 Bilbonet <jesus@bilbonet.net>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import {KanbanQuickCreateController} from "@web/views/kanban/kanban_record_quick_create";
import {patch} from "@web/core/utils/patch";
import {useViewButtons} from "@web/views/view_button/view_button_hook";

patch(KanbanQuickCreateController.prototype, {
    setup() {
        super.setup(...arguments);
        if (this.props.resModel === "tsm.task") {
            useViewButtons(this.rootRef, {
                beforeExecuteAction: async (clickParams) => {
                    if (
                        clickParams.type === "object" &&
                        clickParams.name === "create_and_start"
                    ) {
                        return this.model.root.save({reload: false});
                    }
                    return true;
                },
            });
        }
    },
});
