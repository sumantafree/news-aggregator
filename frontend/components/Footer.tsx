import { t, type Language } from "@/lib/i18n";

export function Footer({ lang }: { lang: Language }) {
  return (
    <footer className="mt-16 border-t border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-slate-500">
        {t(lang, "footer")}
      </div>
    </footer>
  );
}
