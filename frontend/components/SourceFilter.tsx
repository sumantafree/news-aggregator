import Link from "next/link";
import type { Source } from "@/lib/types";
import { type Language } from "@/lib/i18n";

export function SourceFilter({
  sources,
  lang,
  active,
}: {
  sources: Source[];
  lang: Language;
  active?: string;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {sources.map((s) => (
        <Link
          key={s.id}
          href={`/${lang}/source/${s.slug}`}
          className={`rounded-full border px-3 py-1 text-sm ${
            active === s.slug
              ? "border-brand-accent bg-brand-accent text-white"
              : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          {s.name}
        </Link>
      ))}
    </div>
  );
}
