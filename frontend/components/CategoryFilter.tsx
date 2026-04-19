import Link from "next/link";
import { t, type Language } from "@/lib/i18n";

export function CategoryFilter({
  categories,
  lang,
  active,
}: {
  categories: string[];
  lang: Language;
  active?: string;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <Link
        href={`/${lang}`}
        className={`rounded-full border px-3 py-1 text-sm ${
          !active
            ? "border-brand-accent bg-brand-accent text-white"
            : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
        }`}
      >
        {t(lang, "all")}
      </Link>
      {categories.map((c) => (
        <Link
          key={c}
          href={`/${lang}/category/${c}`}
          className={`rounded-full border px-3 py-1 text-sm capitalize ${
            active === c
              ? "border-brand-accent bg-brand-accent text-white"
              : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          {c}
        </Link>
      ))}
    </div>
  );
}
