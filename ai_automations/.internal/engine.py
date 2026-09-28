import argparse
import json
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


SCENARIOS = {
    "customer_360": "Профиль клиента",
    "margin_watch": "Экономика перевозок",
    "document_readiness": "Готовность документов",
    "executive_brief": "Сводка руководителю",
}


def required(record, key, kind):
    if not isinstance(record, dict) or key not in record or not isinstance(record[key], kind) or (isinstance(record[key], bool) and kind is not bool):
        raise ValueError(f"Неверное или отсутствующее поле: {key}")
    return record[key]


def items(record, key):
    return required(record, key, list)


def day(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Неверная дата: {value}") from exc


def amount(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("Сумма должна быть числом")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Сумма должна быть числом") from exc
    if not number.is_finite() or number < 0:
        raise ValueError("Сумма должна быть конечным неотрицательным числом")
    return number


def customer_360(data):
    as_of = day(required(data, "as_of", str))
    orders = items(data, "orders")
    result = []
    ids = set()
    for partner in items(data, "partners"):
        identifier = required(partner, "id", int)
        name = required(partner, "name", str)
        if identifier in ids:
            raise ValueError("Повторяющийся id клиента")
        ids.add(identifier)
        history = []
        for order in orders:
            order_id = required(order, "id", int)
            partner_id = required(order, "partner_id", int)
            ordered_at = day(required(order, "order_date", str))
            paid = required(order, "is_paid", bool)
            if ordered_at > as_of:
                raise ValueError("Дата заказа позже даты среза")
            if partner_id == identifier:
                history.append((ordered_at, order_id, paid))
        latest = max(history) if history else None
        days = (as_of - latest[0]).days if latest else None
        result.append({"partner_id": identifier, "name": name, "orders": len(history),
                       "unpaid_orders": sum(not row[2] for row in history),
                       "days_since_last_order": days,
                       "attention": "review_reactivation" if days is not None and days >= 90 else "no_history" if days is None else "current",
                       "reason": "Нет истории заказов" if days is None else f"Последний заказ {days} дней назад"})
    if any(required(order, "partner_id", int) not in ids for order in orders):
        raise ValueError("Заказ с неизвестным клиентом")
    if len({order["id"] for order in orders}) != len(orders):
        raise ValueError("Повторяющийся id заказа")
    return {"customers": result, "review_reactivation": sum(row["attention"] == "review_reactivation" for row in result)}


def margin_watch(data):
    result = []
    ids = set()
    for order in items(data, "orders"):
        identifier = required(order, "id", int)
        if identifier in ids:
            raise ValueError("Повторяющийся id заказа")
        ids.add(identifier)
        name = required(order, "name", str)
        currency = required(order, "currency", str)
        cost_currency = required(order, "cost_currency", str)
        if currency != cost_currency or not currency:
            raise ValueError("Выручка и затраты должны быть в одной валюте")
        revenue = amount(required(order, "revenue", (str, int, float)))
        cost = amount(required(order, "direct_cost", (str, int, float)))
        difference = revenue - cost
        margin = difference / revenue * 100 if revenue else None
        level = "review" if difference < 0 or (margin is not None and margin < 10) else "ok"
        result.append({"id": identifier, "name": name, "currency": currency, "result": str(difference),
                       "margin_percent": str(margin.quantize(Decimal("0.01"))) if margin is not None else None,
                       "attention": level,
                       "reason": "Затраты выше выручки" if difference < 0 else "Низкая доля результата" if level == "review" else "Порог не нарушен"})
    return {"orders": result, "review_count": sum(row["attention"] == "review" for row in result),
            "note": "Оценка по прямым затратам; не бухгалтерская прибыль и не прогноз"}


def document_readiness(data):
    required_types = items(data, "required_types")
    if not required_types or any(not isinstance(t, str) or not t for t in required_types) or len(set(required_types)) != len(required_types):
        raise ValueError("Список необходимых типов документов должен быть уникальным и непустым")
    result = []
    ids = set()
    for order in items(data, "orders"):
        identifier = required(order, "id", int)
        if identifier in ids:
            raise ValueError("Повторяющийся id заказа")
        ids.add(identifier)
        docs = items(order, "checks")
        by_type = {}
        for check in docs:
            kind = required(check, "document_type", str)
            state = required(check, "state", str)
            if state not in ("queued", "processing", "completed", "attention", "blocked", "failed"):
                raise ValueError("Неизвестный статус проверки")
            by_type.setdefault(kind, []).append(state)
        missing = [kind for kind in required_types if kind not in by_type]
        issues = [kind for kind in required_types if kind in by_type and any(state != "completed" for state in by_type[kind])]
        status = "review" if missing or issues else "ready_for_human_review"
        result.append({"id": identifier, "missing": missing, "needs_review": issues, "status": status,
                       "reason": "Проверить недостающие или проблемные документы" if status == "review" else "Все типы имеют успешную проверку; оригиналы всё равно проверяет логист"})
    return {"orders": result, "review_count": sum(row["status"] == "review" for row in result)}


def executive_brief(data):
    customers = customer_360(required(data, "customer_data", dict))
    margins = margin_watch(required(data, "margin_data", dict))
    documents = document_readiness(required(data, "document_data", dict))
    return {"kpis": {"customers_to_review": customers["review_reactivation"],
                     "orders_with_margin_alert": margins["review_count"],
                     "orders_with_document_gaps": documents["review_count"]},
            "actions": [title for count, title in (
                (customers["review_reactivation"], "Проверить клиентов без недавних заказов"),
                (margins["review_count"], "Уточнить прямые затраты перевозок"),
                (documents["review_count"], "Проверить пакет документов с логистом")) if count],
            "note": "Показатели из отдельных синтетических срезов; не объединять суммы и не считать live KPI"}


FUNCTIONS = {"customer_360": customer_360, "margin_watch": margin_watch,
             "document_readiness": document_readiness, "executive_brief": executive_brief}


def run(scenario):
    parser = argparse.ArgumentParser(description=SCENARIOS[scenario] + " (DEMO)")
    parser.add_argument("--mode", choices=("demo", "live"), default="demo")
    parser.add_argument("--input", type=Path, default=Path(__file__).resolve().parent.parent / "scenarios" / scenario / "example_input.json")
    args = parser.parse_args()
    if args.mode == "live":
        parser.error("LIVE MODE не настроен: нужен согласованный API, права и проверка данных. Демо не запускается вместо live.")
    try:
        if args.input.stat().st_size > 1024 * 1024:
            raise ValueError("Файл больше 1 МБ")
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = FUNCTIONS[scenario](data)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError, TypeError, KeyError) as exc:
        parser.error(f"Ошибка входных данных: {exc}")
    print(json.dumps({"mode": "DEMO", "method": "deterministic_rules_not_llm", "scenario": scenario,
                      "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in FUNCTIONS:
        raise SystemExit("Используйте отдельный run.py из каталога сценария")
    scenario_name = sys.argv.pop(1)
    run(scenario_name)
