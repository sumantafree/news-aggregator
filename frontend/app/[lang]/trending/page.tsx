import { notFound } from "next/navigation";
import { fetchTrending } from "@/lib/api";
import { isValidLang, t, type Language } from "@/lib/i18n";
import { NewsCard } from "@/components/NewsCard";

export const revalidate = 120;

export default async function TrendingPage({
  params,
}: {
  params: { lang: string };
}) {
  if (!isValidLang(params.lang)) notFound();
  const lang: Language = params.lang;
  const clusters = await fetchTrending(lang, 20).catch(() => []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">
        {t(lang, "trending")}
      </h1>

      <div className="space-y-8">
        {clusters.map((c) => (
          <section key={c.cluster_id} className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-3 text-lg font-bold text-slate-900">{c.top_title}</h2>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {c.articles.map((a) => (
                <NewsCard key={a.id} article={a} lang={lang} />
              ))}
            </div>
          </section>
        ))}
        {clusters.length === 0 ? (
          <p className="text-slate-500">{t(lang, "no_news")}</p>
        ) : null}
      </div>
    </div>
  );
}
