import type { Article } from "@/lib/types";
import { t, type Language } from "@/lib/i18n";
import { NewsCard } from "./NewsCard";

export function NewsGrid({ articles, lang }: { articles: Article[]; lang: Language }) {
  if (!articles || articles.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
        {t(lang, "no_news")}
      </div>
    );
  }
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
      {articles.map((a) => (
        <NewsCard key={a.id} article={a} lang={lang} />
      ))}
    </div>
  );
}
