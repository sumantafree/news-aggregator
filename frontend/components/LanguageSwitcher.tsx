"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Language } from "@/lib/types";

export function LanguageSwitcher({ current }: { current: Language }) {
  const pathname = usePathname() || "/";
  const other: Language = current === "hi" ? "en" : "hi";

  // Swap the first path segment if it's /hi or /en, otherwise prepend.
  const segments = pathname.split("/");
  let newPath: string;
  if (segments[1] === "hi" || segments[1] === "en") {
    segments[1] = other;
    newPath = segments.join("/") || "/";
  } else {
    newPath = `/${other}${pathname === "/" ? "" : pathname}`;
  }

  return (
    <Link
      href={newPath}
      className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
      aria-label="Switch language"
    >
      {other === "hi" ? "हिन्दी" : "English"}
    </Link>
  );
}
