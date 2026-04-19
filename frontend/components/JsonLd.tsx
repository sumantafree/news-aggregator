import type { Article } from "@/lib/types";

export function NewsArticleJsonLd({
  article,
  siteUrl,
}: {
  article: Article;
  siteUrl: string;
}) {
  const json = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: article.title,
    datePublished: article.published_at,
    inLanguage: article.language === "hi" ? "hi-IN" : "en-IN",
    url: article.link,
    mainEntityOfPage: `${siteUrl}/${article.language}/article/${article.id}/${article.slug}`,
    image: article.image ? [article.image] : undefined,
    publisher: {
      "@type": "Organization",
      name: article.source_name,
    },
    description: article.ai_summary || article.summary || article.title,
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(json) }}
    />
  );
}

export function ItemListJsonLd({
  articles,
  siteUrl,
  lang,
}: {
  articles: Article[];
  siteUrl: string;
  lang: "hi" | "en";
}) {
  const json = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    itemListElement: articles.slice(0, 20).map((a, i) => ({
      "@type": "ListItem",
      position: i + 1,
      url: `${siteUrl}/${lang}/article/${a.id}/${a.slug}`,
      name: a.title,
    })),
  };
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(json) }}
    />
  );
}
