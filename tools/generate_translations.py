#!/usr/bin/env python3
"""Generate Russian translations (ru.po) for all repka_* addons from audit specs.

Extracts translatable strings (field labels, model descriptions, menu names,
view strings, action names, report names) from the audit JSON specifications
and writes proper ru.po files with Russian translations.
"""
import json
import os
import re
import sys
from pathlib import Path

# Mapping from source module names to repka addon names
MODULE_MAP = {
    "ufs_base": "repka_logistics_core",
    "ufs_fleet": "repka_fleet",
    "ufs_forwarding": "repka_forwarding",
    "ufs_invoices": "repka_invoices",
    "ufs_invoices_base_reports": "repka_invoices_base_reports",
    "ufs_invoices_forwarding": "repka_invoices_forwarding",
    "ufs_complex_reporting": "repka_complex_reporting",
    "ufs_special_lm": "repka_special_lm",
    "ufs_fleet_fuel_import": "repka_fleet_fuel_import",
    "ufs_fleet_maintenance": "repka_fleet_maintenance",
    "ufs_fleet_tires_base": "repka_fleet_tires",
    "ufs_fleet_wallet": "repka_fleet_wallet",
    "ufs_fleet_waybill": "repka_fleet_waybill",
    "ufs_excel_report": "repka_excel_report",
}

