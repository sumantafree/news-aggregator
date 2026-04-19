import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { fetchNews } from "@/lib/api";
import { isValidLang, type Language } from "@/lib/i18n";
import { NewsGrid } from "@/components/NewsGrid";
import { AdSlot } from "@/components/AdSlot";

export const revalidate = 60;

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export async function generateMetadata({
  params,
}: {
  params: { lang: string; slug: string };
}): Promise<Metadata> {
  if (!isValidLang(params.lang)) return {};
  const cat = decodeURIComponent(params.slug);
  const title =
    params.lang === "hi"
      ? `${cat} — ताज़ा समाचार`
      : `${cat.charAt(0).toUpperCase()}${cat.slice(1)} — Latest News`;
  return {
    title,
    alternates: {
      canonical: `${SITE_URL}/${params.lang}/category/${cat}`,
      languages: {
        "hi-IN": `${SITE_URL}/hi/category/${cat}`,
        "en-IN": `${SITE_URL}/en/category/${cat}`,
      },
    },
  };
}

export default async function CategoryPage({
  params,
}: {
  params: { lang: string; slug: string };
}) {
  if (!isValidLang(params.lang)) notFound();
  const lang: Language = params.lang;
  const category = decodeURIComponent(params.slug);
  const articles = await fetchNews({
    lang,
    category,
    limit: 60,
  }).catch(() => []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold capitalize text-slate-900 sm:text-3xl">
        {category}
      </h1>
      <AdSlot slot="category-top" className="h-24" />
      <NewsGrid articles={articles} lang={lang} />
    </div>
  );
}
