import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { fetchNews, fetchSources } from "@/lib/api";
import { isValidLang, type Language } from "@/lib/i18n";
import { NewsGrid } from "@/components/NewsGrid";

export const revalidate = 60;

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export async function generateMetadata({
  params,
}: {
  params: { lang: string; slug: string };
}): Promise<Metadata> {
  if (!isValidLang(params.lang)) return {};
  return {
    title: `${params.slug} — News`,
    alternates: {
      canonical: `${SITE_URL}/${params.lang}/source/${params.slug}`,
    },
  };
}

export default async function SourcePage({
  params,
}: {
  params: { lang: string; slug: string };
}) {
  if (!isValidLang(params.lang)) notFound();
  const lang: Language = params.lang;
  const [articles, sources] = await Promise.all([
    fetchNews({ lang, source: params.slug, limit: 60 }).catch(() => []),
    fetchSources(lang).catch(() => []),
  ]);
  const source = sources.find((s) => s.slug === params.slug);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">
        {source?.name || params.slug}
      </h1>
      <NewsGrid articles={articles} lang={lang} />
    </div>
  );
}
