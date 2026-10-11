/* @odoo-module */

// Copyright 2026 Jesus Ramiro <jesus@bilbonet.net>
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import {
    StateSelectionField,
    stateSelectionField,
} from "@web/views/fields/state_selection/state_selection_field";
import {formatSelection} from "@web/views/fields/formatters";
import {registry} from "@web/core/registry";

export class TaskStatusSelectionField extends StateSelectionField {
    static template = "tsm_base.TaskStatusSelectionField";

    setup() {
        super.setup();
        this.colorPrefix = "o_tsm_status_";
        this.colors = {
            on_track: "success",
            at_risk: "warning",
            off_track: "danger",
            on_hold: "info",
            done: "done",
        };
    }

    get options() {
        return this.props.record.fields[this.props.name].selection.filter(
            ([value]) => value !== "to_define"
        );
    }

    get currentValue() {
        return this.props.record.data[this.props.name] || "to_define";
    }

    get label() {
        return formatSelection(this.currentValue, {
            selection: this.props.record.fields[this.props.name].selection,
        });
    }

    async updateRecord(value) {
        if (!this.props.readonly) {
            await super.updateRecord(value);
        }
    }
}

export const taskStatusSelectionField = {
    ...stateSelectionField,
    component: TaskStatusSelectionField,
    extractProps(fieldInfo, dynamicInfo) {
        const props = stateSelectionField.extractProps(fieldInfo, dynamicInfo);
        return {...props, withCommand: props.withCommand && !props.readonly};
    },
};

registry.category("fields").add("tsm_task_status_selection", taskStatusSelectionField);
