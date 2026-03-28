import { FormEvent, useMemo, useState } from "react";
import { apiGet, apiPost, getApiBaseUrl, setApiBaseUrl } from "./lib/api";
import { HealthResponse, NavSection, WorkflowListResponse } from "./types";

const SECTIONS: Array<{ key: NavSection; label: string }> = [
  { key: "dashboard", label: "Dashboard" },
  { key: "products", label: "Products" },
  { key: "reviews", label: "Reviews" },
  { key: "content-ai", label: "Content AI" },
  { key: "inventory", label: "Inventory" },
  { key: "settings", label: "Settings" }
];

function JsonBlock({ data }: { data: unknown }) {
  if (data === null || data === undefined) return <p className="muted">No data</p>;
  return <pre className="json-block">{JSON.stringify(data, null, 2)}</pre>;
}

export default function App() {
  const [activeSection, setActiveSection] = useState<NavSection>("dashboard");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [payload, setPayload] = useState<unknown>(null);

  const [apiBaseUrlInput, setApiBaseUrlInput] = useState(getApiBaseUrl());
  const [inventoryShopId, setInventoryShopId] = useState("1");
  const [inventoryThreshold, setInventoryThreshold] = useState("10");

  const [contentTitle, setContentTitle] = useState("Термокружка 450 мл");
  const [contentCategory, setContentCategory] = useState("Посуда");
  const [contentFeatures, setContentFeatures] = useState("Держит тепло, Не протекает, Сталь 304");
  const [contentKeywords, setContentKeywords] = useState("термокружка, кружка для кофе");

  const appMeta = useMemo(() => window.desktop, []);

  async function runRequest<T>(fn: () => Promise<T>) {
    setLoading(true);
    setError(null);
    try {
      const result = await fn();
      setPayload(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  function renderDashboard() {
    return (
      <div className="panel-grid">
        <button onClick={() => runRequest<HealthResponse>(() => apiGet("/health"))}>Check Health</button>
        <button onClick={() => runRequest<WorkflowListResponse>(() => apiGet("/workflows/"))}>
          List Workflows
        </button>
        <button onClick={() => runRequest(() => apiGet("/ai/providers"))}>AI Providers</button>
      </div>
    );
  }

  function renderProducts() {
    return (
      <div className="panel-grid">
        <button onClick={() => runRequest(() => apiGet("/products/?limit=20"))}>Load Products</button>
        <button
          onClick={() =>
            runRequest(() =>
              apiPost("/actions/create-product-card", {
                card_payload: { title: "Тестовая карточка", description: "Создано через desktop app" }
              })
            )
          }
        >
          Action: Create Product Card
        </button>
      </div>
    );
  }

  function renderReviews() {
    return (
      <div className="panel-grid">
        <button onClick={() => runRequest(() => apiGet("/feedbacks/?take=20&skip=0"))}>Load Reviews</button>
        <button
          onClick={() =>
            runRequest(() =>
              apiPost("/actions/reply-to-review", {
                review_id: "feedback-000001",
                reply_text: "Спасибо за ваш отзыв!"
              })
            )
          }
        >
          Action: Reply To Review
        </button>
        <button
          onClick={() =>
            runRequest(() =>
              apiPost(
                "/workflows/execute",
                {
                  workflow_name: "review_workflow",
                  context: {
                    review: {
                      id: "feedback-000001",
                      text: "Товар пришел с дефектом",
                      rating: 2,
                      product_name: "Тестовый товар"
                    },
                    execute_action: true
                  }
                }
              )
            )
          }
        >
          Run Review Workflow + Action
        </button>
      </div>
    );
  }

  async function onGenerateContent(event: FormEvent) {
    event.preventDefault();
    const features = contentFeatures
      .split(",")
      .map((f) => f.trim())
      .filter(Boolean);
    const keywords = contentKeywords
      .split(",")
      .map((f) => f.trim())
      .filter(Boolean);

    await runRequest(() =>
      apiPost("/workflows/content/create-card", {
        execute_action: false,
        product_data: {
          title: contentTitle,
          category: contentCategory,
          features,
          keywords
        }
      })
    );
  }

  function renderContentAI() {
    return (
      <form className="form" onSubmit={onGenerateContent}>
        <label>
          Title
          <input value={contentTitle} onChange={(e) => setContentTitle(e.target.value)} />
        </label>
        <label>
          Category
          <input value={contentCategory} onChange={(e) => setContentCategory(e.target.value)} />
        </label>
        <label>
          Features (comma separated)
          <input value={contentFeatures} onChange={(e) => setContentFeatures(e.target.value)} />
        </label>
        <label>
          Keywords (comma separated)
          <input value={contentKeywords} onChange={(e) => setContentKeywords(e.target.value)} />
        </label>
        <button type="submit">Generate Content Workflow</button>
      </form>
    );
  }

  function renderInventory() {
    return (
      <div className="form">
        <label>
          Shop ID
          <input value={inventoryShopId} onChange={(e) => setInventoryShopId(e.target.value)} />
        </label>
        <label>
          Threshold
          <input value={inventoryThreshold} onChange={(e) => setInventoryThreshold(e.target.value)} />
        </label>
        <button
          onClick={() =>
            runRequest(() =>
              apiPost("/workflows/execute", {
                workflow_name: "inventory_workflow",
                context: {
                  shop_id: Number(inventoryShopId),
                  threshold: Number(inventoryThreshold)
                }
              })
            )
          }
        >
          Run Inventory Workflow
        </button>
      </div>
    );
  }

  function renderSettings() {
    return (
      <div className="form">
        <label>
          Backend API Base URL
          <input value={apiBaseUrlInput} onChange={(e) => setApiBaseUrlInput(e.target.value)} />
        </label>
        <button
          onClick={() => {
            setApiBaseUrl(apiBaseUrlInput);
            setPayload({ status: "saved", apiBaseUrl: apiBaseUrlInput });
          }}
        >
          Save API URL
        </button>
        <div className="meta">
          <p>Electron: {appMeta?.version || "N/A"}</p>
          <p>Platform: {appMeta?.platform || "N/A"}</p>
        </div>
      </div>
    );
  }

  function renderSection() {
    switch (activeSection) {
      case "dashboard":
        return renderDashboard();
      case "products":
        return renderProducts();
      case "reviews":
        return renderReviews();
      case "content-ai":
        return renderContentAI();
      case "inventory":
        return renderInventory();
      case "settings":
        return renderSettings();
      default:
        return null;
    }
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>AI Marketplace Assistant</h1>
        <nav>
          {SECTIONS.map((section) => (
            <button
              key={section.key}
              className={activeSection === section.key ? "nav-btn active" : "nav-btn"}
              onClick={() => setActiveSection(section.key)}
            >
              {section.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="main">
        <header className="main-header">
          <h2>{SECTIONS.find((item) => item.key === activeSection)?.label}</h2>
          {loading && <span className="muted">Loading...</span>}
        </header>

        {renderSection()}

        {error && <p className="error">{error}</p>}
        <JsonBlock data={payload} />
      </main>
    </div>
  );
}
