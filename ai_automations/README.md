# Repka AI Automations — исследование и исполняемые DEMO

**Важно:** 4 запускаемых сценария применяют детерминированные правила к синтетическим данным. Это не обученные AI-модели, не OCR, не автономные действия в Odoo и не подтверждённые бизнес-результаты. LIVE MODE не настроен и при вызове явно выдаёт ошибку. Существующий в Odoo `repka_ai_document_check` — отдельный детерминированный mock; его код не менялся.

## Что где лежит

- `scenarios/` — четыре запускаемых демонстрации; в каждой свои инструкция и примеры.
- `catalog/` — полный список идей и раздел `future/` с условиями для следующих этапов.
- `presentation/` — готовая презентация для показа.
- `run_all.py` — единая точка запуска; технические файлы и тесты спрятаны в `.internal/`.

## Быстрый старт

Нужен только Python 3.9+; `pip install` не требуется. Из корня репозитория:

```sh
python3 ai_automations/run_all.py --list
python3 ai_automations/run_all.py customer_360
python3 ai_automations/run_all.py margin_watch
python3 ai_automations/run_all.py document_readiness
python3 ai_automations/run_all.py executive_brief
```

Без аргументов в интерактивном терминале предлагается выбор номера; в неинтерактивной среде выводится список. Каждый сценарий отдельно: `python3 ai_automations/scenarios/customer_360/run.py` (аналогично для других). `--input /path/to/synthetic.json` заменяет пример; файл должен соответствовать JSON-схеме из примера и не превышать 1 МБ. CLI ничего не записывает; JSON выводится в stdout. `--mode live` отклоняется (не заменяется на demo).

| Название | Точка запуска | Суть | Режим |
|---|---|---|---|
| Customer 360 | `scenarios/customer_360/run.py` | давность заказа и неоплаченные заказы | DEMO |
| Freight Margin Watch | `scenarios/margin_watch/run.py` | прямая разница выручки и затрат | DEMO |
| Document Readiness | `scenarios/document_readiness/run.py` | недостающие и проблемные статусы | DEMO |
| Executive Brief | `scenarios/executive_brief/run.py` | три счётчика для проверки | DEMO |

## Проверка

```sh
python3 -m unittest discover -s ai_automations/.internal/tests -v
```

Тесты сверяют сохранённые результаты каждого примера, повторяемость, ошибки ввода, закрытый LIVE MODE и launcher. Документы discovery: `docs/ai-automations/PRD.md`, `docs/ai-automations/ARCHITECTURE.md`. Полная оценка идей: `catalog/AI_AUTOMATIONS_CATALOG.md`; блокеры: `catalog/future/README.md`. Для business demo презентация лежит в `presentation/`.

## Итог аудита

- `addons/repka_suite/__manifest__.py`: стандартные CRM, sale, stock, purchase, account и логистические модули включены в зависимости; это не свидетельствует об использовании конкретных потоков на реальных данных.
- `addons/repka_logistics_core/models/order.py`: заказ, клиент, даты, freight amount, оплата, стадия. `addons/repka_forwarding/models/misc.py`: экспедиторский заказ, подзаказы, стоимость, доходность; `addons/repka_fleet/models/`: рейсы, затраты и путевые листы.
- `addons/repka_ai_document_check/models/ai_document_check.py`: очередь cron, HTTP-запрос в сервис, поля результатов, право менеджера на override. `services/ai_document_check_mock/server.py`: результат строится по имени файла, не по OCR содержимому.
- `compose.yaml` / `compose.dev.yaml` / `compose.prod.yaml`: Odoo и PostgreSQL в Docker, отдельный внутренний mock. Права задаются Odoo группами/ACL; общего проверенного сервиса read-only AI-аналитики нет.
- Текущие данные в Odoo не выгружались. Реальная доступность API для отдельного сервиса, объём выборки, права и пригодность данных для ML не установлены. Доступны лишь подтверждённые определения полей и изолированные синтетические входы.

## Безопасность и границы

Не подключайте production JSON с персональными данными к демонстрационному CLI. Нет внешних запросов, секретов, хранения результатов, записи в БД, массовых отправок или автоматического принятия решений. Не смешивайте валюты или выручку с прибылью. Для live-пилота согласуйте API, ограниченные права и ACL, источник затрат, защиту данных, аудит, проверочные наборы и ручное подтверждение.