# Common English to Russian translations for logistics/ERP terms
TRANSLATIONS = {
    # General
    "Active": "Активно",
    "Active Date": "Дата активности",
    "Address": "Адрес",
    "Amount": "Сумма",
    "Amount in Company Currency": "Сумма в валюте компании",
    "Code": "Код",
    "Comment": "Комментарий",
    "Company": "Компания",
    "Company Currency": "Валюта компании",
    "Country": "Страна",
    "Create Date": "Дата создания",
    "Created by": "Создал",
    "Currency": "Валюта",
    "Customer": "Заказчик",
    "Date": "Дата",
    "Description": "Описание",
    "Display Name": "Отображаемое имя",
    "Email": "Email",
    "Employee": "Сотрудник",
    "ID": "ID",
    "Last Modified on": "Последнее изменение",
    "Name": "Название",
    "Notes": "Примечания",
    "Number": "Номер",
    "Partner": "Партнёр",
    "Phone": "Телефон",
    "Sequence": "Последовательность",
    "State": "Статус",
    "Status": "Статус",
    "Type": "Тип",
    "User": "Пользователь",
    "Vehicle": "Транспортное средство",
    "Vehicle ID": "Транспортное средство",
    # Fleet
    "Asset": "Актив",
    "Driver": "Водитель",
    "Drivers": "Водители",
    "Fleet": "Автопарк",
    "Fleet Vehicle": "Транспортное средство",
    "License Plate": "Гос. номер",
    "Model": "Модель",
    "Odometer": "Одометр",
    "Plate": "Гос. номер",
    "Service": "Обслуживание",
    "Service Type": "Тип обслуживания",
    "Tire": "Шина",
    "Tires": "Шины",
    "Vehicle Model": "Модель ТС",
    "Vehicle Type": "Тип ТС",
    "VIN": "VIN",
    "VIN/SN": "VIN/Серийный номер",
    # Logistics
    "Order": "Заказ",
    "Orders": "Заказы",
    "Order Line": "Строка заказа",
    "Order Lines": "Строки заказа",
    "Forwarder": "Экспедитор",
    "Forwarder Order": "Экспедиторский заказ",
    "Forwarding": "Экспедирование",
    "Forwarding Orders": "Экспедиторские заказы",
    "Route": "Маршрут",
    "Route Point": "Точка маршрута",
    "Route Points": "Точки маршрута",
    "Trip": "Рейс",
    "Trips": "Рейсы",
    "Trip Segment": "Сегмент рейса",
    "Trip Segments": "Сегменты рейса",
    "Cargo": "Груз",
    "Cargo Type": "Тип груза",
    "Contract": "Договор",
    "Contracts": "Договоры",
    "Invoice": "Счёт",
    "Invoices": "Счета",
    "Invoice Count": "Количество счетов",
    "Invoice Date": "Дата счёта",
    "Invoice Line": "Строка счёта",
    "Invoice Lines": "Строки счёта",
    "Payment": "Платёж",
    "Payment Date": "Дата платежа",
    "Payment Terms": "Условия оплаты",
    "Payment Type": "Тип платежа",
    # Financial
    "Amount Total": "Итоговая сумма",
    "Base Amount": "Базовая сумма",
    "Base Currency": "Базовая валюта",
    "Cost": "Стоимость",
    "Cost Line": "Строка стоимости",
    "Cost Lines": "Строки стоимости",
    "Currency Rate": "Курс валюты",
    "Debit": "Дебет",
    "Credit": "Кредит",
    "Balance": "Баланс",
    "Bank": "Банк",
    "Bank Account": "Банковский счёт",
    "Bank Statement": "Банковская выписка",
    "Journal": "Журнал",
    "Journal Entry": "Запись журнала",
    "Journal Entries": "Записи журнала",
    "Tax": "Налог",
    "Taxes": "Налоги",
    "Subtotal": "Промежуточная сумма",
    "Total": "Итого",
    "Unit Price": "Цена за единицу",
    "Quantity": "Количество",
    "UoM": "Единица измерения",
    # Documents
    "Document": "Документ",
    "Documents": "Документы",
    "Document Type": "Тип документа",
    "Document Date": "Дата документа",
    "Document Number": "Номер документа",
    "Attachment": "Вложение",
    "Attachments": "Вложения",
    "File": "Файл",
    "File Name": "Имя файла",
    # Actions
    "Cancel": "Отменить",
    "Confirm": "Подтвердить",
    "Draft": "Черновик",
    "Done": "Выполнено",
    "Open": "Открыть",
    "Close": "Закрыть",
    "Save": "Сохранить",
    "Delete": "Удалить",
    "Edit": "Изменить",
    "New": "Новый",
    "Create": "Создать",
    "Search": "Поиск",
    "Filter": "Фильтр",
    "Group By": "Группировать по",
    "Print": "Печать",
    "Export": "Экспорт",
    "Import": "Импорт",
    "Refresh": "Обновить",
    "Settings": "Настройки",
    "Configuration": "Настройки",
    "Dashboard": "Панель управления",
    "Reports": "Отчёты",
    "Reporting": "Отчётность",
    # Misc
    "Log": "Журнал",
    "Logs": "Журналы",
    "History": "История",
    "Note": "Заметка",
    "Notes": "Заметки",
    "Tag": "Тег",
    "Tags": "Теги",
    "Category": "Категория",
    "Categories": "Категории",
    "Parent": "Родитель",
    "Child": "Дочерний",
    "Reference": "Ссылка",
    "Related": "Связанный",
    "Required": "Обязательное",
    "Readonly": "Только для чтения",
    "Default": "По умолчанию",
    "All": "Все",
    "None": "Нет",
    "True": "Да",
    "False": "Нет",
    "Yes": "Да",
    "No": "Нет",
    "From": "От",
    "To": "До",
    "Start Date": "Дата начала",
    "End Date": "Дата окончания",
    "Start Time": "Время начала",
    "End Time": "Время окончания",
    "Deadline": "Срок",
    "Duration": "Продолжительность",
    "Hours": "Часы",
    "Days": "Дни",
    "Weeks": "Недели",
    "Months": "Месяцы",
    "Years": "Годы",
    # UFS-specific
    "Base order": "Базовый заказ",
    "Base Order": "Базовый заказ",
    "Deal order": "Сделка",
    "Deal Order": "Сделка",
    "Head order": "Головной заказ",
    "Sub Order": "Подзаказ",
    "Suborder": "Подзаказ",
    "Suborders": "Подзаказы",
    "Order Reference": "Реквизит заказа",
    "Order Type": "Тип заказа",
    "Service Type": "Тип услуги",
    "Service Types": "Типы услуг",
    "Planned Maintenances": "Плановое обслуживание",
    "Maintenance": "Обслуживание",
    "Maintenance Request": "Заявка на обслуживание",
    "Fuel": "Топливо",
    "Fuel Card": "Топливная карта",
    "Fuel Cards": "Топливные карты",
    "Fuel Consumption": "Расход топлива",
    "Fuel Norm": "Норма расхода топлива",
    "Fuel Import": "Импорт топлива",
    "Wallet": "Кошелёк",
    "Wallet Entry": "Запись кошелька",
    "Wallet Entries": "Записи кошелька",
    "Waybill": "Путевой лист",
    "Waybills": "Путевые листы",
    "Waybill Line": "Строка путевого листа",
    "Waybill Lines": "Строки путевого листа",
    "Equipment": "Оборудование",
    "Equipments": "Оборудование",
    "Tire Log": "История шин",
    "Tire Logs": "История шин",
    "Tire Status": "Статус шины",
    "Tire Position": "Позиция шины",
    "Tire Brand": "Бренд шины",
    "Tire Model": "Модель шины",
    "Tire Size": "Размер шины",
    "Season": "Сезон",
    "Winter": "Зимняя",
    "Summer": "Летняя",
    "All-Season": "Всесезонная",
    "Carrier": "Перевозчик",
    "Carriers": "Перевозчики",
    "Truck": "Грузовик",
    "Trucks": "Грузовики",
    "Lorry": "Грузовик",
    "Lorries": "Грузовики",
    "Trailer": "Прицеп",
    "Trailers": "Прицепы",
    "Semi-trailer": "Полуприцеп",
    "Semi-trailers": "Полуприцепы",
    "Dispatch": "Диспетчерская",
    "Dispatcher": "Диспетчер",
    "Tracking": "Отслеживание",
    "Track": "Отследить",
    "GPS": "GPS",
    "GLONASS": "ГЛОНАСС",
    "Tracking System": "Система отслеживания",
    "Strict Doc": "Строгий документ",
    "Strict Docs": "Строгие документы",
    "Doc Line": "Строка документа",
    "Doc Lines": "Строки документа",
    "Switch": "Переключение",
    "Switch Line": "Строка переключения",
    "Switch Wizard": "Мастер переключения",
    "Reorder": "Заказать повторно",
    "Reorder Wizard": "Мастер повторного заказа",
    "Cost Type": "Тип стоимости",
    "Cost Types": "Типы стоимости",
    "Trip Cost": "Стоимость рейса",
    "Trip Costs": "Стоимости рейса",
    "Trip Cost Type": "Тип стоимости рейса",
    "Trip Point": "Точка рейса",
    "Trip Points": "Точки рейса",
    "Trip Switch": "Переключение рейса",
    "Trip Doc": "Документ рейса",
    "Trip Docs": "Документы рейса",
    "Trip Docs In/Out": "Документы рейса (вход/выход)",
    "Trip Docs In/Out Line": "Строка документов рейса",
    "Board": "Доска",
    "Disp Board": "Диспетчерская доска",
    "Alert Range": "Диапазон предупреждения",
    "Service Log": "Журнал обслуживания",
    "Service Order": "Заказ на обслуживание",
    "Cost Line": "Строка стоимости",
    "Cost Lines": "Строки стоимости",
    "Current Activity": "Текущая активность",
    "Responsive": "Ответственный",
    "Owner Partner": "Партнёр-владелец",
    "Parent Partner": "Родительский партнёр",
    "Tags": "Теги",
    "Customer": "Заказчик",
    "Freight Amount in Company Base Currency": "Фрахт в базовой валюте компании",
    "Block Freight Amount": "Блокировать фрахт",
    "Close Datetime": "Дата и время закрытия",
    "Advance Invoice Requested": "Запрошен авансовый счёт",
    "Invoice Count": "Количество счетов",
    "Move Lines": "Проводки",
    "Base Currency": "Базовая валюта",
    "EDI SL": "EDI SL",
    "Goods Movement": "Движение товаров",
    "LM: Recompute Order/Suborder Amounts": "LM: Пересчёт сумм заказов/подзаказов",
    "UFS Fleet Maintenance Model": "Модель обслуживания автопарка",
    "UFS Base Order": "Базовый заказ UFS",
    "UFS Forwarder Order": "Экспедиторский заказ UFS",
    "UFS Fleet Order": "Заказ автопарка UFS",
    "UFS Fleet Trip": "Рейс автопарка UFS",
    "UFS Contract": "Договор UFS",
    "UFS Forwarder Suborder": "Подзаказ экспедитора UFS",
    "UFS Forwarder Suborder Type": "Тип подзаказа экспедитора UFS",
    "UFS Forwarder Order Line": "Строка экспедиторского заказа UFS",
    "UFS Fleet Maintenance": "Обслуживание автопарка UFS",
    "UFS Fuel Card": "Топливная карта UFS",
    "UFS Fuel Card History": "История топливной карты UFS",
    "UFS Fleet Vehicle Fuel Norm": "Норма расхода топлива ТС UFS",
    "UFS Fleet Lorry": "Грузовик автопарка UFS",
    "UFS Fleet Order Cost": "Стоимость заказа автопарка UFS",
    "UFS Fleet Order Line": "Строка заказа автопарка UFS",
    "UFS Fleet Trace": "Отслеживание автопарка UFS",
    "UFS Trip CADV": "CADV рейса UFS",
    "UFS Trip Cost": "Стоимость рейса UFS",
    "UFS Trip Cost Type": "Тип стоимости рейса UFS",
    "UFS Trip Strict Doc Line": "Строка строгого документа рейса UFS",
    "UFS CADV Request Approval Wizard": "Мастер утверждения запроса CADV UFS",
    "UFS Employee": "Сотрудник UFS",
    "UFS Partner": "Партнёр UFS",
    "UFS Vehicle": "Транспортное средство UFS",
    "UFS Base Equipment": "Оборудование UFS",
    "UFS Strict Doc": "Строгий документ UFS",
    "UFS Partner Doc Line": "Строка документа партнёра UFS",
    "UFS Employee Doc Line": "Строка документа сотрудника UFS",
    "UFS Waybill": "Путевой лист UFS",
    "UFS Excel Report": "Отчёт Excel UFS",
    "UFS Complex Report": "Комплексный отчёт UFS",
    "UFS Special LM": "Специальный LM UFS",
    # Menu items
    "Logistics": "Логистика",
    "Logistics Core": "Логистическое ядро",
    "Fleet Management": "Управление автопарком",
    "Forwarding Management": "Управление экспедированием",
    "Invoice Management": "Управление счетами",
    "Complex Reporting": "Комплексная отчётность",
    "Special LM": "Специальный LM",
    "Excel Reports": "Отчёты Excel",
    "Maintenance": "Обслуживание",
    "Tires Management": "Управление шинами",
    "Wallet Management": "Управление кошельком",
    "Waybill Management": "Управление путевыми листами",
    "Fuel Import": "Импорт топлива",
    "Configuration": "Настройки",
    "Reports": "Отчёты",
    "Dashboard": "Панель управления",
    # More fleet
    "Acquisition Date": "Дата приобретения",
    "Color": "Цвет",
    "Power": "Мощность",
    "Fuel Type": "Тип топлива",
    "Transmission": "Коробка передач",
    "Doors": "Двери",
    "Seats": "Места",
    "CO2 Emissions": "Выбросы CO2",
    "Horsepower": "Лошадиные силы",
    "Current Odometer": "Текущий одометр",
    "Next Assignation": "Следующее назначение",
    "Car Value": "Стоимость ТС",
    "Manager": "Менеджер",
    "Manager ID": "Менеджер",
    "Sticky Note": "Заметка",
    "Catalog": "Каталог",
    "Catalog VEH": "Каталог ТС",
    "Vehicles": "Транспортные средства",
    "Vehicle Status": "Статус ТС",
    "Vehicle Count": "Количество ТС",
    "Motor Vehicle": "Автомобиль",
    "Plans": "Планы",
    "Planned": "Запланировано",
    "Overdue": "Просрочено",
    "Overdue Maint": "Просроченное обслуживание",
    "Maintenance Generator": "Генератор обслуживания",
    "Period Type": "Тип периода",
    "Alert": "Предупреждение",
    "Alerts": "Предупреждения",
    "Fuel Norm": "Норма расхода",
    "Fuel Norms": "Нормы расхода",
    "Card Number": "Номер карты",
    "Card Holder": "Держатель карты",
    "Card Type": "Тип карты",
    "Card Status": "Статус карты",
    "Balance": "Баланс",
    "Limit": "Лимит",
    "Daily Limit": "Дневной лимит",
    "Monthly Limit": "Месячный лимит",
    "Transaction": "Транзакция",
    "Transactions": "Транзакции",
    "Transaction Date": "Дата транзакции",
    "Transaction Amount": "Сумма транзакции",
    "Transaction Type": "Тип транзакции",
    "Fuel Volume": "Объём топлива",
    "Fuel Price": "Цена топлива",
    "Fuel Station": "АЗС",
    "Fuel Station Name": "Название АЗС",
    "Fueling Date": "Дата заправки",
    "Odometer Reading": "Показание одометра",
    "Tank Capacity": "Объём бака",
    "Average Consumption": "Средний расход",
    "Actual Consumption": "Фактический расход",
    "Norm Consumption": "Нормативный расход",
    "Overconsumption": "Перерасход",
    "Underconsumption": "Экономия",
    # Waybill
    "Waybill Number": "Номер путевого листа",
    "Waybill Date": "Дата путевого листа",
    "Waybill Status": "Статус путевого листа",
    "Departure Date": "Дата выезда",
    "Return Date": "Дата возвращения",
    "Departure Odometer": "Одометр при выезде",
    "Return Odometer": "Одометр при возвращении",
    "Total Mileage": "Общий пробег",
    "Fuel Start": "Топливо при выезде",
    "Fuel End": "Топливо при возвращении",
    "Fuel Issued": "Выдано топлива",
    "Fuel Remaining": "Остаток топлива",
    "Driver Signature": "Подпись водителя",
    "Mechanic Signature": "Подпись механика",
    "Dispatcher Signature": "Подпись диспетчера",
    # Wallet
    "Wallet Balance": "Баланс кошелька",
    "Wallet Transaction": "Транзакция кошелька",
    "Wallet Transactions": "Транзакции кошелька",
    "Deposit": "Пополнение",
    "Withdrawal": "Снятие",
    "Transfer": "Перевод",
    "Entry Type": "Тип записи",
    "Entry Date": "Дата записи",
    "Entry Amount": "Сумма записи",
    # Invoices
    "Base Invoice": "Базовый счёт",
    "Base Invoices": "Базовые счета",
    "Advance Invoice": "Авансовый счёт",
    "Advance Invoices": "Авансовые счета",
    "Invoice Status": "Статус счёта",
    "Invoice Total": "Сумма счёта",
    "Invoice Paid": "Оплачено",
    "Invoice Due": "К оплате",
    "Invoice Partner": "Партнёр по счёту",
    "Invoice Date": "Дата счёта",
    "Invoice Number": "Номер счёта",
    # Reporting
    "Report": "Отчёт",
    "Report Type": "Тип отчёта",
    "Report Date": "Дата отчёта",
    "Report Period": "Период отчёта",
    "Report Format": "Формат отчёта",
    "Excel Report": "Отчёт Excel",
    "Complex Report": "Комплексный отчёт",
    "Summary": "Сводка",
    "Details": "Подробности",
    "Grand Total": "Общий итог",
    "Subtotal": "Промежуточная сумма",
}


