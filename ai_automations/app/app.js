const NAMES = {
  customer_360: 'Профиль клиента',
  margin_watch: 'Экономика перевозок',
  document_readiness: 'Готовность документов',
  executive_brief: 'Сводка руководителю',
  'future-lead-scoring-qualification': 'Оценка и отбор заявок',
  'future-next-best-action-follow-up': 'Следующее действие и напоминания',
  'future-lost-reason-conversion-forecast': 'Причины потерь и прогноз конверсии',
  'future-upsell-cross-sell': 'Дополнительные и сопутствующие услуги',
  'future-sales-revenue-forecast': 'Прогноз продаж и выручки',
  'future-discount-pricing-optimization': 'Контроль скидок и цен',
  'future-cancellation-risk-order-anomaly': 'Риск отмены и аномалии заказов',
  'future-customer-churn-lifetime-value': 'Отток и ценность клиентов',
  'future-demand-stockout-excess-forecast': 'Прогноз спроса и остатков',
  'future-slow-moving-dead-stock': 'Неликвидные и залежавшиеся товары',
  'future-purchase-recommendation': 'Рекомендации по закупкам',
  'future-supplier-quality-delay-forecast': 'Качество и сроки поставщиков',
  'future-cash-flow-expense-anomalies': 'Денежный поток и аномалии расходов',
  'future-ocr-extraction-comparison': 'Распознавание и сверка документов',
  'future-incoming-mail-routing-draft-reply': 'Распределение почты и черновики ответов',
  'future-task-extraction-from-messages': 'Задачи из сообщений',
  'future-natural-language-analytics': 'Аналитика по запросу на обычном языке',
  'future-fleet-breakdown-fuel-anomaly': 'Поломки транспорта и расход топлива',
  'future-manager-quality-analysis': 'Анализ работы менеджеров',
};
const CATEGORIES = {
  CRM: 'Клиенты', 'Sales / Finance': 'Продажи и финансы', 'Documents / Logistics': 'Документы и логистика',
  Management: 'Управление', Sales: 'Продажи', Inventory: 'Склад', Procurement: 'Закупки',
  Finance: 'Финансы', Documents: 'Документы', Communications: 'Коммуникации', Tasks: 'Задачи',
  BI: 'Аналитика', Fleet: 'Транспорт',
};
const STATUS = { IMPLEMENTED: 'ВНЕДРЕНО', DEMO: 'ДЕМО', BLOCKED: 'ЗАБЛОКИРОВАНО', FUTURE: 'В ПЛАНАХ' };
const RESULT_KEYS = {
  customers: 'Клиенты', review_reactivation: 'Клиентов для проверки', partner_id: 'Идентификатор клиента',
  name: 'Название', orders: 'Заказы', unpaid_orders: 'Неоплаченных заказов',
  days_since_last_order: 'Дней с последнего заказа', attention: 'Внимание', reason: 'Причина',
  id: 'Идентификатор заказа', currency: 'Валюта', result: 'Разница выручки и затрат',
  margin_percent: 'Доля результата, %', review_count: 'Количество замечаний', note: 'Примечание',
  missing: 'Не хватает документов', needs_review: 'Требуют проверки', status: 'Статус',
  kpis: 'Показатели', customers_to_review: 'Клиентов для проверки',
  orders_with_margin_alert: 'Заказов с финансовыми замечаниями',
  orders_with_document_gaps: 'Заказов с пробелами в документах', actions: 'Действия для проверки',
};
const RESULT_VALUES = {
  review_reactivation: 'Проверить повторное обращение', no_history: 'Нет истории заказов',
  current: 'Без замечаний', review: 'Требует проверки', ok: 'Без замечаний',
  ready_for_human_review: 'Готово к ручной проверке',
};
const state = { automations: [], history: [], category: 'Все', search: '', current: null };
const $ = (id) => document.getElementById(id);
const nameOf = (item) => NAMES[item.slug] || item.details?.what || item.name;
const categoryOf = (category) => CATEGORIES[category] || category;
const modeOf = (modes) => modes.includes('DEMO') ? 'ДЕМО-РЕЖИМ' : 'НЕТ ДОСТУПНОГО РЕЖИМА';
const statusOf = (status) => STATUS[status] || 'НЕИЗВЕСТНО';
const historyName = (run) => nameOf(state.automations.find((item) => item.slug === run.slug) || { slug: run.slug, name: run.automation });

