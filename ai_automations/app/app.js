const state = { automations: [], history: [], category: 'All', search: '', current: null };
const $ = (id) => document.getElementById(id);

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

async function api(path, options) {
  const response = await fetch(path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'Request failed.');
  return body;
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
    ['Total automations', state.automations.length],
    ['Implemented', state.automations.filter((a) => a.status === 'IMPLEMENTED').length],
    ['Demo', state.automations.filter((a) => a.status === 'DEMO').length],
    ['Future', state.automations.filter((a) => a.status === 'BLOCKED' || a.status === 'FUTURE').length],
    ['Categories', new Set(state.automations.map((a) => a.category)).size],
  ];
  $('stats').replaceChildren(...stats.map(([label, count]) => {
    const card = node('div', 'stat');
    card.append(node('div', 'number', String(count)), node('div', 'label', label));
    return card;
  }));
}

function renderFilters() {
  const categories = ['All', ...new Set(state.automations.map((a) => a.category))];
  $('filters').replaceChildren(...categories.map((category) => button(category, `filter${state.category === category ? ' active' : ''}`, () => {
    state.category = category;
    renderFilters();
    renderCards();
  })));
}

function matches(item) {
  const query = state.search.trim().toLocaleLowerCase();
  const searchable = [item.name, item.description, item.category, ...item.tags].join(' ').toLocaleLowerCase();
  return (state.category === 'All' || item.category === state.category) && searchable.includes(query);
}

function renderCards() {
  const filtered = state.automations.filter(matches);
  $('result-count').textContent = `${filtered.length} AUTOMATIONS`;
  if (!filtered.length) {
    $('cards').replaceChildren(node('div', 'empty', 'No automations match your search. Try another keyword or category.'));
    return;
  }
  $('cards').replaceChildren(...filtered.map((item) => {
    const card = node('article', 'card');
    const top = node('div', 'card-top');
    top.append(node('span', 'card-icon', item.name.slice(0, 1).toUpperCase()), node('span', `badge ${item.runnable ? 'demo' : 'blocked'}`, item.status));
    const actions = node('div', 'card-actions');
    actions.append(button('Details →', 'link-button', () => details(item)), button(item.runnable ? 'Run ↗' : 'Unavailable', 'run-button', () => runDialog(item), !item.runnable));
    card.append(top, node('h3', '', item.name), node('span', 'category', item.category + '  ·  ' + (item.modes.join(', ') || 'NOT AVAILABLE')), node('p', 'desc', item.description), actions);
    return card;
  }));
}

function renderActivity() {
  const latest = state.history[0];
  const container = $('activity');
  const text = node('div');
  text.append(node('strong', '', 'Recent activity'), document.createTextNode(latest ? `${latest.automation} · ${latest.status} · ${latest.mode}` : 'No runs yet. Run a demo to see activity here.'));
  container.replaceChildren(text, button('VIEW HISTORY →', '', () => showView('history')));
}

