# 🎓 SkillUp Digest — Your Daily Opportunity Newspaper

A **100% free**, cloud-based system that scans 25+ sources across 6 world
regions every night and emails you **one professional PDF** at **5:00 AM Nepal
Time** — with AI/Tech news, Health news, Nepal news, free courses,
certifications, scholarships, internships, hackathons, and webinars.

Your computer stays OFF. GitHub's servers do all the work. **Cost: $0/month.**

---

## A) ARCHITECTURE — how it all fits together

```
              ┌──────────────────────────────────────────────────────────┐
              │            GITHUB ACTIONS CLOUD (free, 24/7)             │
              │                                                          │
 23:15 UTC ──►│  cron: "15 23 * * *"   (= 5:00 AM NPT next morning)      │
 (every day)  │        │                                                 │
              │        ▼                                                 │
              │  ┌────────────┐   19 direct RSS feeds                    │
              │  │  main.py   │──► BBC / TechCrunch / WHO / Kathmandu    │
              │  │            │    Post / Opportunity Desk / freeCodeCamp │
              │  │            │   + Google News RSS × 6 regions           │
              │  │            │    (US · UK · IN · NP · AU · CA)          │
              │  └─────┬──────┘                                           │
              │        ▼                                                  │
              │  CLEAN: news ≤ 48 h · opportunities ≤ 7 d                 │
              │  DEDUP: vs seen.json (memory across days)                 │
              │  TAG:   [GLOBAL] / [NEPAL] · AI+Health sorted to top      │
              │        ▼                                                  │
              │  PDF: cover + 9 color sections (clickable titles)         │
              │        ▼                                                  │
              │  GMAIL SMTP ──► 📧 Kusalkandel0@gmail.com                  │
              │        ▼                                                  │
              │  git commit seen.json (never re-send, keeps repo active)  │
              └──────────────────────────────────────────────────────────┘
```

## B) SOURCE COVERAGE MATRIX — what was actually tested

Every URL below was **live-tested on 2026-11-05**. Nothing is invented.

