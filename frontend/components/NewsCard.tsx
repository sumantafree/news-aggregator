"use client";

import type { Article } from "@/lib/types";
import { timeAgo } from "@/lib/format";
import { trackClick } from "@/lib/api";
import { t, type Language } from "@/lib/i18n";

export function NewsCard({ article, lang }: { article: Article; lang: Language }) {
  const handleClick = () => {
    trackClick({
      article_id: article.id,
      source_name: article.source_name,
      language: article.language,
      referer: typeof window !== "undefined" ? window.location.href : undefined,
    });
  };

  return (
    <article className="group flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md">
      {article.image ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={article.image}
          alt=""
          loading="lazy"
          className="h-44 w-full object-cover"
          onError={(e) => ((e.currentTarget as HTMLImageElement).style.display = "none")}
        />
      ) : (
        <div className="h-3 w-full bg-gradient-to-r from-brand-accent to-amber-500" />
      )}

      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-center justify-between text-xs font-medium text-slate-500">
          <span className="rounded bg-slate-100 px-2 py-0.5 text-slate-700">
            {article.source_name}
          </span>
          <time dateTime={article.published_at}>{timeAgo(article.published_at, lang)}</time>
        </div>

        <h3 className="line-clamp-3 text-base font-semibold leading-snug text-slate-900 group-hover:text-brand-accent">
          <a
            href={article.link}
            onClick={handleClick}
            target="_blank"
            rel="noopener noreferrer nofollow"
          >
            {article.title}
          </a>
        </h3>

        {article.ai_summary ? (
          <p className="line-clamp-3 text-sm text-slate-600">{article.ai_summary}</p>
        ) : null}

        <div className="mt-auto pt-2">
          <a
            href={article.link}
            onClick={handleClick}
            target="_blank"
            rel="noopener noreferrer nofollow"
            className="inline-flex items-center gap-1 text-sm font-medium text-brand-accent hover:underline"
          >
            {t(lang, "read_more")} {article.source_name} →
          </a>
        </div>
      </div>
    </article>
  );
}
