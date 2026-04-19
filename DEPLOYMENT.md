# Deployment Guide — Subdomain on cPanel + Render + Supabase + Vercel

This guide takes your NewsPulse aggregator from zero to **https://news.yourdomain.com**, fully live, on the free tier.

## Architecture

```
[ cPanel DNS ]  ──CNAME──▶  [ Vercel (Next.js frontend) ] ──HTTPS──▶  [ Render.com (FastAPI backend) ] ──▶ [ Supabase (Postgres) ]
                                                                              ▲
                                                                              │ every 10 min
                                                               [ Render Cron Job ─ POST /cron/refresh ]
```

**Why this split?** cPanel shared hosting almost never runs Python/FastAPI/Postgres properly. We use cPanel **only** as your DNS manager (it already owns your domain) and host the actual app on free PaaS services.

---

## Step 0 — Push the code to GitHub

1. Create a new empty repo on GitHub, e.g. `news-aggregator`.
2. From the project folder:
   ```bash
   cd G:/Ai-assitent/news-aggregator
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USER/news-aggregator.git
   git push -u origin main
   ```

---

## Step 1 — Database on Supabase (free)

1. Go to <https://supabase.com> → **New project**.
   - Name: `news-aggregator`
   - Region: closest to your users (Mumbai for India)
   - Strong DB password — **save it**.
2. Once provisioned, open **Project Settings → Database → Connection string → URI**.
3. Choose the **Transaction pooler** (port **6543**) string. It looks like:
   ```
   postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
   ```
4. Convert to SQLAlchemy format by replacing `postgresql://` with `postgresql+psycopg2://`:
   ```
   postgresql+psycopg2://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
   ```
   Keep this — you'll paste it into Render as `DATABASE_URL`.

> Tables are created automatically on first backend startup — no SQL migrations needed.

---

## Step 2 — Backend on Render.com (free Web Service)

1. Go to <https://render.com> → **New → Blueprint**.
2. Connect your GitHub account → select the `news-aggregator` repo.
3. Render detects `render.yaml` and shows two services: `news-aggregator-api` + `news-aggregator-refresh`.
4. Click **Apply** — it will prompt for the secret env vars. Fill in:

   **For `news-aggregator-api`:**
   | Var | Value |
   |---|---|
   | `DATABASE_URL` | the Supabase pooler URI from Step 1 |
   | `ADMIN_PASSWORD` | a strong password you'll use to log in to `/admin` |
   | `ALLOWED_ORIGINS` | `https://news.yourdomain.com` (your final subdomain) |
   | `SITE_URL` | `https://news.yourdomain.com` |
   | `SECRET_KEY` | leave as **Generate** |
   | `CRON_SECRET` | leave as **Generate**, then copy value to cron job below |

5. Once deployed, note the public URL — e.g. `https://news-aggregator-api.onrender.com`.
6. Test it: open `https://news-aggregator-api.onrender.com/health` → `{"status":"ok"}`.
7. Open `/docs` to see the Swagger UI.

> The free tier sleeps after 15 min idle. The cron job (next step) keeps it warm.

---

## Step 3 — Configure the Cron Job on Render

Render's Blueprint already created `news-aggregator-refresh`. Open it and set:

| Var | Value |
|---|---|
| `API_URL` | `https://news-aggregator-api.onrender.com` (from Step 2) |
| `CRON_SECRET` | the same value you generated for the backend in Step 2 |

Schedule is already `*/10 * * * *` (every 10 min). Save — it will run automatically.

---

## Step 4 — Frontend on Vercel

1. Go to <https://vercel.com> → **Add New… → Project** → import the same GitHub repo.
2. **Root Directory**: `frontend`
3. **Framework preset**: Next.js (auto-detected)
4. **Environment variables** (Production):
   | Var | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://news-aggregator-api.onrender.com` |
   | `NEXT_PUBLIC_SITE_URL` | `https://news.yourdomain.com` |
   | `NEXT_PUBLIC_ADSENSE_CLIENT` | your AdSense client ID (optional, leave empty for now) |