function localText(text) {
  return text.replaceAll('DEMO MODE', 'демо-режим').replaceAll('LIVE MODE', 'рабочий режим')
    .replaceAll('ML/LLM', 'машинное обучение / языковая модель').replaceAll('LLM', 'языковая модель')
    .replaceAll('OCR', 'распознавание текста').replaceAll('read-only', 'только чтение')
    .replaceAll('lead time', 'сроков поставки').replaceAll('AI', 'ИИ');
}

function localResult(value) {
  if (Array.isArray(value)) return value.map(localResult);
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, data]) => [RESULT_KEYS[key] || key, localResult(data)]));
  }
  if (value === null) return 'Нет данных';
  return typeof value === 'string' ? RESULT_VALUES[value] || value : value;
}

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

async function api(path, options) {
  let response;
  try { response = await fetch(path, options); }
  catch { throw new Error('Нет связи с локальным сервером. Обновите страницу и попробуйте ещё раз.'); }
  if (!response.ok) {
    const errors = {
      400: 'Сценарий отклонил входные данные. Сверьте формат JSON с примером.',
      403: 'Запрос не разрешён. Откройте приложение на локальном адресе.',
      413: 'Входные данные превышают 64 КБ.',
      429: 'Сейчас выполняются другие сценарии. Повторите попытку позже.',
    };
    throw new Error(errors[response.status] || 'Не удалось выполнить запрос. Проверьте локальный сервер.');
  }
  return response.json();
}

function button(text, className, action, disabled = false) {
  const element = node('button', className, text);
  element.type = 'button';
  element.disabled = disabled;
  if (action) element.addEventListener('click', action);
  return element;
}

function renderStats() {
  const stats = [
    ['Всего сценариев', state.automations.length],
    ['Внедрено', state.automations.filter((a) => a.status === 'IMPLEMENTED').length],
    ['Демонстраций', state.automations.filter((a) => a.status === 'DEMO').length],
    ['Пока недоступно', state.automations.filter((a) => a.status === 'BLOCKED' || a.status === 'FUTURE').length],
    ['Категорий', new Set(state.automations.map((a) => a.category)).size],
  ];
  $('stats').replaceChildren(...stats.map(([label, count]) => {
    const card = node('div', 'stat');
    card.append(node('div', 'number', String(count)), node('div', 'label', label));
    return card;
  }));
}

function renderFilters() {
  const categories = ['Все', ...new Set(state.automations.map((a) => a.category))];
  $('filters').replaceChildren(...categories.map((category) => button(category === 'Все' ? category : categoryOf(category), `filter${state.category === category ? ' active' : ''}`, () => {
    state.category = category;
    renderFilters();
    renderCards();
  })));
}

function matches(item) {
  const query = state.search.trim().toLocaleLowerCase('ru');
  const searchable = [nameOf(item), item.name, localText(item.description), categoryOf(item.category), item.category, ...item.tags].join(' ').toLocaleLowerCase('ru');
  return (state.category === 'Все' || item.category === state.category) && searchable.includes(query);
}

function renderCards() {
  const filtered = state.automations.filter(matches);
  $('result-count').textContent = `НАЙДЕНО: ${filtered.length}`;
  if (!filtered.length) {
    $('cards').replaceChildren(node('div', 'empty', 'По вашему запросу ничего не найдено. Измените запрос или категорию.'));
    return;
  }
  $('cards').replaceChildren(...filtered.map((item) => {
    const card = node('article', 'card');
    const top = node('div', 'card-top');
    top.append(node('span', 'card-icon', nameOf(item).slice(0, 1).toUpperCase()), node('span', `badge ${item.runnable ? 'demo' : 'blocked'}`, statusOf(item.status)));
    const actions = node('div', 'card-actions');
    actions.append(button('Подробнее →', 'link-button', () => details(item)), button(item.runnable ? 'Запустить ↗' : 'Недоступно', 'run-button', () => runDialog(item), !item.runnable));
    card.append(top, node('h3', '', nameOf(item)), node('span', 'category', categoryOf(item.category) + '  ·  ' + modeOf(item.modes)), node('p', 'desc', localText(item.description)), actions);
    return card;
  }));
}

