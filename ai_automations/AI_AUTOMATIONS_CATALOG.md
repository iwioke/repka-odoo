# Каталог Repka AI Automations

`DEMO` означает исполняемые, протестированные сценарии на синтетических JSON с детерминированными правилами; это НЕ генеративный AI, не live-интеграция и не подтверждённая экономия. `BLOCKED` означает идею, а не работающий продукт. `IMPLEMENTED` намеренно не применяется к автономным примерам. Поля моделей подтверждены исходниками, но наличие реальных записей и их качество не подтверждены.

| # | Scenario | Department | Value | Complexity | Status |
|---|---|---|---|---|---|
| 1 | Customer 360 / reactivation | CRM | HIGH | LOW | DEMO |
| 2 | Freight margin watch | Sales / Finance | HIGH | MEDIUM | DEMO |
| 3 | Document readiness | Documents / Logistics | HIGH | LOW | DEMO |
| 4 | Executive brief | Management | HIGH | MEDIUM | DEMO |
| 5 | Lead scoring / qualification | CRM | MEDIUM | HIGH | BLOCKED |
| 6 | Next best action / follow-up | CRM | MEDIUM | MEDIUM | BLOCKED |
| 7 | Lost reason / conversion forecast | CRM | MEDIUM | HIGH | BLOCKED |
| 8 | Upsell / cross-sell | Sales | MEDIUM | HIGH | BLOCKED |
| 9 | Sales / revenue forecast | Sales | HIGH | HIGH | BLOCKED |
| 10 | Discount / pricing optimization | Sales | MEDIUM | HIGH | BLOCKED |
| 11 | Cancellation risk / order anomaly | Sales | MEDIUM | HIGH | BLOCKED |
| 12 | Customer churn / lifetime value | CRM | HIGH | HIGH | BLOCKED |
| 13 | Demand / stockout / excess forecast | Inventory | MEDIUM | HIGH | BLOCKED |
| 14 | Slow-moving / dead stock | Inventory | MEDIUM | MEDIUM | BLOCKED |
| 15 | Purchase recommendation | Procurement | MEDIUM | HIGH | BLOCKED |
| 16 | Supplier quality / delay forecast | Procurement | MEDIUM | HIGH | BLOCKED |
| 17 | Cash-flow / expense anomalies | Finance | HIGH | HIGH | BLOCKED |
| 18 | OCR / extraction / comparison | Documents | HIGH | HIGH | BLOCKED |
| 19 | Incoming mail routing / draft reply | Communications | MEDIUM | HIGH | BLOCKED |
| 20 | Task extraction from messages | Tasks | MEDIUM | MEDIUM | BLOCKED |
| 21 | Natural-language analytics | BI | MEDIUM | HIGH | BLOCKED |
| 22 | Fleet breakdown / fuel anomaly | Fleet | HIGH | HIGH | BLOCKED |
| 23 | Manager quality analysis | Management | MEDIUM | HIGH | BLOCKED |

## Оценка четырёх исполняемых демонстраций

| Критерий | Customer 360 | Freight margin watch | Document readiness | Executive brief |
|---|---|---|---|---|
| Описание | Профиль заказчика и давность заказа | Пороговая проверка экономики экспедирования | Проверка статусов пакета документов | Сводный обзор действий |
| Проблема | История клиента разбросана | Отрицательный результат незаметен | Пакет закрывают с пробелами | Несколько экранов для контроля |
| Данные | Партнёры, заказы, даты, оплата | Выручка и себестоимость в одной валюте | Статусы проверок и типы документов | Результаты трёх сценариев |
| Odoo-модели (для будущего live) | `res.partner`, `ufs.base.order` | `ufs.base.order`, `ufs.forwarder.order` | `ufs.ai.document.check`, `ufs.transport.document` | модели трёх сценариев |
| Запуск | CLI вручную | CLI вручную | CLI вручную | CLI вручную |
| AI-логика | НЕТ модели: сегментация правилами | НЕТ модели: сравнение и порог | НЕТ модели: набор правил | НЕТ модели: агрегация |
| Результат | Заказы, оплата, окно реакции | Список отклонений с причинами | Недостающие/заблокированные проверки | Краткие KPI и задачи |
| Полностью автоматизируемо | Сбор и вычисление на доступных данных | Вычисление и уведомление | Формирование списка замечаний | Расчёт сводки |
| Человек подтверждает | Контакт и отправку сообщения | Проверку исходной себестоимости | Исправление и закрытие заказа | Управленческое решение |
| Потенциал экономии времени | Сбор истории вручную; не измерен | Поиск проблем вручную; не измерен | Просмотр перечня; не измерен | Подготовка обзора; не измерен |
| Ценность | HIGH | HIGH | HIGH | HIGH |
| Сложность | LOW | MEDIUM | LOW | MEDIUM |
| Риски | Неполная история | Валюты/косвенные расходы | Неравнозначность статуса и юридической проверки | Ложное чувство полноты |
| Ограничения | Нет CRM переписки | Нет проводок, налогов, прогноза | Нет OCR/сканов | Нет live KPI |
| Плюсы | Прозрачные причины | Выделяет кандидатов на аудит | Не разрешает закрытие | Единый контекст |
| Минусы | Эвристика вместо вероятности | Не бухгалтерская маржа | Синтетические статусы | Не интерактивный BI |

Остальные сценарии и 17 критериев для каждого приведены в [future/README.md](future/README.md). Технические детали, доказательства и порядок запуска — в корневом README и документации сценариев.
