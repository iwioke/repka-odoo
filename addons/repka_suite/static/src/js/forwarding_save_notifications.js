/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { FormController } from "@web/views/form/form_controller";

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.repkaNotification = useService("notification");
    },

    async saveButtonClicked() {
        const saved = await super.saveButtonClicked(...arguments);
        if (saved !== false && this.model.root.resModel === "ufs.forwarder.order") {
            this.repkaNotification.add(_t("Заказ сохранён"), { type: "success" });
        }
        return saved;
    },

    async discard() {
        const notify =
            this.model.root.resModel === "ufs.forwarder.order" &&
            (await this.model.root.isDirty());
        const result = await super.discard(...arguments);
        if (notify) {
            this.repkaNotification.add(_t("Изменения отменены"), { type: "warning" });
        }
        return result;
    },
});
