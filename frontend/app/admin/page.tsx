"use client";

import { useEffect, useState } from "react";
import {
  adminAddSource,
  adminAnalytics,
  adminDeleteSource,
  adminListSources,
  adminLogin,
  adminRefresh,
  adminToggleSource,
} from "@/lib/api";
import type { Analytics, Source } from "@/lib/types";

const TOKEN_KEY = "np_admin_token";

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = typeof window !== "undefined" ? window.localStorage.getItem(TOKEN_KEY) : null;
    if (t) setToken(t);
  }, []);

  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const t = await adminLogin(username, password);
      window.localStorage.setItem(TOKEN_KEY, t);
      setToken(t);
    } catch {
      setError("Invalid credentials");
    }
  };

  const logout = () => {
    window.localStorage.removeItem(TOKEN_KEY);
    setToken(null);
  };

  if (!token) {
    return (
      <div className="mx-auto max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow">
        <h1 className="mb-4 text-2xl font-bold">Admin Login</h1>
        <form onSubmit={login} className="space-y-3">
          <input
            className="w-full rounded border border-slate-300 px-3 py-2"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            className="w-full rounded border border-slate-300 px-3 py-2"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            className="w-full rounded bg-brand-accent py-2 font-semibold text-white hover:opacity-90"
          >
            Login
          </button>
        </form>
      </div>
    );
  }

  return <Dashboard token={token} onLogout={logout} />;
}

function Dashboard({ token, onLogout }: { token: string; onLogout: () => void }) {
  const [sources, setSources] = useState<Source[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Add source form
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [language, setLanguage] = useState<"hi" | "en">("en");
  const [category, setCategory] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [s, a] = await Promise.all([
        adminListSources(token),
        adminAnalytics(token),
      ]);
      setSources(s);
      setAnalytics(a);
    } catch {
      onLogout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const addSource = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    try {
      await adminAddSource(token, {
        name,
        url,
        language,
        category: category || undefined,
      });
      setName("");
      setUrl("");
      setCategory("");
      await load();
    } catch (err) {
      setFormError((err as Error).message);
    }
  };

  const toggle = async (id: number, isActive: boolean) => {
    await adminToggleSource(token, id, !isActive);
    load();
  };

  const remove = async (id: number) => {
    if (!confirm("Delete this source?")) return;
    await adminDeleteSource(token, id);
    load();
  };

  const refresh = async () => {
    setRefreshing(true);
    try {
      await adminRefresh(token);
    } finally {
      setTimeout(() => {
        setRefreshing(false);
        load();
      }, 1500);
    }
  };

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={refresh}
            disabled={refreshing}
            className="rounded bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60"
          >
            {refreshing ? "Refreshing…" : "Refresh feeds now"}
          </button>
          <button
            onClick={onLogout}
            className="rounded border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Logout
          </button>
        </div>
      </header>

      {loading ? (
        <p className="text-slate-500">Loading…</p>
      ) : (
        <>
          {/* Analytics */}
          <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <Stat label="Total Articles" value={analytics?.total_articles ?? 0} />
            <Stat label="Total Clicks" value={analytics?.total_clicks ?? 0} />
            <Stat
              label="Hindi Articles"
              value={analytics?.articles_by_language?.hi ?? 0}
            />
            <Stat
              label="English Articles"
              value={analytics?.articles_by_language?.en ?? 0}
            />
          </section>

          <section className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <Panel title="Top Sources (clicks)">
              {analytics?.top_sources?.length ? (
                <ul className="space-y-1 text-sm">
                  {analytics.top_sources.map((s) => (
                    <li key={s.source} className="flex justify-between">
                      <span>{s.source}</span>
                      <span className="font-mono">{s.clicks}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-500">No clicks yet.</p>
              )}
            </Panel>

            <Panel title="Clicks — last 7 days">
              {analytics?.clicks_last_7d?.length ? (
                <ul className="space-y-1 text-sm">
                  {analytics.clicks_last_7d.map((d) => (
                    <li key={d.date} className="flex justify-between">
                      <span>{d.date}</span>
                      <span className="font-mono">{d.clicks}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-500">No activity.</p>
              )}
            </Panel>
          </section>

          {/* Add source form */}
          <section className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-3 text-lg font-semibold">Add RSS source</h2>
            <form onSubmit={addSource} className="grid grid-cols-1 gap-3 md:grid-cols-5">
              <input
                className="rounded border border-slate-300 px-3 py-2 md:col-span-1"
                placeholder="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
              <input
                className="rounded border border-slate-300 px-3 py-2 md:col-span-2"
                placeholder="RSS URL"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                required
              />
              <select
                className="rounded border border-slate-300 px-3 py-2"
                value={language}
                onChange={(e) => setLanguage(e.target.value as "hi" | "en")}
              >
                <option value="en">English</option>
                <option value="hi">Hindi</option>
              </select>
              <input
                className="rounded border border-slate-300 px-3 py-2"
                placeholder="Category (optional)"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
              <button
                type="submit"
                className="rounded bg-brand-accent px-3 py-2 font-semibold text-white md:col-span-5"
              >
                Add source
              </button>
              {formError ? (
                <p className="text-sm text-red-600 md:col-span-5">{formError}</p>
              ) : null}
            </form>
          </section>

          {/* Sources list */}
          <section className="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
            <h2 className="mb-3 text-lg font-semibold">Sources ({sources.length})</h2>

            {/* Desktop table */}
            <div className="hidden overflow-x-auto md:block">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="py-2">Name</th>
                    <th>Lang</th>
                    <th>Category</th>
                    <th>URL</th>
                    <th>Active</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {sources.map((s) => (
                    <tr key={s.id} className="border-b">
                      <td className="py-2 font-medium">{s.name}</td>
                      <td>{s.language}</td>
                      <td>{s.category || "-"}</td>
                      <td className="max-w-xs truncate text-slate-500">{s.url}</td>
                      <td>
                        <button
                          onClick={() => toggle(s.id, s.is_active)}
                          className={`rounded px-2 py-1 text-xs font-semibold ${
                            s.is_active
                              ? "bg-emerald-100 text-emerald-700"
                              : "bg-slate-200 text-slate-600"
                          }`}
                        >
                          {s.is_active ? "Active" : "Disabled"}
                        </button>
                      </td>
                      <td>
                        <button
                          onClick={() => remove(s.id)}
                          className="text-xs font-semibold text-red-600 hover:underline"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile card list */}
            <ul className="space-y-3 md:hidden">
              {sources.map((s) => (
                <li
                  key={s.id}
                  className="rounded-lg border border-slate-200 p-3 text-sm"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="font-semibold text-slate-900">{s.name}</div>
                      <div className="mt-0.5 text-xs text-slate-500">
                        {s.language === "hi" ? "हिन्दी" : "English"}
                        {s.category ? ` · ${s.category}` : ""}
                      </div>
                      <div className="mt-1 break-all text-xs text-slate-400">
                        {s.url}
                      </div>
                    </div>
                    <button
                      onClick={() => toggle(s.id, s.is_active)}
                      className={`shrink-0 rounded px-2 py-1 text-xs font-semibold ${
                        s.is_active
                          ? "bg-emerald-100 text-emerald-700"
                          : "bg-slate-200 text-slate-600"
                      }`}
                    >
                      {s.is_active ? "Active" : "Off"}
                    </button>
                  </div>
                  <div className="mt-2 text-right">
                    <button
                      onClick={() => remove(s.id)}
                      className="text-xs font-semibold text-red-600 hover:underline"
                    >
                      Delete
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-1 text-2xl font-bold">{value}</div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </h3>
      {children}
    </div>
  );
}
