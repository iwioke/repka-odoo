import { FormEvent, useMemo, useState } from "react";

type Section = "assistant" | "knowledge" | "drafts" | "odoo" | "history" | "profile" | "admin";
type Message = {
  id: number;
  author: "assistant" | "user";
  text: string;
  sources?: string[];
};

const navigation: { id: Section; label: string; code: string; restricted?: boolean }[] = [
  { id: "assistant", label: "Ассистент", code: "AI" },
  { id: "knowledge", label: "Знания", code: "KB" },
  { id: "drafts", label: "Черновики", code: "DR" },
  { id: "odoo", label: "Odoo агент", code: "OD" },
  { id: "history", label: "История", code: "HS" },
  { id: "profile", label: "Профиль", code: "PR" },
  { id: "admin", label: "Администрирование", code: "AD", restricted: true },
];

const quickPrompts = [
  "Найди условия в договоре перевозки",
  "Подготовь черновик письма клиенту",
  "Покажи статус локального AI",
];

const sectionDescriptions: Record<Exclude<Section, "assistant">, string> = {
  knowledge: "Здесь появятся утверждённые источники с проверяемыми правами доступа и цитатами.",
  drafts: "Здесь будут только черновики по утверждённым шаблонам с обязательной проверкой человеком.",
  odoo: "Odoo Development Agent будет работать read-only до утверждения плана и отдельной feature branch.",
  history: "История запросов и действий будет доступна только после реализации аутентификации и audit log.",
  profile: "Профиль, активные сессии и настройки доступа появятся после выбора identity provider.",
  admin: "Раздел зарезервирован для knowledge, security и system administrators.",
};

function mockReply(text: string): Message {
  const normalized = text.toLocaleLowerCase("ru");
  if (normalized.includes("статус") || normalized.includes("ai")) {
    return {
      id: Date.now(),
      author: "assistant",
      text: "Локальный AI worker пока не подключён. Интерфейс работает в test-only режиме и не отправляет данные во внешние модели.",
      sources: ["Статус системы • test-only"],
    };
  }
  if (normalized.includes("письм") || normalized.includes("чернов")) {
    return {
      id: Date.now(),
      author: "assistant",
      text: "В будущем здесь будет черновик по утверждённому шаблону. Сейчас интерфейс показывает только безопасный макет без отправки писем и без корпоративных данных.",
      sources: ["Черновики • макет"],
    };
  }
  return {
    id: Date.now(),
    author: "assistant",
    text: "Это демонстрационный ответ нового LM GROUP PWA. Подключение знаний, Odoo и локальной модели намеренно отключено до утверждения ACL, identity и infrastructure boundaries.",
    sources: ["Интерфейс • test-only"],
  };
}