function renderActivity() {
  const latest = state.history[0];
  const container = $('activity');
  const text = node('div');
  text.append(node('strong', '', 'Последние действия'), document.createTextNode(latest ? `${historyName(latest)} · ${latest.status === 'Completed' ? 'Завершено' : 'Ошибка'} · ДЕМО` : 'Запусков пока нет. Выберите демонстрационный сценарий.'));
  container.replaceChildren(text, button('ИСТОРИЯ ЗАПУСКОВ →', '', () => showView('history')));
}

function renderHistory() {
  const target = $('history-content');
  if (!state.history.length) {
    target.replaceChildren(node('div', 'empty', 'Запусков пока нет. Выберите демонстрационный сценарий.'));
    return;
  }
  const wrap = node('div', 'history-table');
  const table = node('table');
  const head = node('thead');
  const row = node('tr');
  ['Сценарий', 'Статус', 'Начало', 'Длительность', 'Режим'].forEach((label) => row.append(node('th', '', label)));
  head.append(row);
  const body = node('tbody');
  state.history.forEach((run) => {
    const entry = node('tr');
    entry.append(node('td', '', historyName(run)), node('td', run.status.toLowerCase(), run.status === 'Completed' ? 'Завершено' : 'Ошибка'), node('td', '', new Date(run.started).toLocaleString('ru-RU')), node('td', '', `${run.duration_ms} мс`), node('td', '', 'ДЕМО'));
    body.append(entry);
  });
  table.append(head, body);
  wrap.append(table);
  target.replaceChildren(wrap);
}

async function refreshHistory() {
  try {
    state.history = (await api('/api/history')).runs;
    renderActivity();
    renderHistory();
  } catch {
    $('activity').textContent = 'История запусков недоступна.';
  }
}

function showView(view) {
  $('automations-view').hidden = view !== 'automations';
  $('history-view').hidden = view !== 'history';
  $('nav-automations').classList.toggle('active', view === 'automations');
  $('nav-history').classList.toggle('active', view === 'history');
  $('crumb').textContent = view === 'history' ? 'ИСТОРИЯ ЗАПУСКОВ' : 'АВТОМАТИЗАЦИИ';
  if (view === 'history') refreshHistory();
  window.scrollTo(0, 0);
}

function closeModal() { $('modal-root').replaceChildren(); state.current = null; }
function modal(item, label) {
  const backdrop = node('div', 'modal-backdrop');
  const panel = node('section', 'modal');
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-modal', 'true');
  panel.setAttribute('aria-label', `${label}: ${nameOf(item)}`);
  const header = node('div', 'modal-header');
  const title = node('div');
  title.append(node('span', 'eyebrow', `${statusOf(item.status)} · ${categoryOf(item.category)}`), node('h2', '', nameOf(item)));
  header.append(title, button('×', 'close', closeModal));
  const body = node('div', 'modal-body');
  panel.append(header, body);
  backdrop.append(panel);
  backdrop.addEventListener('click', (event) => { if (event.target === backdrop) closeModal(); });
  $('modal-root').replaceChildren(backdrop);
  state.current = item;
  header.querySelector('button').focus();
  return body;
}

function details(item) {
  const body = modal(item, 'Подробности');
  const labels = [
    ['what', 'Что делает'], ['simplifies', 'Что упрощает'], ['how', 'Как работает'],
    ['data', 'Используемые данные'], ['processing', 'Обработка данных'], ['output', 'Результат'],
    ['pros', 'Преимущества'], ['cons', 'Ограничения'], ['risks', 'Риски'],
    ['architecture', 'Интеграция и зависимости'], ['limitations', 'Что пока недоступно'],
  ];
  labels.forEach(([key, title]) => {
    if (!item.details[key]) return;
    const row = node('div', 'detail-row');
    row.append(node('h3', '', title), node('p', '', localText(item.details[key])));
    body.append(row);
  });
  const status = node('div', 'detail-row');
  status.append(node('h3', '', 'Статус и режим'), node('p', '', `${statusOf(item.status)} · ${modeOf(item.modes)}`));
  body.append(status);
  const actions = node('div', 'modal-actions');
  actions.append(button('Закрыть', 'secondary', closeModal), button(item.runnable ? 'Запустить сценарий' : 'Недоступно', 'primary', () => runDialog(item), !item.runnable));
  body.append(actions);
}

