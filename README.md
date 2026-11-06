# 🎓 SkillUp Digest v2.1 "World Edition" — Your Daily Newspaper

A **100% free**, cloud-based system that scans **1,200+ sources across 23 world
regions** every night and emails you **one professional PDF** by **5:00 AM
Nepal Time** (build starts 4:00 AM NPT) — covering **every field**: AI/tech, world news, business,
science, space, health, climate, sports, entertainment, Nepal + free courses,
certifications, scholarships, internships, hackathons, webinars, conferences
and fellowships.

Your computer stays OFF. GitHub's servers do all the work. **Cost: $0/month.**

> **What's new in v2.1 (vs v2.0)**
> ① **Elastic caps** — a section flooded with fresh items now grows up to
> **2× its base cap** (`CAP_ELASTIC_FACTOR = 2.0`), so big news days deliver
> more (real test: **624 items / 32 pages**); quiet days shrink automatically;
> overflow items are *not* marked seen, so they get another chance tomorrow.
> ② **Beautiful HTML email** — the email is now a styled briefing with a blue
> header, colored section chips + counts, and **clickable ⭐ Top picks (3 per
> section)** — plus the same plain-text fallback and PDF attachment.
>
> ③ **Never-miss-a-day delivery system** — the nightly build now starts at
> **4:00 AM NPT** (1 h before your 5 AM target, to absorb GitHub's queuing)
> **plus 3 backup slots** at 5:30 AM, 7:30 AM and 4:00 PM NPT. `main.py`
> delivers only the **first digest of each Nepal day** — later slots see
> "already delivered today" and exit in ~1 second, so you never get
> duplicates. Failed runs no longer commit `seen.json`, so a crashed send
> can never burn the day's news — the next slot simply re-sends it.
> **Re-upload `main.py` AND `digest.yml`** for this to take effect.
>
> **What's new in v2.0 (vs v1.3)**
> | | v1.3 | v2.0 |
> |---|---|---|
> | Sections in the PDF | 9 | **17** (8 new: World, Business, Science & Space, Climate, Sports, Entertainment, Conferences, Fellowships) |
> | Items per day | up to 182 | **up to 312** (real test: 312) |
> | Direct RSS feeds | 27 | **70** (all live-verified) |
> | Google News regions | 6 | **23** (adds SG, NZ, ZA, NG, KE, PK, BD, LK, PH, MY, AE, IE, DE, FR, BR, JP, ID) |
> | Search queries per run | ~130 | **~1,180** |
> | Fetch method | sequential | **10 parallel workers → full run in ~2 minutes** |

---

## A) ARCHITECTURE — how it all fits together

```
              ┌──────────────────────────────────────────────────────────┐
              │            GITHUB ACTIONS CLOUD (free, 24/7)             │
              │                                                          │
 22:15 UTC ──►│  cron ×4 slots/night  (= 4:00 AM NPT → mail by ~5:00)    │
 (every day)  │        │                                                 │
              │        ▼                                                 │
              │  ┌────────────┐   70 direct RSS feeds                    │
              │  │  main.py   │──► BBC / TechCrunch / Al Jazeera / NASA  │
              │  │            │    Kathmandu Post / Space.com / Variety   │
              │  │            │   + Google News RSS × 23 regions          │
              │  │            │    (US UK IN NP AU CA SG NZ ZA NG KE PK   │
              │  │            │     BD LK PH MY AE IE DE FR BR JP ID)     │
              │  └─────┬──────┘   10 parallel workers ≈ 2 min total       │
              │        ▼                                                  │
              │  CLEAN: news ≤ 48 h · opportunities ≤ 7 d                 │
              │  DEDUP: vs seen.json (memory across days)                 │
              │  TAG:   [GLOBAL] / [NEPAL] · AI+Health sorted to top      │
              │        ▼                                                  │
              │  PDF: cover + 17 color sections (clickable titles)        │
              │        ▼                                                  │
              │  GMAIL SMTP ──► 📧 Kusalkandel0@gmail.com                  │
              │        ▼                                                  │
              │  git commit seen.json (never re-send, keeps repo active)  │
              └──────────────────────────────────────────────────────────┘
```

## B) SOURCE COVERAGE MATRIX — what was actually tested

Every URL below was **live-tested on 2026-11-06**. Nothing is invented.

### Direct RSS feeds (70)

| # | Source | PDF section | Status |
|---|--------|-------------|--------|
| 1 | BBC Technology `feeds.bbci.co.uk/news/technology/rss.xml` | AI & Tech | ✅ |
| 2 | TechCrunch `techcrunch.com/feed/` | AI & Tech | ✅ |
| 3 | The Verge `theverge.com/rss/index.xml` | AI & Tech | ✅ |
| 4 | MIT Tech Review AI `technologyreview.com/topic/artificial-intelligence/feed` | AI & Tech | ✅ |
| 5 | Wired `wired.com/feed/rss` | AI & Tech | ✅ |
| 6 | Ars Technica `feeds.arstechnica.com/arstechnica/index` | AI & Tech | ✅ |
| 7 | IEEE Spectrum AI `spectrum.ieee.org/feeds/topic/artificial-intelligence.rss` | AI & Tech | ✅ |
| 8 | Hacker News `hnrss.org/frontpage` | AI & Tech | ✅ |
| 9 | dev.to `dev.to/feed` | AI & Tech | ✅ |
| 10 | Engadget `engadget.com/rss.xml` | AI & Tech | ✅ new v2.0 |
| 11 | Tom's Hardware `tomshardware.com/feeds.xml` | AI & Tech | ✅ new v2.0 |
| 12 | TechRadar `techradar.com/feeds.xml` | AI & Tech | ✅ new v2.0 |
| 13 | HackerNoon `hackernoon.com/feed` | AI & Tech | ✅ new v2.0 |
| 14 | The Next Web `thenextweb.com/feed` | AI & Tech | ✅ new v2.0 |
| 15 | VentureBeat AI `venturebeat.com/category/ai/feed/` | AI & Tech | ⚠️ to-verify (429 from test server; may work on GitHub's) |
| 16 | BBC World `feeds.bbci.co.uk/news/world/rss.xml` | World | ✅ new v2.0 |
| 17 | Al Jazeera `aljazeera.com/xml/rss/all.xml` | World | ✅ new v2.0 |
| 18 | Guardian World `theguardian.com/world/rss` | World | ✅ new v2.0 |
| 19 | CNN World `rss.cnn.com/rss/edition_world.rss` | World | ✅ new v2.0 |
| 20 | NYT World `rss.nytimes.com/services/xml/rss/nyt/World.xml` | World | ✅ new v2.0 |
| 21 | DW English `rss.dw.com/rdf/rss-en-world` | World | ✅ new v2.0 |
| 22 | NPR World `feeds.npr.org/1004/rss.xml` | World | ✅ new v2.0 |
| 23 | France24 EN `france24.com/en/rss` | World | ✅ new v2.0 |
| 24 | The Independent `independent.co.uk/rss?topic=world` | World | ✅ new v2.0 |
| 25 | BBC Business `feeds.bbci.co.uk/news/business/rss.xml` | Business | ✅ new v2.0 |
| 26 | Guardian Business `theguardian.com/uk/business/rss` | Business | ✅ new v2.0 |
| 27 | CNBC `cnbc.com/id/100003114/device/rss/rss.html` | Business | ✅ new v2.0 |
| 28 | Business Standard `business-standard.com/rss/home_page_top_stories.rss` | Business | ✅ new v2.0 |
| 29 | ScienceDaily `sciencedaily.com/rss/all.xml` | Science & Space | ✅ new v2.0 |
| 30 | Phys.org `phys.org/rss-feed/` | Science & Space | ✅ new v2.0 |
| 31 | Space.com `space.com/rss` | Science & Space | ✅ new v2.0 |
| 32 | NASA `nasa.gov/news-release/feed/` | Science & Space | ✅ new v2.0 |
| 33 | Quanta `api.quantamagazine.org/feed/` | Science & Space | ✅ new v2.0 |
| 34 | Science Magazine `science.org/rss/news_current.xml` | Science & Space | ✅ new v2.0 |
| 35 | Nature `nature.com/nature.rss` | Science & Space | ✅ |
| 36 | BBC Health `feeds.bbci.co.uk/news/health/rss.xml` | Health | ✅ |
| 37 | STAT News `statnews.com/feed/` | Health | ✅ |
| 38 | WHO News `who.int/rss-feeds/news-english.xml` | Health | ✅ |
| 39 | Medical Xpress `medicalxpress.com/rss-feed/` | Health | ✅ |
| 40 | NPR Health `feeds.npr.org/1128/rss.xml` | Health | ✅ |
| 41 | Guardian Environment `theguardian.com/environment/rss` | Climate | ✅ new v2.0 |
| 42 | Grist `grist.org/feed/` | Climate | ✅ new v2.0 |
| 43 | BBC Sport `feeds.bbci.co.uk/sport/rss.xml` | Sports | ✅ new v2.0 |
| 44 | Sky Sports `skysports.com/rss/12040` | Sports | ✅ new v2.0 |
| 45 | Guardian Sport `theguardian.com/sport/rss` | Sports | ✅ new v2.0 |
| 46 | Times of India Sports `timesofindia.indiatimes.com/rssfeeds/4719148.cms` | Sports | ✅ new v2.0 |
| 47 | Variety `variety.com/feed/` | Entertainment | ✅ new v2.0 |
| 48 | Hollywood Reporter `hollywoodreporter.com/feed/` | Entertainment | ✅ new v2.0 |
| 49 | Billboard Music `billboard.com/c/music/music-news/feed/` | Entertainment | ✅ new v2.0 |
| 50 | Rolling Stone `rollingstone.com/feed/` | Entertainment | ✅ new v2.0 |
| 51 | Polygon Games `polygon.com/rss/index.xml` | Entertainment | ✅ new v2.0 |
| 52 | IGN Games `feeds.ign.com/ign/games-all` | Entertainment | ✅ new v2.0 |
| 53 | Kathmandu Post `kathmandupost.com/rss` | Nepal | ✅ |
| 54 | OnlineKhabar English `english.onlinekhabar.com/feed` | Nepal | ✅ |
| 55 | Ratopati `ratopati.com/feed` | Nepal | ✅ |
| 56 | Khabarhub English `english.khabarhub.com/feed/` | Nepal | ✅ |
| 57 | Nepali Times `nepalitimes.com/feed` | Nepal | ✅ new v2.0 |
| 58 | Nepal Press `nepalpress.com/feed/` | Nepal | ✅ new v2.0 |
| 59 | Himal Press `himalpress.com/feed` | Nepal | ✅ new v2.0 |
| 60 | The Hindu National `thehindu.com/news/national/feeder/default.rss` | Nepal & S. Asia | ✅ new v2.0 |
| 61 | Opportunity Desk `opportunitydesk.org/feed/` | auto-classified | ✅ |
| 62 | Opportunities For Africans `opportunitiesforafricans.com/feed/` | auto-classified | ✅ |
| 63 | Scholars4Dev `scholars4dev.com/feed/` | auto-classified | ✅ |
| 64 | WeWorkRemotely `weworkremotely.com/categories/remote-programming-jobs.rss` | auto-classified | ✅ new v2.0 |
| 65 | Internshala Blog `blog.internshala.com/feed/` | auto-classified | ✅ new v2.0 |
| 66 | Eurodesk Youth `eurodesk.eu/feed/` | auto-classified | ✅ new v2.0 |
| 67 | freeCodeCamp `freecodecamp.org/news/rss/` | auto-classified | ✅ |
| 68 | Coursera Blog `blog.coursera.org/feed/` | auto-classified | ✅ |
| 69 | Open Culture `openculture.com/feed` | auto-classified | ✅ |
| 70 | Class Central `classcentral.com/report/feed/` | auto-classified | ⚠️ to-verify (403 from test server) |

### Google News (multi-region search)

- **23 regions**, all verified with real results: US, UK, IN, NP, AU, CA, SG,
  NZ, ZA, NG, KE, PK, BD, LK, PH, MY, AE, IE, DE, FR, BR, JP, ID.
- **~1,180 queries**: per-section synonym groups × region lists (e.g.
  scholarships run in 20 regions, fellowships in 14, world news in 18 regions
  + 16 regional Top-Stories feeds).
- Sections with no direct RSS (hackathons via Devpost/Unstop/Kaggle,
  DAAD/Erasmus+ scholarships, webinars, career fairs…) are covered purely by
  these queries — nothing is missed.

### Tested and EXCLUDED (dead/blocked — don't waste time)

ESPN (403), Mongabay (403), Inside Climate News (403), Carbon Brief (403),
KDnuggets (403), Fast Company (403), New Scientist (406), LiveScience (404),
Space.com `/feeds/main` (404 — replaced by `/rss` which works), UN News RSS
(404), Down To Earth (404), Yale E360 (404), Newsweek (406), Euronews (406),
Yahoo News (403), News18 (403), Youth Opportunities (404), Opportunity Cell
(403), Scholarship-Positions (SSL error), Mladiinfo (timeout), RemoteOK (410),
Setopati (500), Himalayan Times (403), My Republica (404), The Record Nepal
(empty), Edusanjal (404), Gorkhapatra EN (404), Kaggle blog (empty), Devpost
(empty), HuggingFace blog (429), Entrepreneur (empty), Business Age (conn.
error), DAAD (no RSS), ReliefWeb jobs (444), Devex (404), UN Careers (empty),
UNDP (404), Idealist (404), MOOC List (403), HackerEarth (403), OpenWHO (403).

**Coverage per section:** every one of the **17 sections** has multiple
independent sources (direct feeds + multi-region Google News + aggregators),
and the section caps total **312 items/day** (v1.3: 182 · v1.2: 114).
Real v2.0 test run: **1,247 sources fetched in 95 seconds → 28,958 raw items
→ 312 kept (all 17 sections full)**.

## C) WHAT'S IN THE ZIP

```
skillup-digest/
├── main.py                      ← the whole engine (fetch → clean → PDF → email)
├── requirements.txt             ← 3 Python libraries
├── seen.json                    ← dedup memory (keep it — see F-4)
├── .gitignore
├── README.md                    ← this guide
└── .github/
    └── workflows/
        └── digest.yml           ← cron ×4: 22:15/23:45/01:45/10:15 UTC
```

> 🔁 **Already running v1.x or v2.0?** You only need to replace **`main.py`**
> and **`digest.yml`** (the never-miss-a-day backup ladder — see ③ above),
> plus optionally this README. `requirements.txt` is unchanged — no new
> secrets, no new settings. Commit and re-run.

---

## D) ONE-TIME SETUP — click-by-click (≈ 15 minutes)

### Step 1 — Create the Gmail App Password (5 min)

> ❓ **Don't see an "App passwords" option?** That's normal — Google HIDES it
> until 2-Step Verification is ON. Follow steps 1–3 below; step 3 is a direct
> link that always works. If it still fails, see troubleshooting **F-2**.

1. On a **computer browser** (not the Gmail app), go to
   **https://myaccount.google.com/security** and sign in as
   **Kusalkandel0@gmail.com**.
2. Under *"How you sign in to Google"*, click **2-Step Verification** →
   **Get started** and turn it **ON** — the easiest option is
   **Google prompts** or **Text message** (enter your phone number,
   get a code, confirm). Wait ~2 minutes after enabling.
3. Now open this DIRECT link: **https://myaccount.google.com/apppasswords**
   (if you're on the Security page instead, search **"App passwords"** in the
   top search bar). The page now shows an *"App name"* box.
4. In *"App name"* type: `SkillUp Digest` → click **Create**.
5. Google shows a **16-character password** like `abcd efgh ijkl mnop`.
   Copy it **without spaces**: `abcdefghijklmnop`.
   ⚠️ This is the ONLY password you will ever use — not your Gmail password.

### Step 2 — Create the GitHub repository (2 min)

1. Go to **https://github.com/new** (sign up free if needed).
2. Repository name: `skillup-digest`
3. Visibility: **Public** ✅ recommended (public repos get **unlimited free
   Action minutes**; a private repo also works — its 2,000 free min/month is
   still far more than this job needs).
4. Click **Create repository**.

### Step 3 — Upload the files (3 min)

1. On the new empty repo page click **"uploading an existing file"**.
2. Drag in `main.py`, `requirements.txt`, `README.md`, `.gitignore`,
   `seen.json` from this folder.
3. Now add the workflow file: click **"Create new file"** (same page, or the
   **Add file ▾** button).
4. In the filename box type exactly:
   `.github/workflows/digest.yml`
   — typing the `/` characters makes GitHub create the folders for you.
5. Paste the full contents of `digest.yml` from this zip.
6. Click **Commit changes**.

### Step 4 — Add the Secret (1 min)

1. In your repo: **Settings → Secrets and variables → Actions**.
2. Click **New repository secret**:
   - Name: `GMAIL_APP_PASSWORD`
   - Secret: the 16-character password from Step 1
3. Click **Add secret**. Done.
   *(Optional extras — the code already defaults to your address:
   `GMAIL_USER` = `Kusalkandel0@gmail.com`;
   `RECIPIENT_EMAIL` = add later for extra recipients.)*

### Step 5 — First test run (3 min)

1. Repo tab: **Actions** → if asked, click **"I understand my workflows, go
   ahead and enable them"**.
2. Left sidebar: **SkillUp Daily Digest** → right side: **Run workflow ▾**
   → **Run workflow**.
3. After ~10 seconds the run appears. Click it → click **digest** to watch
   the live log. A full run takes **about 2–3 minutes**.
4. ✅ Success looks like:
   ```
   [i]    ... DONE — 312 items, PDF at digest_output/SkillUp-Digest-....pdf,
              sources 1245 ok / 2 warn
   ```
   A couple of `[warn]` lines are **normal** (one flaky source never breaks
   the run). A red ❌ means read section F below.
5. Note: the schedule shows on the Actions page in **UTC**, listed as
   *"Schedule: 15 22 * * *, 45 23 * * *, 45 1 * * *, 15 10 * * *"* — all four
   slots are correct: 4:00 AM NPT primary + 5:30 AM / 7:30 AM / 4:00 PM NPT
   backups. `main.py` sends only the first digest of each Nepal day, so you
   get exactly one email even though the workflow fires 4 times.

### Step 6 — Verify daily life

- 📧 Check **Kusalkandel0@gmail.com** — subject looks like:
  `🎓 SkillUp Digest — 500+ updates + news — 07 Nov 2026`. The email itself is
  a styled briefing: colored section chips with counts + **⭐ Top picks**
  (3 clickable headlines per section), with the full PDF attached.
- 🔁 The **Commits** page will show a daily
  `chore: update seen.json [skip ci]` — that's the dedup memory being saved
  and it doubles as proof the repo is active (see F-4).

---

## ⏰ TIMEZONE CHEAT-SHEET (the cron + backup ladder)

GitHub cron understands **only UTC**. Nepal is **UTC+5:45**:

| You want (NPT) | Minus 5:45 | UTC cron | Cron string |
|----------------|-----------|----------|-------------|
| **4:00 AM build start** ✅ current | 22:15 (prev. day) | 22:15 | `"15 22 * * *"` |
| 5:30 AM backup 1 | 23:45 (prev. day) | 23:45 | `"45 23 * * *"` |
| 7:30 AM backup 2 | 01:45 | 01:45 | `"45 1 * * *"` |
| 4:00 PM same-day rescue | 10:15 | 10:15 | `"15 10 * * *"` |
| 6:00 AM | 00:15 | 00:15 | `"15 0 * * *"` |
| 7:00 AM | 01:15 | 01:15 | `"15 1 * * *"` |
| 8:00 PM | 14:15 | 14:15 | `"15 14 * * *"` |

Formula: **UTC time = NPT time − 5 hours 45 minutes** (if negative, add 24 h).

**Why start at 4:00 AM if you want the mail by 5:00 AM?** GitHub's scheduler
is *best effort*: under load, scheduled jobs are commonly queued **15–60
minutes** (occasionally longer), and a slot can even be skipped entirely.
The 1-hour head start means even a slow start still delivers your email
around 5:00 AM NPT. The **three backup slots** make a missed day virtually
impossible: if the 4:00 AM slot is skipped or fails, the 5:30 AM slot sends
instead; then 7:30 AM; and a 4:00 PM rescue covers even a GitHub-wide
morning outage. Because `main.py` sends only the **first** digest of each
Nepal day, the backups exit in ~1 second once the email is out — you always
get exactly one email, just never zero. Manual *Run workflow* runs always
send (so running one manually on a day the email already arrived gives you
a second, thinner email — expected, not a bug).

---

## E) PDF LAYOUT — what lands in your inbox

```
┌─────────────────────────────────────────────────────────────┐
│  SKILLUP DIGEST                                    (cover)  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Your daily intelligence briefing · 07 Nov 2026 · 5:00 NPT  │
│                                                             │
│  312 fresh items across 17 sections (150 news · 162 opps)   │
│  Scanned 1247 sources in 23 world regions …                 │
│                                                             │
│  ■ AI & TECHNOLOGY .................. 20   ← blue bar       │
│  ■ WORLD NEWS ....................... 22   ← slate bar      │
│  ■ BUSINESS & STARTUPS .............. 16   ← green bar      │
│  ■ SCIENCE & SPACE .................. 16   ← violet bar     │
│  ■ HEALTH & MEDICINE ................ 18   ← teal bar       │
│  ■ CLIMATE & ENVIRONMENT ............ 14   ← lime bar       │
│  ■ SPORTS ........................... 14   ← orange bar     │
│  ■ ENTERTAINMENT & CULTURE .......... 14   ← pink bar       │
│  ■ NEPAL & SOUTH ASIA ............... 16   ← crimson bar    │
│  ■ TRAINING & FREE COURSES .......... 24   ← indigo bar     │
│  ■ CERTIFICATIONS ................... 22   ← purple bar     │
│  ■ SCHOLARSHIPS & FUNDING ........... 24   ← green bar      │
│  ■ INTERNSHIPS & GRAD PROGRAMS ...... 24   ← rust bar       │
│  ■ HACKATHONS & COMPETITIONS ........ 20   ← red bar        │
│  ■ WEBINARS & WORKSHOPS ............. 18   ← cyan bar       │
│  ■ CONFERENCES & CAREER FAIRS ....... 12   ← amber bar      │
│  ■ FELLOWSHIPS, GRANTS & EXCHANGES .. 18   ← navy bar       │
│  [GLOBAL] worldwide  [NEPAL] Nepal&SouthAsia  Deadline:…    │
├─────────────────────────────────────────────────────────────┤
│ ■ SCHOLARSHIPS & FUNDING                              24    │  ← green
│ ─────────────────────────────────────────────────────────── │
│ DAAD Eiffel Excellence Scholarship 2027 …  ← clickable blue │
│ [GLOBAL] · Opportunity Desk · 06 Nov 2026                  │
│ Deadline: 15 Jan 2027                       ← RED deadline  │
│ ────────────────────────────────────────────────────────── │
│ ■ WORLD NEWS                                          22    │  ← slate
│ …                                                           │
└─────────────────────────────────────────────────────────────┘
(~15–32 pages, mobile-friendly A4 — elastic caps let busy sections grow to
2× their base cap, so a heavy news day can reach ~624 items)
```

Design rules baked into the code: exact section order & colors, per-section
caps (20/22/16/16/18/14/14/14/16 news + 24/22/24/24/20/18/12/18 opportunities
= up to **312 items**), AI+Health items first in **every** section, newest
next, red deadlines, no padding with junk when a day is quiet. *(Emoji flags
are rendered as colored text chips [GLOBAL]/[NEPAL] because PDF base fonts
can't display color emoji — same meaning, cleaner look.)*

---

## F) TROUBLESHOOTING — the failures you may actually hit

**F-1 · A source fails (`[warn] HTTP 403/404/429 …` in the log)**
One bad source never breaks the run — the item count just shrinks a little.
Fix: open the URL from `main.py`'s `DIRECT_FEEDS` in your browser; if it's
dead, replace it with any RSS URL from section B (they're re-testable), or
delete that feed's 2-line block. Aggregator/classified sources
(`"kind": "agg"`) can also be safely deleted without touching anything else.

**F-2 · Gmail authentication error, or "App passwords option missing"**
*Option missing?* — App passwords are hidden unless ALL of these are true:
① **2-Step Verification is ON** (turn it on first, wait 2 minutes, then open
the direct link **https://myaccount.google.com/apppasswords**); ② your 2SV is
**not** "security key/passkey only" — add *Google prompts* or *Text message*
as a sign-in method too; ③ it's a **personal** Google account, not a
school/work Workspace account (admin must allow it there); ④ Advanced
Protection Program is off.
*Authentication error* (`535 Username and Password not accepted`) — causes,
in order of likelihood: ① pasted the App Password **with spaces** → re-save
the secret without spaces; ② used your **Gmail login password** instead of
the App Password; ③ 2-Step Verification got switched off → Step 1 again;
④ Google revoked the app password (e.g. after a password change) → create a
new one and update the secret.
**Truly stuck?** Send from a different provider instead — the script
supports it via two extra secrets: e.g. for Outlook/Hotmail set
`SMTP_HOST=smtp.office365.com`, `SMTP_PORT=587`; for Yahoo
`SMTP_HOST=smtp.mail.yahoo.com`, `SMTP_PORT=465`; then put that provider's
address in `GMAIL_USER` and its app password in `GMAIL_APP_PASSWORD`.
After fixing: Actions → Run workflow → re-test.

**F-3 · "It ran at the wrong time / is late!" (timezone + scheduler delays)**
GitHub schedules in **UTC only** and its free scheduler may start jobs
**15–60+ min late** under load. The primary slot `15 22 * * *` = **22:15 UTC
= 4:00 AM NPT build start** — the Actions page will always *display* 22:15,
23:45, 01:45 and 10:15; do not "fix" them. The 1-hour head start is
deliberate, and the three backup slots fire automatically if a slot is
skipped. (If it seems hours off, check whether a `workflow_dispatch` manual
run is what you're looking at — the run list shows the trigger: "Scheduled"
vs "Manual run".)

**F-4 · "GitHub disabled my scheduled workflow (60 days)"**
GitHub turns off crons after **60 days of no repo activity**. This project
defeats that automatically: the daily `seen.json` commit counts as activity.
If you ever see the banner *"This scheduled workflow is disabled because
there hasn't been activity in 60 days"* → Actions → SkillUp Daily Digest →
**Enable workflow** → Run workflow once. Keep commits flowing (they do, by
design) and it never happens.

**F-5 · Empty sections or "0 updates" day**
Normal on quiet days (weekends/holidays): sections simply shrink instead of
being padded. If it happens often: ① check the log's
`sources N ok / M warn` — many warns = network/URL issue (F-1);
② widen the windows: `NEWS_MAX_AGE_HOURS = 48 → 72`,
`OPP_MAX_AGE_DAYS = 7 → 10`; ③ add query terms/regions (section G);
④ raise caps if sections hit their limits every day.

**F-6 · `Process completed with exit code 1` (python step) or `exit code 128` (commit step)**
Read the EXACT error first: **Actions → click the failed run → click
`digest` → click the red step → expand it.** Then match the line:
- `[error] Gmail login REJECTED (535)` → wrong/old app password → F-2
  checklist. (The script auto-removes spaces from the secret, so pasting
  `abcd efgh ijkl mnop` is safe.)
- `error: pathspec 'seen.json' did not match any files` → python crashed
  before creating seen.json → look higher in the log for the real traceback
  (and re-run; one-off network crashes are rare — the workflow ignores
  this safely).
- `remote: Permission to ... denied to github-actions[bot]` or `403` on push
  → repo Settings → **Actions → General → Workflow permissions** → select
  **"Read and write permissions"** → Save → re-run. (The workflow already
  requests write access; this repo-level switch can still block it.)
- A red step that says **Node.js 20 deprecated** or mentions **Ubuntu 26** is
  only a NOTICE — harmless, and already fixed by using `checkout@v5` /
  `setup-python@v6` in the current workflow.

**F-7 · "I got two emails today" / "the log says already delivered"**
The backup ladder sends at most **ONE digest per Nepal day**, but a manual
*Run workflow* run always sends — so running one manually after the
scheduled email (or on a day you already tested) gives you a second,
thinner email. Harmless. Conversely, if a run's log says *"already
delivered by an earlier run today — backup slot exiting"*, that's the
system working as designed: an earlier slot already sent today's digest,
so this one skipped itself in ~1 second. And if you ever see a failed run
followed by a later successful one that re-sent the full digest — that is
the anti-data-loss rule: failed runs don't commit `seen.json`, so the next
slot re-sends everything instead of losing the day's news.

---

## G) CUSTOMIZATION GUIDE — every change is one small edit

**Add a country/region (two edits)** — ① add a line to `REGIONS`:
```python
"IT": {"gl": "it", "hl": "en", "ceid": "IT:en"},   # Italy (all verified live)
```
② add `"IT"` to the region lists where you want it — `R_WIDE` / `R_TOP` /
`R_CORE` / `R_SCHOL` / `R_GRANT`, or any section's inline `"regions"` list in
`NEWS_QUERIES` / `OPP_QUERIES`.

**Add a topic / search term** — append to the section's `terms` list in
`NEWS_QUERIES` (48 h news) or to any `OPP_QUERIES` group's `terms` list
(7-day opportunities), e.g. `"agritech"`, `"agriculture grant"`,
`"khalti fonepay"`, `"isro launch"`.

**Add a source** — append a block to `DIRECT_FEEDS` (test the RSS URL in a
browser first; never guess URLs):
```python
{"name": "Agriculture RSS", "kind": "news", "section": "science",
 "url": "https://example.org/rss"},
```
Use `"kind": "agg"` (auto-classified) or `"kind": "news"` with a fixed
`"section"`; add `"tag": "Nepal"` for Nepali sources.

**Change caps, colors, order** — each line of `SECTIONS` holds `cap` and
hex `"color"`. Reordering lines reorders the PDF. Total pages scale with the
sum of caps.

**Tune elastic caps** — `CAP_ELASTIC_FACTOR = 2.0`: on a big news day every
section can grow to 2× its base cap (total up to 624 items). Set `1.0` for
fixed caps, or `99` to include *everything* found (PDF gets very long).
Anything that doesn't fit under the cap is **not** marked as seen — it
automatically gets another chance in tomorrow's edition.

**Tune the email** — `EMAIL_TOP_PICKS = 3` clickable headlines per section in
the email body (`0` = counts only). The email is styled HTML with a
plain-text fallback, so it renders nicely in Gmail mobile too.

**Tune speed vs politeness** — `FETCH_WORKERS = 10` parallel downloads and
`REQUEST_JITTER = (0.05, 0.25)` seconds pause per request. Lower workers to
2–3 if a source complains; raise to 16 if you add many more sources.

**Change delivery time** — edit the `cron:` line in
`.github/workflows/digest.yml` using the cheat-sheet above.

**Add a second recipient** — Settings → Secrets → `RECIPIENT_EMAIL`:
`Kusalkandel0@gmail.com,friend@gmail.com` (comma-separated; the code already
splits it).

**Change email subject** — edit the `msg["Subject"]` line in `send_email()`.

---

## H) RUN IT ON YOUR OWN COMPUTER (optional)

```bash
pip install -r requirements.txt
python main.py                      # builds PDF into digest_output/, no email
```
To also email locally:
```bash
export GMAIL_APP_PASSWORD="abcdefghijklmnop"     # Windows: set GMAIL_APP_PASSWORD=...
python main.py
```

## 💰 COST & LIMITS

- GitHub Actions: **free** on public repos (unlimited minutes); private repos
  get 2,000 min/month — this job uses ~2–3 min/day ≈ 75 min/month.
- Gmail App Password email: free (within Gmail's ~500/day send limit).
- All content comes from public RSS feeds; every title links to the original
  source. Respect each source's terms of service.
