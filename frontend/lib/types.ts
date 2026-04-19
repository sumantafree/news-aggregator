export type Language = "hi" | "en";

export interface Article {
  id: number;
  title: string;
  slug: string;
  link: string;
  summary?: string | null;
  ai_summary?: string | null;
  image?: string | null;
  language: Language;
  category?: string | null;
  source_name: string;
  published_at: string;
  trending_score?: number;
  cluster_id?: string | null;
}

export interface Source {
  id: number;
  name: string;
  slug: string;
  url: string;
  language: Language;
  category?: string | null;
  is_active: boolean;
}

export interface TrendingCluster {
  cluster_id: string;
  language: Language;
  count: number;
  top_title: string;
  articles: Article[];
}

export interface Analytics {
  total_articles: number;
  total_clicks: number;
  articles_by_language: Record<string, number>;
  top_sources: { source: string; clicks: number }[];
  top_trending: { cluster_id: string; title: string; language: string }[];
  clicks_last_7d: { date: string; clicks: number }[];
}
