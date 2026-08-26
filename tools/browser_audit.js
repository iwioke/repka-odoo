(async () => {
    const specs = {
        "ir.module.module": {
            domain: [["state", "=", "installed"]],
            fields: ["name", "shortdesc", "summary", "description", "author", "website", "license", "category_id", "state", "latest_version", "published_version", "application", "auto_install", "demo", "icon", "dependencies_id"],
        },
        "ir.module.module.dependency": {
            fields: ["module_id", "name", "auto_install_required"],
        },
        "ir.model": {
            fields: ["name", "model", "state", "transient", "modules", "info", "is_mail_thread", "is_mail_activity", "is_mail_blacklist", "order"],
        },
        "ir.model.fields": {
            fields: ["name", "complete_name", "field_description", "model", "model_id", "state", "modules", "ttype", "relation", "relation_field", "required", "readonly", "index", "store", "compute", "depends", "related", "copy", "translate", "help", "selection", "size", "on_delete", "groups"],
        },
        "ir.ui.view": {
            fields: ["name", "model", "type", "priority", "arch_db", "inherit_id", "key", "active", "mode", "xml_id", "groups_id"],
        },
        "ir.ui.menu": {
            fields: ["name", "complete_name", "parent_id", "action", "sequence", "groups_id", "active", "web_icon", "xml_id"],
        },
        "ir.actions.act_window": {
            fields: ["name", "type", "res_model", "view_mode", "view_ids", "domain", "context", "target", "search_view_id", "limit", "binding_model_id", "binding_type", "binding_view_types", "xml_id"],
        },
        "ir.actions.server": {
            fields: ["name", "type", "model_id", "state", "crud_model_id", "link_field_id", "binding_model_id", "binding_type", "binding_view_types", "xml_id"],
        },
        "ir.actions.act_url": {
            fields: ["name", "type", "target", "binding_model_id", "binding_type", "xml_id"],
        },
        "ir.actions.client": {
            fields: ["name", "type", "tag", "target", "binding_model_id", "binding_type", "xml_id"],
        },
        "ir.actions.report": {
            fields: ["name", "type", "model", "report_type", "report_name", "report_file", "print_report_name", "paperformat_id", "attachment_use", "multi", "groups_id", "binding_model_id", "binding_type", "binding_view_types", "xml_id"],
        },
        "report.paperformat": {
            fields: ["name", "format", "page_height", "page_width", "orientation", "margin_top", "margin_bottom", "margin_left", "margin_right", "header_line", "header_spacing", "dpi", "css_margins", "disable_shrinking", "xml_id"],
        },
        "ir.model.access": {
            fields: ["name", "active", "model_id", "group_id", "perm_read", "perm_write", "perm_create", "perm_unlink", "xml_id"],
        },
        "ir.rule": {
            fields: ["name", "active", "model_id", "domain_force", "groups", "global", "perm_read", "perm_write", "perm_create", "perm_unlink", "xml_id"],
        },
        "res.groups": {
            fields: ["name", "category_id", "privilege_id", "comment", "implied_ids", "share", "xml_id"],
        },
        "ir.module.category": {
            fields: ["name", "parent_id", "sequence", "visible", "exclusive", "xml_id"],
        },
        "base.automation": {
            fields: ["name", "active", "model_id", "trigger", "trg_date_id", "trg_date_range", "trg_date_range_type", "filter_pre_domain", "filter_domain", "action_server_ids", "last_run", "xml_id"],
        },
        "ir.cron": {
            fields: ["name", "active", "user_id", "interval_number", "interval_type", "priority", "model_id", "state", "ir_actions_server_id", "xml_id"],
        },
        "mail.template": {
            fields: ["name", "model_id", "lang", "auto_delete", "use_default_to", "report_template_ids", "mail_server_id", "xml_id"],
        },
        "ir.sequence": {
            fields: ["name", "active", "code", "implementation", "prefix", "suffix", "padding", "number_increment", "use_date_range", "company_id", "xml_id"],
        },
        "ir.sequence.date_range": {
            fields: ["sequence_id", "date_from", "date_to"],
        },
        "ir.model.data": {
            fields: ["name", "module", "model", "res_id", "noupdate", "complete_name"],
        },
        "res.lang": {
            domain: [["active", "=", true]],
            fields: ["name", "code", "iso_code", "url_code", "active", "direction", "date_format", "time_format"],
        },
    };

    let requestId = 1;
    const call = async (model, method, args = [], kwargs = {}) => {
        const response = await fetch(`/web/dataset/call_kw/${model}/${method}`, {
            method: "POST",
            credentials: "same-origin",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {model, method, args, kwargs},
                id: requestId++,
            }),
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const payload = await response.json();
        if (payload.error) {
            throw new Error(payload.error.data?.message || payload.error.message || "Odoo RPC error");
        }
        return payload.result;
    };

    const readModel = async (model, spec) => {
        const available = await call(model, "fields_get", [], {attributes: ["type", "string"]});
        const fields = (spec.fields || []).filter((field) => field in available);
        const records = [];
        const domain = spec.domain || [];
        let offset = 0;
        while (true) {
            const page = await call(model, "search_read", [domain], {
                fields,
                offset,
                limit: 500,
                order: "id",
            });
            records.push(...page);
            if (page.length < 500) {
                break;
            }
            offset += page.length;
        }
        return {
            available_fields: Object.keys(available).sort(),
            selected_fields: fields,
            records,
        };
    };

    const result = {
        audit_version: 1,
        created_at: new Date().toISOString(),
        source: {
            host: location.hostname,
            database: null,
            server_version: "18.0-20251222",
        },
        datasets: {},
        errors: [],
    };

    console.log("РЕПКА: аудит начат. Не закрывайте вкладку.");
    for (const [model, spec] of Object.entries(specs)) {
        try {
            result.datasets[model] = await readModel(model, spec);
            console.log(`${model}: ${result.datasets[model].records.length}`);
        } catch (error) {
            const message = String(error.message || error).split("\n")[0].slice(0, 300);
            result.errors.push({model, error: message});
            console.warn(`${model}: недоступно (${message})`);
        }
    }

    const timestamp = new Date().toISOString().replaceAll(":", "-").replaceAll(".", "-");
    const filename = `repka_odoo_audit_${timestamp}.json`;
    const blob = new Blob([JSON.stringify(result, null, 2)], {type: "application/json"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);

    alert(`Аудит РЕПКА завершён. Файл ${filename} сохранён в Загрузки.`);
})();