function renderHistory() {
  const target = $('history-content');
  if (!state.history.length) {
    target.replaceChildren(node('div', 'empty', 'No runs yet. Start a demo automation to see it here.'));
    return;
  }
  const wrap = node('div', 'history-table');
  const table = node('table');
  const head = node('thead');
  const row = node('tr');
  ['Automation', 'Status', 'Started', 'Duration', 'Mode'].forEach((label) => row.append(node('th', '', label)));
  head.append(row);
  const body = node('tbody');
  state.history.forEach((run) => {
    const entry = node('tr');
    entry.append(node('td', '', run.automation), node('td', run.status.toLowerCase(), run.status), node('td', '', new Date(run.started).toLocaleString()), node('td', '', `${run.duration_ms} ms`), node('td', '', run.mode));
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
    $('activity').textContent = 'Recent activity is unavailable.';
  }
}

function showView(view) {
  $('automations-view').hidden = view !== 'automations';
  $('history-view').hidden = view !== 'history';
  $('nav-automations').classList.toggle('active', view === 'automations');
  $('nav-history').classList.toggle('active', view === 'history');
  $('crumb').textContent = view === 'history' ? 'RUN HISTORY' : 'AUTOMATIONS';
  if (view === 'history') refreshHistory();
  window.scrollTo(0, 0);
}

function closeModal() { $('modal-root').replaceChildren(); state.current = null; }
function modal(item, label) {
  const backdrop = node('div', 'modal-backdrop');
  const panel = node('section', 'modal');
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-modal', 'true');
  panel.setAttribute('aria-label', `${label}: ${item.name}`);
  const header = node('div', 'modal-header');
  const title = node('div');
  title.append(node('span', 'eyebrow', `${item.status} · ${item.category}`), node('h2', '', item.name));
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
  const body = modal(item, 'Details');
  const labels = [
    ['what', 'What it does'], ['simplifies', 'What it simplifies'], ['how', 'How it works'],
    ['data', 'Data used'], ['processing', 'AI processing'], ['output', 'Output'],
    ['pros', 'Pros'], ['cons', 'Cons'], ['risks', 'Risks'],
    ['architecture', 'Integration & dependencies'], ['limitations', 'Limitations'],
  ];
  labels.forEach(([key, title]) => {
    if (!item.details[key]) return;
    const row = node('div', 'detail-row');
    row.append(node('h3', '', title), node('p', '', item.details[key]));
    body.append(row);
  });
  const status = node('div', 'detail-row');
  status.append(node('h3', '', 'Status & mode'), node('p', '', `${item.status} · ${item.modes.join(', ') || 'No executable mode'}`));
  body.append(status);
  const actions = node('div', 'modal-actions');
  actions.append(button('Close', 'secondary', closeModal), button(item.runnable ? 'Run automation' : 'Not available', 'primary', () => runDialog(item), !item.runnable));
  body.append(actions);
}

function runDialog(item, previousInput = null) {
  if (!item.runnable) return;
  const body = modal(item, 'Run automation');
  const notice = node('div', 'notice', 'DEMO MODE · Uses synthetic example data, deterministic rules and no Odoo connection. LIVE MODE is unavailable.');
  body.append(notice);
  const label = node('label', 'input-label');
  const checkbox = node('input');
  checkbox.type = 'checkbox';
  checkbox.checked = previousInput !== null;
  label.append(checkbox, document.createTextNode('Use custom synthetic JSON input'));
  const input = node('textarea');
  input.setAttribute('aria-label', 'Custom synthetic JSON input');
  input.spellcheck = false;
  input.value = previousInput === null ? JSON.stringify(item.example_input, null, 2) : previousInput;
  input.hidden = !checkbox.checked;
  checkbox.addEventListener('change', () => { input.hidden = !checkbox.checked; });
  body.append(label, input, node('p', 'input-hint', 'Default: checked-in example_input.json. Custom input must match its structure (64 KB max). Do not paste production data.'));
  const actions = node('div', 'modal-actions');
  actions.append(button('Cancel', 'secondary', closeModal), button('Run automation', 'primary', () => startRun(item, checkbox.checked ? input.value : null)));
  body.append(actions);
}

async function startRun(item, text) {
  let input;
  if (text !== null) {
    try { input = JSON.parse(text); if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error(); }
    catch { showError(item, 'Input must be a valid JSON object.', text); return; }
  }
  const body = modal(item, 'Running');
  body.append(node('div', 'notice', 'DEMO MODE · No Odoo data is accessed.'), node('p', 'input-hint', 'Running the registered scenario with synthetic input...'));
  const loading = node('p');
  loading.append(node('span', 'spinner'), document.createTextNode('Running automation...'));
  body.append(loading);
  try {
    const result = await api('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ slug: item.slug, mode: 'DEMO', ...(text !== null ? { input } : {}) }) });
    if (state.current === item) showResult(item, result.output, text);
  } catch (error) {
    if (state.current === item) showError(item, error.message, text);
  } finally { await refreshHistory(); }
}

function showResult(item, output, text) {
  const body = modal(item, 'Result');
  body.append(node('div', 'notice', 'Automation completed · DEMO MODE · Actual result from the registered scenario.'), node('h3', '', 'Result'), node('pre', '', JSON.stringify(output, null, 2)));
  const actions = node('div', 'modal-actions');
  actions.append(button('Back to automations', 'secondary', closeModal), button('Run again', 'primary', () => runDialog(item, text)));
  body.append(actions);
}

function showError(item, message, text) {
  const body = modal(item, 'Error');
  body.append(node('div', 'notice error', `Automation failed · ${message}`));
  const actions = node('div', 'modal-actions');
  actions.append(button('Back to automations', 'secondary', closeModal), button('Retry', 'primary', () => runDialog(item, text)));
  body.append(actions);
}

$('search').addEventListener('input', (event) => { state.search = event.target.value; renderCards(); });
$('nav-automations').addEventListener('click', () => showView('automations'));
$('nav-history').addEventListener('click', () => showView('history'));
document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && state.current) closeModal(); });
api('/api/automations').then(({ automations }) => {
  state.automations = automations;
  renderStats(); renderFilters(); renderCards(); refreshHistory();
}).catch(() => { $('cards').replaceChildren(node('div', 'empty', 'Catalogue is unavailable. Check the server and reload the page.')); });
