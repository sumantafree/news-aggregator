import { notFound } from "next/navigation";
import Link from "next/link";
import { fetchSources } from "@/lib/api";
import { isValidLang, t } from "@/lib/i18n";

export const revalidate = 300;

export default async function SourcesPage({ params }: { params: { lang: string } }) {
  if (!isValidLang(params.lang)) notFound();
  const sources = await fetchSources(params.lang).catch(() => []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-slate-900">{t(params.lang, "sources")}</h1>
      <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {sources.map((s) => (
          <li key={s.id}>
            <Link
              href={`/${params.lang}/source/${s.slug}`}
              className="block rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md"
            >
              <div className="text-base font-semibold text-slate-900">{s.name}</div>
              <div className="mt-1 text-xs text-slate-500">
                {s.language === "hi" ? "हिन्दी" : "English"}
                {s.category ? ` · ${s.category}` : ""}
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
