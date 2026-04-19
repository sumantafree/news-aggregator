"use client";

import type { TrendingCluster } from "@/lib/types";
import { t, type Language } from "@/lib/i18n";
import { trackClick } from "@/lib/api";

export function TrendingSection({
  clusters,
  lang,
}: {
  clusters: TrendingCluster[];
  lang: Language;
}) {
  if (!clusters || clusters.length === 0) return null;
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-slate-900">
        <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-brand-accent" />
        {t(lang, "trending")}
      </h2>
      <ol className="space-y-3">
        {clusters.slice(0, 6).map((c, idx) => {
          const top = c.articles[0];
          if (!top) return null;
          return (
            <li key={c.cluster_id} className="flex gap-3">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm font-bold text-slate-700">
                {idx + 1}
              </span>
              <div className="min-w-0 flex-1">
                <a
                  href={top.link}
                  target="_blank"
                  rel="noopener noreferrer nofollow"
                  onClick={() =>
                    trackClick({
                      article_id: top.id,
                      source_name: top.source_name,
                      language: top.language,
                    })
                  }
                  className="line-clamp-2 text-sm font-medium text-slate-900 hover:text-brand-accent"
                >
                  {c.top_title}
                </a>
                <div className="mt-1 text-xs text-slate-500">
                  {c.count > 1
                    ? `${c.count} ${lang === "hi" ? "स्रोत" : "sources"}`
                    : top.source_name}
                </div>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