function App() {
  const [section, setSection] = useState<Section>("assistant");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      author: "assistant",
      text: "Добро пожаловать в LM GROUP Assistant. Это первый test-only интерфейс: здесь нет доступа к документам, Odoo или модели, поэтому ни один запрос не выходит за пределы браузерного макета.",
      sources: ["Архитектура • test-only shell"],
    },
  ]);

  const activeLabel = useMemo(
    () => navigation.find((item) => item.id === section)?.label ?? "LM GROUP",
    [section],
  );

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = input.trim();
    if (!value) return;
    setMessages((current) => [
      ...current,
      { id: Date.now() - 1, author: "user", text: value },
      mockReply(value),
    ]);
    setInput("");
  }

  function choosePrompt(prompt: string) {
    setInput(prompt);
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand" aria-label="LM GROUP">
          <span className="brand-mark">LM</span>
          <span>
            <strong>LM GROUP</strong>
            <small>Corporate AI</small>
          </span>
        </div>

        <nav aria-label="Основная навигация">
          <p className="nav-caption">Рабочее пространство</p>
          {navigation.map((item) => (
            <button
              className={`nav-item ${section === item.id ? "is-active" : ""}`}
              key={item.id}
              onClick={() => setSection(item.id)}
              type="button"
            >
              <span className="nav-code" aria-hidden="true">{item.code}</span>
              <span>{item.label}</span>
              {item.restricted && <span className="restricted">только роль</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="availability-dot" aria-hidden="true" />
          <span>Test-only контур</span>
          <small>Без внешних интеграций</small>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">LM GROUP / {activeLabel}</p>
            <h1>{section === "assistant" ? "Корпоративный AI-помощник" : activeLabel}</h1>
          </div>
          <div className="topbar-actions">
            <span className="pilot-chip">Пилотный макет</span>
            <button className="profile-button" type="button" aria-label="Профиль пользователя">MM</button>
          </div>
        </header>

        <div className="status-banner" role="status">
          <span className="status-indicator" aria-hidden="true" />
          <div>
            <strong>Локальный AI недоступен</strong>
            <p>Макет работает без модели и не обрабатывает документы или запросы Odoo.</p>
          </div>
          <button type="button" className="status-link" onClick={() => setSection("knowledge")}>Ограничения</button>
        </div>

        {section === "assistant" ? (
          <section className="assistant-layout" aria-label="Чат с AI-помощником">
            <div className="chat-panel">
              <div className="chat-heading">
                <div>
                  <p className="eyebrow">Новый диалог</p>
                  <h2>Чем могу помочь?</h2>
                </div>
                <span className="scope-label">Mock mode</span>
              </div>

              <div className="quick-prompts" aria-label="Примеры запросов">
                {quickPrompts.map((prompt) => (
                  <button key={prompt} type="button" onClick={() => choosePrompt(prompt)}>{prompt}</button>
                ))}
              </div>

              <div className="conversation" aria-live="polite">
                {messages.map((message) => (
                  <article className={`message ${message.author}`} key={message.id}>
                    <span className="message-avatar" aria-hidden="true">{message.author === "assistant" ? "LM" : "MM"}</span>
                    <div>
                      <div className="message-meta">{message.author === "assistant" ? "LM GROUP Assistant" : "Вы"}</div>
                      <p>{message.text}</p>
                      {message.sources && (
                        <div className="sources">
                          {message.sources.map((source) => <span key={source}>{source}</span>)}
                        </div>
                      )}
                    </div>
                  </article>
                ))}
              </div>

              <form className="composer" onSubmit={submit}>
                <label htmlFor="assistant-input">Сообщение</label>
                <div className="composer-row">
                  <textarea
                    id="assistant-input"
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                    placeholder="Опишите задачу или выберите пример выше"
                    rows={2}
                  />
                  <button type="submit">Отправить</button>
                </div>
                <p>Демо не сохраняет сообщения и не передаёт их модели, Odoo или внешнему сервису.</p>
              </form>
            </div>

            <aside className="context-panel" aria-label="Контекст системы">
              <section>
                <p className="eyebrow">Контуры доступа</p>
                <h2>Безопасный старт</h2>
                <dl>
                  <div><dt>Документы</dt><dd>Не подключены</dd></div>
                  <div><dt>Odoo</dt><dd>Не подключён</dd></div>
                  <div><dt>Провайдер</dt><dd>Local-only policy</dd></div>
                </dl>
              </section>
              <section className="roadmap-card">
                <p className="eyebrow">Следующий этап</p>
                <h3>Identity и RBAC</h3>
                <p>После утверждения учётных записей появятся персональные сессии, роли и audit trail.</p>
              </section>
            </aside>
          </section>
        ) : (
          <section className="section-placeholder">
            <p className="eyebrow">Раздел проектируется</p>
            <h2>{activeLabel}</h2>
            <p>{sectionDescriptions[section as Exclude<Section, "assistant">]}</p>
            <div className="placeholder-grid">
              <article><span>01</span><h3>Нет production data</h3><p>Раздел не делает вызовов в Odoo, файловый сервер или внешние API.</p></article>
              <article><span>02</span><h3>Права до контекста</h3><p>Будущая реализация будет проверять доступ на backend до retrieval и model context.</p></article>
              <article><span>03</span><h3>Human-in-the-loop</h3><p>Письма, документы, Odoo changes и необратимые операции останутся под контролем человека.</p></article>
            </div>
          </section>
        )}
      </section>
    </main>
  );
}

export default App;
