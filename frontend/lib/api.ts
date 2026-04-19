import type { Analytics, Article, Source, TrendingCluster } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    // ISR-friendly: 60s
    next: init?.cache ? undefined : { revalidate: 60 },
    cache: init?.cache,
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

export async function fetchNews(params: {
  lang?: "hi" | "en" | "all";
  source?: string;
  category?: string;
  limit?: number;
  offset?: number;
}): Promise<Article[]> {
  const qs = new URLSearchParams();
  if (params.lang) qs.set("lang", params.lang);
  if (params.source) qs.set("source", params.source);
  if (params.category) qs.set("category", params.category);
  if (params.limit) qs.set("limit", String(params.limit));
  if (params.offset) qs.set("offset", String(params.offset));
  return request<Article[]>(`/news?${qs.toString()}`);
}

export async function fetchSources(lang?: "hi" | "en"): Promise<Source[]> {
  const qs = lang ? `?lang=${lang}` : "";
  return request<Source[]>(`/sources${qs}`);
}

export async function fetchTrending(
  lang: "hi" | "en",
  limit = 6
): Promise<TrendingCluster[]> {
  return request<TrendingCluster[]>(`/trending?lang=${lang}&limit=${limit}`);
}

export async function fetchCategories(): Promise<string[]> {
  return request<string[]>(`/categories`);
}

// --- Admin ---
export async function adminLogin(username: string, password: string): Promise<string> {
  const data = await request<{ access_token: string }>(`/admin/login`, {
    method: "POST",
    body: JSON.stringify({ username, password }),
    cache: "no-store",
  });
  return data.access_token;
}

function auth(token: string) {
  return { Authorization: `Bearer ${token}` };
}

export async function adminListSources(token: string): Promise<Source[]> {
  return request<Source[]>(`/admin/sources`, { headers: auth(token), cache: "no-store" });
}

export async function adminAddSource(
  token: string,
  payload: { name: string; url: string; language: "hi" | "en"; category?: string }
): Promise<Source> {
  return request<Source>(`/admin/source`, {
    method: "POST",
    headers: auth(token),
    body: JSON.stringify(payload),
    cache: "no-store",
  });
}

export async function adminToggleSource(
  token: string,
  id: number,
  is_active: boolean
): Promise<Source> {
  return request<Source>(`/admin/source/${id}`, {
    method: "PATCH",
    headers: auth(token),
    body: JSON.stringify({ is_active }),
    cache: "no-store",
  });
}

export async function adminDeleteSource(token: string, id: number): Promise<void> {
  const res = await fetch(`${API_URL}/admin/source/${id}`, {
    method: "DELETE",
    headers: auth(token),
  });
  if (!res.ok && res.status !== 204) throw new Error(`delete failed: ${res.status}`);
}

export async function adminRefresh(token: string): Promise<void> {
  await request<{ ok: boolean }>(`/admin/refresh`, {
    method: "POST",
    headers: auth(token),
    cache: "no-store",
  });
}

export async function adminAnalytics(token: string): Promise<Analytics> {
  return request<Analytics>(`/admin/analytics`, {
    headers: auth(token),
    cache: "no-store",
  });
}

// Click tracking (fire-and-forget)
export function trackClick(payload: {
  article_id?: number;
  source_name?: string;
  language?: string;
  referer?: string;
}): void {
  try {
    fetch(`${API_URL}/track`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      keepalive: true,
    }).catch(() => {});
  } catch {
    /* noop */
  }
}