| # | Source | Feeds section | Status |
|---|--------|---------------|--------|
| 1 | Google News RSS (multi-region system: US, UK, IN, NP + AU, CA for scholarships) | all 9 sections | ✅ verified |
| 2 | BBC Technology `feeds.bbci.co.uk/news/technology/rss.xml` | AI & Tech | ✅ verified |
| 3 | TechCrunch `techcrunch.com/feed/` | AI & Tech | ✅ verified |
| 4 | The Verge `theverge.com/rss/index.xml` | AI & Tech | ✅ verified |
| 5 | MIT Tech Review AI `technologyreview.com/topic/artificial-intelligence/feed` | AI & Tech | ✅ verified |
| 6 | VentureBeat AI `venturebeat.com/category/ai/feed/` | AI & Tech | ⚠️ to-verify (429 from test server; may work on GitHub's) |
| 7 | BBC Health `feeds.bbci.co.uk/news/health/rss.xml` | Health | ✅ verified |
| 8 | STAT News `statnews.com/feed/` | Health | ✅ verified |
| 9 | Nature `nature.com/nature.rss` | Health | ✅ verified (news.rss is dead → this is the replacement) |
| 10 | WHO News `who.int/rss-feeds/news-english.xml` | Health | ✅ verified |
| 11 | Medical Xpress `medicalxpress.com/rss-feed/` | Health | ✅ verified |
| 12 | NPR Health `feeds.npr.org/1128/rss.xml` | Health | ✅ verified |
| 13 | Kathmandu Post `kathmandupost.com/rss` | Nepal | ✅ verified |
| 14 | OnlineKhabar English `english.onlinekhabar.com/feed` | Nepal | ✅ verified |
| 15 | Opportunity Desk `opportunitydesk.org/feed/` | scholarships/courses/interns (auto) | ✅ verified |
| 16 | Opportunities For Africans `opportunitiesforafricans.com/feed/` | (auto) | ✅ verified |
| 17 | Scholars4Dev `scholars4dev.com/feed/` | (auto) | ✅ verified |
| 18 | freeCodeCamp `freecodecamp.org/news/rss/` | courses/certs (auto) | ✅ verified |
| 19 | Coursera Blog `blog.coursera.org/feed/` | courses/certs (auto) | ✅ verified |
| 20 | Class Central `classcentral.com/report/feed/` | courses (auto) | ⚠️ to-verify (403 from test server) |
| 21 | Hackathons: Devpost / Unstop / Kaggle have **no public RSS** | Hackathons | ℹ️ covered via Google News queries (hackathon · coding competition · innovation challenge) in 4 regions |
| 22 | DAAD / Erasmus+ | Scholarships | ℹ️ no simple RSS → covered via Google News "fully funded scholarship" in 6 regions |

Dead feeds we tested and **excluded** (so you don't waste time): Setopati
feed (500), Himalayan Times (403), My Republica (403), Edusanjal (404), Youth
Opportunities (404), Opportunity Cell (403), Scholarship-Positions (SSL error),
OpenWHO (403, no RSS — its certificates still appear via the "OpenWHO
certificate" Google News query).

**Coverage per section:** every one of the 9 sections has **at least 3
independent sources** (direct feeds + multi-region Google News + aggregators).

## C) WHAT'S IN THE ZIP

```
skillup-digest/
├── main.py                      ← the whole engine (fetch → clean → PDF → email)
├── requirements.txt             ← 3 Python libraries
├── .gitignore
├── README.md                    ← this guide
└── .github/
    └── workflows/
        └── digest.yml           ← the daily cron (23:15 UTC = 5:00 AM NPT)
```

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
   still ~10× more than this job needs).
4. Click **Create repository**.

### Step 3 — Upload the 4 files (3 min)

1. On the new empty repo page click **"uploading an existing file"**.
2. Drag in `main.py`, `requirements.txt`, `README.md`, `.gitignore`
   from this folder.
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
   the live log. A full run takes **4–6 minutes**.
4. ✅ Success looks like:
   ```
   [i]    ... DONE — 78 items, PDF at digest_output/SkillUp-Digest-....pdf,
              sources 130 ok / 3 warn
   ```
   A couple of `[warn]` lines are **normal** (one flaky source never breaks
   the run). A red ❌ means read section F below.
5. Note: the schedule shows on the Actions page in **UTC**, listed as
   *"Schedule: 15 23 * * *"* — that is correct for 5:00 AM NPT.

### Step 6 — Verify daily life

- 📧 Check **Kusalkandel0@gmail.com** — subject looks like:
  `🎓 SkillUp Digest — 78 updates + news — 06 Nov 2026`
- 🔁 The **Commits** page will show a daily
  `chore: update seen.json [skip ci]` — that's the dedup memory being saved
  and it doubles as proof the repo is active (see F-4).

---

## ⏰ TIMEZONE CHEAT-SHEET (why the cron is `"15 23 * * *"`)

GitHub cron understands **only UTC**. Nepal is **UTC+5:45**:

| You want (NPT) | Minus 5:45 | UTC cron | Cron string |
|----------------|-----------|----------|-------------|
| **5:00 AM** ✅ current | 23:15 (prev. day) | 23:15 | `"15 23 * * *"` |
| 6:00 AM | 00:15 | 00:15 | `"15 0 * * *"` |
| 7:00 AM | 01:15 | 01:15 | `"15 1 * * *"` |
| 8:00 PM | 14:15 | 14:15 | `"15 14 * * *"` |

Formula: **UTC time = NPT time − 5 hours 45 minutes** (if negative, add 24 h).
Note: GitHub scheduled runs can start a few minutes late — that's normal and
free-tier behaviour, not a bug.

---

## E) PDF LAYOUT — what lands in your inbox

```
┌─────────────────────────────────────────────────────────────┐
│  SKILLUP DIGEST                                    (cover)  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Your daily intelligence briefing · 06 Nov 2026 · 5:00 NPT  │
│                                                             │
│  78 fresh items across 9 sections                           │
│  Scanned 133 sources (130 OK, 3 warnings) · news ≤48h …     │
│                                                             │
│  ■ AI & TECHNOLOGY .................. 10   ← blue bar       │
│  ■ HEALTH & MEDICINE ................ 10   ← teal bar       │
│  ■ NEPAL & SOUTH ASIA ............... 10   ← crimson bar    │
│  ■ TRAINING & FREE COURSES .......... 15   ← indigo bar     │
│  ■ CERTIFICATIONS ................... 15   ← purple bar     │
│  ■ SCHOLARSHIPS & FUNDING ........... 15   ← green bar      │
│  ■ INTERNSHIPS & GRAD PROGRAMS ...... 15   ← orange bar     │
│  ■ HACKATHONS & COMPETITIONS ........ 12   ← red bar        │
│  ■ WEBINARS & EVENTS ................ 12   ← dark-cyan bar  │
│  [GLOBAL] worldwide  [NEPAL] Nepal&SouthAsia  Deadline:…    │
├─────────────────────────────────────────────────────────────┤
│ ■ AI & TECHNOLOGY                                     10    │  ← blue
│ ─────────────────────────────────────────────────────────── │
│ OpenAI releases open-weight model …        ← clickable blue │
│ [GLOBAL] · TechCrunch · 06 Nov 2026                        │
│ The company said the weights will be …     ← one-line summary│
│ ────────────────────────────────────────────────────────── │
│ Nepal launches AI policy draft …                            │
│ [NEPAL] · Kathmandu Post · 06 Nov 2026     ← crimson tag    │
│ ────────────────────────────────────────────────────────── │
│ ■ HEALTH & MEDICINE                                   10    │  ← teal
│ ─────────────────────────────────────────────────────────── │
│ …                                                           │
│ 💰 …green section…  Scholarship deadline: 30 Nov 2026 ← RED │
└─────────────────────────────────────────────────────────────┘
(~12–15 pages max, mobile-friendly A4)
```

Design rules baked into the code: exact section order & colors, per-section
caps (10/10/10/15/15/15/15/12/12), AI+Health items first in **every**
section, newest next, red deadlines, no padding with junk when a day is
quiet. *(Emoji flags are rendered as colored text chips [GLOBAL]/[NEPAL]
because PDF base fonts can't display color emoji — same meaning, cleaner
look.)*

---

## F) TROUBLESHOOTING — the 5 failures you may actually hit

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

**F-3 · "It ran at the wrong time!" (timezone confusion)**
GitHub schedules in **UTC only** and may start **up to ~15 min late** on the
free tier. `15 23 * * *` = **23:15 UTC = 5:00 AM NPT** — the Actions page
will always *display* 23:15; do not "fix" it into 5:15. Use the cheat-sheet
above for any other delivery hour. (If it seems hours off, check whether a
`workflow_dispatch` manual run is what you're looking at.)

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

---

## G) CUSTOMIZATION GUIDE — every change is one small edit

**Add a country/region (one edit)** — in `REGIONS` add a line, then add its
key to `REGIONS_ALL` or `REGIONS_SCHOLAR`:
```python
"DE": {"gl": "de", "hl": "en", "ceid": "DE:en"},
```

**Add a topic / search term** — append to `NEWS_QUERIES` (48 h news) or to
any `OPP_QUERIES` group's `terms` list (7-day opportunities), e.g.
`"climate change"`, `"agritech"`, `"agriculture grant"`.

**Add a source** — append a block to `DIRECT_FEEDS` (test the RSS URL in a
browser first; never guess URLs):
```python
{"name": "Agriculture RSS", "kind": "news", "section": "health",
 "url": "https://example.org/rss"},
```
Use `"kind": "agg"` (auto-classified) or `"kind": "news"` with a fixed
`"section"`; add `"tag": "Nepal"` for Nepali sources.

**Change caps, colors, order** — each line of `SECTIONS` holds `cap` and
hex `"color"`. Reordering lines reorders the PDF.

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
  get 2,000 min/month — this job uses ~6 min/day ≈ 180 min/month.
- Gmail App Password email: free (within Gmail's ~500/day send limit).
- All content comes from public RSS feeds; every title links to the original
  source. Respect each source's terms of service.
