import type { Language } from "./types";
export type { Language };

export const translations = {
  en: {
    site_title: "NewsPulse — Latest Hindi & English News",
    tagline: "Top headlines from trusted publishers, updated every 10 minutes.",
    latest: "Latest News",
    trending: "Trending Now",
    sources: "Sources",
    categories: "Categories",
    all: "All",
    read_more: "Read on",
    published: "Published",
    by: "by",
    switch_lang: "हिन्दी",
    home: "Home",
    admin: "Admin",
    footer: "© NewsPulse — aggregating public RSS feeds. All rights belong to original publishers.",
    no_news: "No news yet. The ingest runs in the background — refresh in a moment.",
  },
  hi: {
    site_title: "न्यूज़पल्स — ताज़ा हिन्दी और अंग्रेज़ी समाचार",
    tagline: "भरोसेमंद प्रकाशकों से शीर्ष समाचार, हर 10 मिनट में अपडेट।",
    latest: "ताज़ा ख़बरें",
    trending: "ट्रेंडिंग",
    sources: "स्रोत",
    categories: "श्रेणियाँ",
    all: "सभी",
    read_more: "पढ़ें",
    published: "प्रकाशित",
    by: "द्वारा",
    switch_lang: "English",
    home: "मुखपृष्ठ",
    admin: "एडमिन",
    footer: "© न्यूज़पल्स — सार्वजनिक RSS फ़ीड से एकत्रित। सभी अधिकार मूल प्रकाशकों के पास हैं।",
    no_news: "अभी कोई समाचार नहीं। पृष्ठभूमि में डेटा आ रहा है — थोड़ी देर में पुनः आज़माएँ।",
  },
} as const;

export function t(lang: Language, key: keyof typeof translations["en"]): string {
  return (translations[lang] ?? translations.en)[key];
}

export const isValidLang = (l: string): l is Language => l === "hi" || l === "en";