function runDialog(item, previousInput = null) {
  if (!item.runnable) return;
  const body = modal(item, 'Запуск сценария');
  body.append(node('div', 'notice', 'ДЕМО-РЕЖИМ · Синтетические данные, понятные правила, без подключения к Odoo. Рабочий режим недоступен.'));
  const label = node('label', 'input-label');
  const checkbox = node('input');
  checkbox.type = 'checkbox';
  checkbox.checked = previousInput !== null;
  label.append(checkbox, document.createTextNode('Использовать свой синтетический JSON'));
  const input = node('textarea');
  input.setAttribute('aria-label', 'Синтетические входные данные JSON');
  input.spellcheck = false;
  input.value = previousInput === null ? JSON.stringify(item.example_input, null, 2) : previousInput;
  input.hidden = !checkbox.checked;
  checkbox.addEventListener('change', () => { input.hidden = !checkbox.checked; });
  body.append(label, input, node('p', 'input-hint', 'По умолчанию используется пример из example_input.json. Свой JSON должен сохранять технические названия полей и не превышать 64 КБ. Не вставляйте реальные данные.'));
  const actions = node('div', 'modal-actions');
  actions.append(button('Отмена', 'secondary', closeModal), button('Запустить сценарий', 'primary', () => startRun(item, checkbox.checked ? input.value : null)));
  body.append(actions);
}

async function startRun(item, text) {
  let input;
  if (text !== null) {
    try { input = JSON.parse(text); if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error(); }
    catch { showError(item, 'Входные данные должны быть корректным объектом JSON.', text); return; }
  }
  const body = modal(item, 'Выполнение');
  body.append(node('div', 'notice', 'ДЕМО-РЕЖИМ · Данные Odoo не используются.'), node('p', 'input-hint', 'Запускаем сценарий с синтетическими данными...'));
  const loading = node('p');
  loading.append(node('span', 'spinner'), document.createTextNode('Сценарий выполняется...'));
  body.append(loading);
  try {
    const result = await api('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ slug: item.slug, mode: 'DEMO', ...(text !== null ? { input } : {}) }) });
    if (state.current === item) showResult(item, result.output, text);
  } catch (error) {
    if (state.current === item) showError(item, error.message, text);
  } finally { await refreshHistory(); }
}

function showResult(item, output, text) {
  const body = modal(item, 'Результат');
  body.append(node('div', 'notice', 'Сценарий завершён · ДЕМО-РЕЖИМ · Результат получен от запущенного сценария.'), node('h3', '', 'Результат'), node('pre', '', JSON.stringify(localResult(output.result), null, 2)));
  const actions = node('div', 'modal-actions');
  actions.append(button('К каталогу', 'secondary', closeModal), button('Запустить снова', 'primary', () => runDialog(item, text)));
  body.append(actions);
}

function showError(item, message, text) {
  const body = modal(item, 'Ошибка');
  body.append(node('div', 'notice error', `Не удалось выполнить сценарий · ${message}`));
  const actions = node('div', 'modal-actions');
  actions.append(button('К каталогу', 'secondary', closeModal), button('Повторить', 'primary', () => runDialog(item, text)));
  body.append(actions);
}

$('search').addEventListener('input', (event) => { state.search = event.target.value; renderCards(); });
$('nav-automations').addEventListener('click', () => showView('automations'));
$('nav-history').addEventListener('click', () => showView('history'));
document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && state.current) closeModal(); });
api('/api/automations').then(({ automations }) => {
  state.automations = automations;
  renderStats(); renderFilters(); renderCards(); refreshHistory();
}).catch(() => { $('cards').replaceChildren(node('div', 'empty', 'Каталог недоступен. Проверьте локальный сервер и обновите страницу.')); });
