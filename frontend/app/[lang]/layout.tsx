import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { isValidLang, t } from "@/lib/i18n";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export async function generateMetadata({
  params,
}: {
  params: { lang: string };
}): Promise<Metadata> {
  if (!isValidLang(params.lang)) return {};
  const lang = params.lang;
  const other = lang === "hi" ? "en" : "hi";
  return {
    title: t(lang, "site_title"),
    description: t(lang, "tagline"),
    alternates: {
      canonical: `${SITE_URL}/${lang}`,
      languages: {
        "hi-IN": `${SITE_URL}/hi`,
        "en-IN": `${SITE_URL}/en`,
        "x-default": `${SITE_URL}/en`,
      },
    },
    openGraph: {
      title: t(lang, "site_title"),
      description: t(lang, "tagline"),
      locale: lang === "hi" ? "hi_IN" : "en_IN",
      alternateLocale: other === "hi" ? "hi_IN" : "en_IN",
    },
  };
}

export function generateStaticParams() {
  return [{ lang: "hi" }, { lang: "en" }];
}

export default function LangLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { lang: string };
}) {
  if (!isValidLang(params.lang)) notFound();
  return (
    <div lang={params.lang} className="min-h-screen bg-slate-50 text-slate-900">
      <Header lang={params.lang} />
      <main className="mx-auto max-w-6xl px-3 py-4 sm:px-4 sm:py-6">{children}</main>
      <Footer lang={params.lang} />
    </div>
  );
}