5. **Before deploying**, open `frontend/vercel.json` and replace `YOUR-BACKEND.onrender.com` with your real Render backend host. Commit + push.
6. Click **Deploy**. You'll get a URL like `news-aggregator-xyz.vercel.app` — verify it loads.

---

## Step 5 — Point your cPanel subdomain to Vercel

1. In Vercel: **Project → Settings → Domains → Add** → enter `news.yourdomain.com` → Add.
2. Vercel shows the required DNS record — usually:
   ```
   Type:  CNAME
   Name:  news
   Value: cname.vercel-dns.com
   ```
3. Log in to **cPanel → Zone Editor** (or **Domains → DNS**).
4. Select your domain → **Add Record**:
   - **Type:** CNAME
   - **Name:** `news` (cPanel will append your domain automatically)
   - **Target/Value:** `cname.vercel-dns.com.` (with trailing dot)
   - **TTL:** `14400` (default is fine)
5. Save. DNS propagation usually takes 5–30 minutes.
6. Back in Vercel, the domain row will flip from **Invalid Configuration** to a green check + HTTPS cert issued automatically.

> If cPanel also runs the main site (`yourdomain.com`) on your shared hosting, **leave that alone**. You're only adding a record for the `news` subdomain.

---

## Step 6 — Final smoke test

Open `https://news.yourdomain.com` on:
- Desktop Chrome
- Phone (should see hamburger menu, stacked cards)
- Tablet

Checks:
- [ ] Homepage shows news cards
- [ ] Language toggle `English ⇄ हिन्दी` works
- [ ] Clicking a news card opens the original publisher in a new tab
- [ ] `/admin` login works with your `ADMIN_PASSWORD`
- [ ] `/admin` → **Refresh feeds now** runs without error
- [ ] `https://news.yourdomain.com/sitemap.xml` returns XML
- [ ] `https://news.yourdomain.com/robots.txt` returns text

---

## Step 7 — After deployment

### Submit to Google
1. <https://search.google.com/search-console> → Add property → `https://news.yourdomain.com`
2. Verify via DNS TXT record (again in cPanel Zone Editor) **or** HTML file (drop in `frontend/public/`).
3. Submit sitemap: `https://news.yourdomain.com/sitemap.xml`.

### Enable AdSense
1. Apply at <https://adsense.google.com>.
2. Once approved, set `NEXT_PUBLIC_ADSENSE_CLIENT=ca-pub-XXXXXXXXXXX` in Vercel → redeploy.
3. The `AdSlot` component activates automatically.

### Change the admin password
- Render → `news-aggregator-api` → Environment → update `ADMIN_PASSWORD` → Save → service auto-redeploys.

---

## Cost breakdown

| Service | Free tier | What you get |
|---|---|---|
| Supabase | 500 MB Postgres, 2 GB bandwidth | enough for ~500k articles |
| Render Web Service | 750 hrs/month | one always-on backend |
| Render Cron Job | free | feed refresh every 10 min |
| Vercel Hobby | 100 GB bandwidth | plenty for a news site |
| cPanel (existing) | already paid | DNS only |
| **Total** | **$0/month** | until you outgrow free tiers |

---

## Troubleshooting

**Backend cold-start / 502 on first request**
Free Render sleeps after 15 min. First request after idle takes 30–60s. The cron job every 10 min mostly prevents this.

**Articles not appearing**
Check `https://<api>.onrender.com/news?lang=all&limit=5`. If empty:
- Wait 2 min after first deploy (background initial ingest runs on startup).
- Or manually hit **Admin → Refresh feeds now**.
- Check Render logs for "RSS fetch failed" lines — some feeds rotate URLs; disable them in the admin UI.

**CORS errors in the browser**
Ensure `ALLOWED_ORIGINS` on Render exactly matches your final site URL **including** the scheme and no trailing slash.

**Supabase "too many connections"**
Make sure you used the **pooler** URI (port 6543), not the direct connection (5432). The pooler allows hundreds of connections on free tier.

**Hindi text shows as boxes on mobile**
The Noto Sans Devanagari font is loaded from Google Fonts. If your users are in a region where Google Fonts is blocked, self-host it in `frontend/public/fonts/` and reference it in `app/globals.css`.
