const API_URL_KEY = "ama.api.baseUrl";
const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

function normalizeBaseUrl(value: string): string {
  return value.replace(/\/+$/, "");
}

export function getApiBaseUrl(): string {
  const stored = localStorage.getItem(API_URL_KEY);
  return normalizeBaseUrl(stored || DEFAULT_API_BASE_URL);
}

export function setApiBaseUrl(url: string): void {
  localStorage.setItem(API_URL_KEY, normalizeBaseUrl(url));
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`GET ${path} failed: ${response.status} ${text}`);
  }
  return (await response.json()) as T;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`POST ${path} failed: ${response.status} ${text}`);
  }
  return (await response.json()) as T;
}
