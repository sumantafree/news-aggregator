"use client";

import Link from "next/link";
import { useState } from "react";
import { t, type Language } from "@/lib/i18n";
import { LanguageSwitcher } from "./LanguageSwitcher";

export function Header({ lang }: { lang: Language }) {
  const [open, setOpen] = useState(false);
  const close = () => setOpen(false);

  const nav = [
    { href: `/${lang}`, label: t(lang, "home") },
    { href: `/${lang}/trending`, label: t(lang, "trending") },
    { href: `/${lang}/sources`, label: t(lang, "sources") },
    { href: "/admin", label: t(lang, "admin") },
  ];

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
        <Link href={`/${lang}`} className="flex items-center gap-2" onClick={close}>
          <span className="inline-block h-7 w-7 rounded bg-brand-accent" aria-hidden />
          <span className="text-lg font-bold tracking-tight text-slate-900 sm:text-xl">
            NewsPulse
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden items-center gap-5 text-sm font-medium text-slate-700 md:flex">
          {nav.map((n) => (
            <Link key={n.href} href={n.href} className="hover:text-brand-accent">
              {n.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <LanguageSwitcher current={lang} />

          {/* Hamburger (mobile only) */}
          <button
            type="button"
            onClick={() => setOpen((o) => !o)}
            aria-label="Toggle menu"
            aria-expanded={open}
            className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-700 md:hidden"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
            >
              {open ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </>
              ) : (
                <>
                  <line x1="3" y1="6" x2="21" y2="6" />
                  <line x1="3" y1="12" x2="21" y2="12" />
                  <line x1="3" y1="18" x2="21" y2="18" />
                </>
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      {open && (
        <nav className="border-t border-slate-200 bg-white md:hidden">
          <ul className="mx-auto flex max-w-6xl flex-col px-4 py-2">
            {nav.map((n) => (
              <li key={n.href}>
                <Link
                  href={n.href}
                  onClick={close}
                  className="block rounded-md px-2 py-3 text-base font-medium text-slate-700 hover:bg-slate-50 hover:text-brand-accent"
                >
                  {n.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </header>
  );
}