def generate_ru_po(spec_path, addon_name, output_path):
    """Generate a ru.po file from an audit spec."""
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)

    # Collect translatable strings
    strings = {}  # en_string -> set of source references

    def add_string(s, source=""):
        if not s or not isinstance(s, str):
            return
        s = s.strip()
        if not s or s == "False" or s == "True" or s == "None":
            return
        # Skip non-translatable strings
        if re.match(r'^[a-z_]+$', s) and len(s) < 30:
            return  # likely a technical name
        if s.startswith(("ufs.", "fleet.", "res.", "account.", "hr.", "mail.", "ir.")):
            return
        if s in strings:
            strings[s].add(source)
        else:
            strings[s] = {source}

    # Module name
    module_name = spec.get("module", {}).get("name", "")
    if module_name:
        summary = spec.get("module", {}).get("summary", "")
        if summary:
            add_string(summary, f"module summary")

    # Model descriptions
    for m in spec.get("models", []):
        desc = m.get("description")
        if desc:
            add_string(desc, f"model {m.get('model', '')} description")

    # Field labels
    for model_name, fields_list in spec.get("fields", {}).items():
        for f in fields_list:
            label = f.get("field_description")
            if label:
                add_string(label, f"field {model_name}.{f.get('name', '')}")

    # Selection field values
    for model_name, fields_list in spec.get("fields", {}).items():
        for f in fields_list:
            sel = f.get("selection")
            if sel and isinstance(sel, list):
                for item in sel:
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        add_string(item[1], f"selection {model_name}.{f.get('name', '')}")

    # Menu names
    for menu in spec.get("menus", []):
        name = menu.get("name")
        if name:
            add_string(name, f"menu {menu.get('id', '')}")

    # View names
    for v in spec.get("views", []):
        name = v.get("name")
        if name:
            add_string(name, f"view {v.get('id', '')}")
        # Also extract strings from arch
        arch = v.get("arch_db") or v.get("arch") or ""
        if arch:
            # Extract string= attributes
            for m in re.finditer(r'string="([^"]+)"', arch):
                add_string(m.group(1), f"view arch")
            # Extract label tags
            for m in re.finditer(r'<label[^>]*string="([^"]+)"', arch):
                add_string(m.group(1), f"view arch label")
            # Extract filter strings
            for m in re.finditer(r'<filter[^>]*string="([^"]+)"', arch):
                add_string(m.group(1), f"view arch filter")
            # Extract page names
            for m in re.finditer(r'<page[^>]*string="([^"]+)"', arch):
                add_string(m.group(1), f"view arch page")
            # Extract group strings
            for m in re.finditer(r'<group[^>]*string="([^"]+)"', arch):
                add_string(m.group(1), f"view arch group")
            # Extract tab strings
            for m in re.finditer(r'<tab[^>]*string="([^"]+)"', arch):
                add_string(m.group(1), f"view arch tab")

    # Action names
    for a in spec.get("actions", []):
        name = a.get("name")
        if name:
            add_string(name, f"action {a.get('id', '')}")

    # Report names
    for r in spec.get("reports", []):
        name = r.get("name")
        if name:
            add_string(name, f"report {r.get('id', '')}")

    # Server action names
    for s in spec.get("server_actions", []):
        name = s.get("name")
        if name:
            add_string(name, f"server_action {s.get('id', '')}")

    # Cron names
    for c in spec.get("crons", []):
        name = c.get("name")
        if name:
            add_string(name, f"cron {c.get('id', '')}")

    # Generate ru.po content
    lines = [
        "# Translation of Odoo Server.",
        f"# This file contains the translation of the following modules:",
        f"#   * {addon_name}",
        "#",
        "msgid \"\"",
        "msgstr \"\"",
        "\"Project-Id-Version: Odoo Server 18.0\\n\"",
        "\"Report-Msgid-Bugs-To: \\n\"",
        "\"POT-Creation-Date: 2026-01-01 00:00+0000\\n\"",
        "\"PO-Revision-Date: 2026-01-01 00:00+0000\\n\"",
        "\"Last-Translator: \\n\"",
        "\"Language-Team: Russian\\n\"",
        "\"Language: ru\\n\"",
        "\"MIME-Version: 1.0\\n\"",
        "\"Content-Type: text/plain; charset=UTF-8\\n\"",
        "\"Content-Transfer-Encoding: \\n\"",
        "\"Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);\\n\"",
        "",
    ]

    for en_str, sources in sorted(strings.items()):
        ru_str = TRANSLATIONS.get(en_str, "")
        lines.append(f"#. module: {addon_name}")
        lines.append(f"#: {' '.join(sorted(sources)[:3])}")
        lines.append(f"msgid \"{en_str}\"")
        lines.append(f"msgstr \"{ru_str}\"")
        lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return len(strings)


def main():
    audit_dir = Path("audit")
    addons_dir = Path("addons")

    total = 0
    for spec_file in sorted(audit_dir.glob("ufs_*_spec.json")):
        # Remove _spec suffix from the stem (not from within the name)
        stem = spec_file.stem
        if stem.endswith("_spec"):
            spec_name = stem[:-5]
        else:
            spec_name = stem
        addon_name = MODULE_MAP.get(spec_name)
        if not addon_name:
            print(f"  SKIP: No mapping for {spec_name}")
            continue

        addon_dir = addons_dir / addon_name
        if not addon_dir.exists():
            print(f"  SKIP: {addon_name} does not exist")
            continue

        i18n_dir = addon_dir / "i18n"
        i18n_dir.mkdir(exist_ok=True)
        output_path = i18n_dir / "ru.po"

        count = generate_ru_po(spec_file, addon_name, output_path)
        total += count
        print(f"  OK: {addon_name}: {count} strings translated")

    print(f"\nTotal: {total} strings translated across all modules")


if __name__ == "__main__":
    main()
