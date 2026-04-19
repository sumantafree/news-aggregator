import { notFound } from "next/navigation";
import { fetchCategories, fetchNews, fetchTrending } from "@/lib/api";
import { isValidLang, t } from "@/lib/i18n";
import { NewsGrid } from "@/components/NewsGrid";
import { CategoryFilter } from "@/components/CategoryFilter";
import { TrendingSection } from "@/components/TrendingSection";
import { AdSlot } from "@/components/AdSlot";
import { ItemListJsonLd } from "@/components/JsonLd";

export const revalidate = 60;

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export default async function LangHome({ params }: { params: { lang: string } }) {
  if (!isValidLang(params.lang)) notFound();
  const lang = params.lang;

  const [articles, trending, categories] = await Promise.all([
    fetchNews({ lang, limit: 48 }).catch(() => []),
    fetchTrending(lang, 6).catch(() => []),
    fetchCategories().catch(() => []),
  ]);

  return (
    <div className="space-y-6 sm:space-y-8">
      <section className="space-y-3">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl md:text-4xl">
          {t(lang, "latest")}
        </h1>
        <p className="max-w-3xl text-sm text-slate-600 sm:text-base">
          {t(lang, "tagline")}
        </p>
        <CategoryFilter categories={categories} lang={lang} />
      </section>

      <AdSlot slot="home-top" className="h-24" />

      <div className="grid grid-cols-1 gap-4 sm:gap-6 lg:grid-cols-[1fr_320px]">
        <section>
          <NewsGrid articles={articles} lang={lang} />
        </section>
        <aside className="order-first space-y-4 lg:order-last">
          <TrendingSection clusters={trending} lang={lang} />
          <AdSlot slot="home-sidebar" className="h-64" />
        </aside>
      </div>

      <ItemListJsonLd articles={articles} siteUrl={SITE_URL} lang={lang} />
    </div>
  );
}
