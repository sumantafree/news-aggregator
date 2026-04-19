# Dual-Language News Aggregator (Hindi + English)

A production-ready, SaaS-grade news aggregator that collects news from major Hindi and English RSS feeds, deduplicates & clusters them, and redirects users to the original publisher (Google News–style traffic redirection model).

## Tech Stack

- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Backend:** FastAPI (Python 3.11+) + SQLAlchemy
- **Database:** PostgreSQL
- **Cache:** Redis (with in-memory fallback)
- **Queue:** Celery (RSS refresh) + FastAPI background tasks
- **Deployment:** Docker + docker-compose

## Features

- Aggregates news from 10 major Hindi + English RSS sources
- Stores only: title, source, publish date, link, summary, image, language
- Redirects to original publisher (no republishing)
- Fuzzy deduplication (85% threshold)
- Trending score + topic clustering
- AI-generated short summaries (Hindi + English)
- SSR with dynamic meta tags, hreflang, JSON-LD NewsArticle schema
- Auto-generated sitemap.xml & robots.txt
- Admin dashboard with JWT auth
- Redis cache (10 min TTL)
- Click tracking & analytics
- AdSense / sponsored / affiliate monetization slots
- Rate-limited APIs

## Quick Start

### With Docker (recommended)

```bash
cd news-aggregator
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000/docs

### Manual

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Default admin
- username: `admin`
- password: `admin123` (override via `ADMIN_PASSWORD` env var)

## Project Structure

```
news-aggregator/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # config, security, cache
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # RSS fetch, dedup, AI, trending
│   │   └── tasks/        # Celery / background jobs
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/              # Next.js App Router
│   ├── components/
│   ├── lib/
│   └── Dockerfile
└── docker-compose.yml
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET    | `/news` | List news (filters: `lang`, `source`, `category`, `limit`) |
| GET    | `/sources` | List active sources |
| GET    | `/trending` | Trending clusters |
| POST   | `/track` | Log click |
| POST   | `/admin/login` | JWT login |
| POST   | `/admin/source` | Add RSS feed (auth) |
| DELETE | `/admin/source/{id}` | Remove feed (auth) |
| PATCH  | `/admin/source/{id}` | Toggle active (auth) |
| GET    | `/admin/analytics` | Dashboard stats (auth) |
| POST   | `/admin/refresh` | Manual RSS refresh (auth) |

## License

MIT
