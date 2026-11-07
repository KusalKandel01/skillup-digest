# 🗞️ SkillUp Digest — Your Automated Daily Newspaper

> **One email every morning. Every field. Every corner of the world. $0/month.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/Powered_by-GitHub_Actions-2088FF?logo=githubactions&logoColor=white)
![Cost](https://img.shields.io/badge/cost-%240%2Fmonth-success)
![Output](https://img.shields.io/badge/output-HTML_%2B_PDF-red)

**SkillUp Digest** is a fully automated news pipeline that lives entirely in
GitHub's free cloud. It wakes up on its own schedule, scans **1,200+ sources
across 23 world regions**, and delivers **one professional PDF briefing** to
your inbox — covering technology, world events, business, science, space,
health, climate, sports, culture, plus daily-hunted opportunities
(scholarships, internships, hackathons, courses, certifications,
conferences, fellowships and grants).

No computer left on. No server to rent. No button to press. **It just
arrives, every single day.**

- 🤖 **Fully automatic** — 4 scheduled runs per night with a self-healing
  backup ladder and a one-email-per-day guard
- 🌍 **Every field** — 9 news sections + 8 opportunity sections (17 total)
- 🧠 **Smart** — 10 parallel fetchers finish ~1,180 searches in ~2 minutes;
  duplicate stories are remembered and never re-sent
- 📎 **Beautiful output** — styled HTML briefing with clickable headlines,
  plus a cover-page PDF with red deadline alerts
- 🔒 **Private by design** — all credentials live in GitHub Secrets; nothing
  personal is stored anywhere in this repository

---

## 📬 What lands in your inbox

**1. A styled email briefing** — colored section chips with item counts and
**⭐ Top picks** (three clickable headlines per section), with a plain-text
fallback that renders well on mobile.

**2. A print-quality PDF** — cover page with a section legend, then every
story with title, source, age, summary, and deadlines highlighted in red.

### The 17 daily sections

| # | News (last 48 h) | Cap* | # | Opportunities (last 7 days) | Cap* |
|---|------------------|------|---|------------------------------|------|
| 1 | AI & Technology | 20 | 10 | Training & Free Courses | 24 |
| 2 | World News | 22 | 11 | Certifications | 22 |
| 3 | Business & Startups | 16 | 12 | Scholarships & Funding | 24 |
| 4 | Science & Space | 16 | 13 | Internships & Grad Programs | 24 |
| 5 | Health & Medicine | 18 | 14 | Hackathons & Competitions | 20 |
| 6 | Climate & Environment | 14 | 15 | Webinars & Workshops | 18 |
| 7 | Sports | 14 | 16 | Conferences & Career Fairs | 12 |
| 8 | Entertainment & Culture | 14 | 17 | Fellowships, Grants & Exchanges | 18 |
| 9 | Nepal & South Asia | 16 | | | |

\* Caps are **elastic**: on heavy news days a section can grow to **2× its
base size**, and quiet days shrink automatically. Overflow items are *not*
discarded — they get another chance tomorrow. Typical delivery: **300–600
items per day**.

---

## ⏰ How it runs itself — fully automatic

The workflow fires **four times every Nepal day**. The first run that
actually delivers sends the digest; every later run sees *"already delivered
today"* and exits in ~1 second:

| UTC | Nepal (NPT) | Role |
|-----|-------------|------|
| 20:45 | 2:30 AM | 🥇 **Primary** — you read at 5:00 AM, so we start early; email lands ~2:30–4:00 AM |
| 22:45 | 4:30 AM | 🥈 Backup 1 — if the primary slot was skipped |
| 00:30 | 6:15 AM | 🥉 Backup 2 — if both earlier slots failed |
| 10:15 | 4:00 PM | 🆘 Same-day rescue — covers even a GitHub-wide morning outage |

> The Actions page shows this as
> `Schedule: 45 20 * * *, 45 22 * * *, 30 0 * * *, 15 10 * * *` — all four
> lines are intentional. GitHub cron understands **UTC only**.
>
> **Every email shows exactly when it was generated** — in the subject line
> (`… — 07 Nov 2026, 02:31 AM NPT`), in the blue header of the HTML body,
> and on the PDF cover. So you always know the last-update time of what
> you are reading.

**Built-in reliability rules** (no configuration needed):

- **Exactly one email per Nepal day** — a delivery stamp inside `seen.json`
  makes duplicate sends impossible.
- **A failed run never loses the day's news** — the dedup memory is only
  committed when a run *succeeds*, so the next backup slot re-sends the full
  digest instead of skipping stories.
- **Manual *Run workflow* always sends** — perfect for testing on demand.
- **Never gets disabled** — the daily `seen.json` commit counts as repository
  activity, defeating GitHub's 60-day auto-disable rule.
- **GitHub's scheduler is "best effort"** (slots can start 15–60+ min late,
  rarely are skipped) — that is exactly why there are four chances every day.

---

## 🏗️ How it works

```
              ┌──────────────────────────────────────────────────────────┐
              │            GITHUB ACTIONS CLOUD (free, 24/7)             │
              │                                                          │
 cron ×4 ────►│  2:30 AM NPT (+ backups) → main.py                       │
 (every day)  │        │                                                 │
              │        ▼                                                 │
              │  ┌────────────┐   70 direct RSS feeds                    │
              │  │  main.py   │──► BBC / TechCrunch / Al Jazeera / NASA  │
              │  │            │    + Google News RSS × 23 regions         │
              │  │            │    (US UK IN NP AU CA SG NZ ZA NG KE PK   │
              │  │            │     BD LK PH MY AE IE DE FR BR JP ID)     │
              │  └─────┬──────┘                                           │
              │        ▼                                                  │
              │  clean → dedup (seen.json) → elastic caps → build PDF     │
              │        │                          (ReportLab, ~2 min)     │
              │        ▼                                                  │
              │  📧 styled email + PDF attachment → your inbox            │
              │        ▼                                                  │
              │  commit seen.json  (dedup memory + keeps repo active)     │
              └──────────────────────────────────────────────────────────┘
```

**Sources:** 70 hand-verified RSS feeds (BBC, TechCrunch, Al Jazeera, NASA,
Nature, Space.com, Kathmandu Post, …) plus ~1,180 Google News queries
across 23 regions, fetched by **10 parallel workers** with polite jitter and
429-retry handling. Stories are deduplicated by URL **and** title-hash, with
a 60-day memory.

---

## 🚀 Setup (one time, ≈ 15 minutes)

### 1 · Create the repository
Create a new GitHub repository (public or private — both work) and upload:
`main.py`, `requirements.txt`, `.gitignore`, `seen.json` and
`.github/workflows/digest.yml`.

### 2 · Get a Gmail App Password
1. Turn on **2-Step Verification** for the Gmail account you want to send from.
2. Go to **myaccount.google.com/apppasswords** and create an app password.
3. Copy the **16-character** password (spaces are fine — the code cleans them).

### 3 · Add the secrets
Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value | Required |
|--------|-------|----------|
| `GMAIL_USER` | `your-email@gmail.com` (the sender account) | ✅ |
| `GMAIL_APP_PASSWORD` | the 16-char app password | ✅ |
| `RECIPIENT_EMAIL` | where the digest goes — comma-separate for several readers | optional¹ |
| `SMTP_HOST` / `SMTP_PORT` | only for non-Gmail senders (e.g. `smtp.mail.yahoo.com` / `465`) | optional |

¹ Defaults to `GMAIL_USER`.

> 🔒 **Nothing personal lives in this repository** — if a secret is missing,
> the run still completes and saves the PDF locally instead of crashing.

### 4 · Allow the daily commit
Repo → **Settings → Actions → General → Workflow permissions** → select
**"Read and write permissions"** → Save. (Needed so the bot can commit
`seen.json` back — that is the dedup memory.)

### 5 · First run
**Actions → SkillUp Daily Digest → Run workflow** → wait for the green ✓ →
check your inbox for
`🎓 SkillUp Digest — N updates + news — <date, time> NPT`.

From the next morning onward: **nothing to do, ever.** The schedule, backups,
dedup and commits are all automatic.

---

## ⚙️ Customize

**Change delivery time** — edit the `cron:` lines in
`.github/workflows/digest.yml`. Formula: **UTC = Nepal time − 5:45**
(if negative, add 24 h).

| You want (NPT) | UTC cron | Cron string |
|----------------|----------|-------------|
| 2:30 AM ✅ current | 20:45 (prev. day) | `"45 20 * * *"` |
| 4:00 AM | 22:15 (prev. day) | `"15 22 * * *"` |
| 6:00 AM | 00:15 | `"15 0 * * *"` |
| 7:00 AM | 01:15 | `"15 1 * * *"` |
| 8:00 PM | 14:15 | `"15 14 * * *"` |

**Add a country** — one line in `REGIONS` in `main.py`:
```python
"IT": {"gl": "it", "hl": "en", "ceid": "IT:en"},   # Italy
```
then add `"IT"` to the region lists (`R_WIDE`, `R_TOP`, `R_CORE`,
`R_SCHOL`, `R_GRANT`).

**Add a topic** — append a term to any section's `terms` list in
`NEWS_QUERIES` (news) or `OPP_QUERIES` (opportunities), e.g. `"agritech"`,
`"robotics grant"`.

**Tune volume** — section caps live in `SECTIONS` (elastic factor:
`CAP_ELASTIC_FACTOR = 2.0`); fetch parallelism: `FETCH_WORKERS = 10`;
news window: `NEWS_MAX_AGE_HOURS = 48`; opportunities window:
`OPP_MAX_AGE_DAYS = 7`.

---

## 🔧 Troubleshooting

| Symptom | Cause → Fix |
|---------|-------------|
| `[error] Gmail login REJECTED (535)` | Wrong/old app password → create a fresh one at myaccount.google.com/apppasswords and update the `GMAIL_APP_PASSWORD` secret. (Spaces in the secret are cleaned automatically.) |
| `Permission to ... denied to github-actions[bot]` / exit 128 | Settings → Actions → General → Workflow permissions → **Read and write** → re-run. |
| Empty sections or "0 updates" | Quiet day — sections shrink instead of padding. Persistent? Widen `NEWS_MAX_AGE_HOURS` → 72, `OPP_MAX_AGE_DAYS` → 10, or add topics/regions. |
| "This scheduled workflow is disabled (60 days)" | Repository inactive 60 days → Actions → **Enable workflow** → Run workflow once. The daily commits normally prevent this. |
| Email arrives late | GitHub's free scheduler is best-effort (15–60+ min queues). The 4-slot ladder already covers this — the email arrives the same morning, guaranteed. |
| Two emails in one day | A manual *Run workflow* always sends — running it on a day the digest already arrived gives a second, thinner email. Expected, not a bug. |
| Log says "already delivered … exiting" | The system working: an earlier slot sent today's digest, so this scheduled run skipped itself in ~1 second. |
| Red *Node.js 20 deprecated* notice | Harmless notice only — already mitigated with `checkout@v5` / `setup-python@v6`. |

A couple of `[warn]` lines in the log are normal — one flaky source never
breaks the run.

---

## 📁 Project layout

```
skillup-digest/
├── main.py                      ← the whole pipeline (fetch → PDF → email)
├── requirements.txt             ← feedparser, requests, reportlab
├── seen.json                    ← dedup memory (auto-committed daily)
├── .gitignore
├── README.md
└── .github/
    └── workflows/
        └── digest.yml           ← the 4-slot automatic schedule
```

---

## 🔒 Privacy

- All credentials live in **GitHub Secrets** — never in code, never in logs.
- `seen.json` stores **anonymous hashes only** (no titles, no URLs, no emails).
- No personal information is embedded anywhere in this repository.

## 🧾 Changelog

- **v2.1** — Never-miss-a-day system: 4-slot backup ladder, one-email-per-day
  guard, commit-only-on-success anti-data-loss rule. Elastic section caps
  (up to 2×). Beautiful HTML email with clickable top picks.
- **v2.0 "World Edition"** — 17 sections, 70 verified sources, 23 Google News
  regions, ~1,180 queries, 10 parallel workers (full run ≈ 2 minutes).
- **v1.3** — First stable single-schedule release.

---

<div align="center">

**Built with Python, ReportLab and GitHub Actions — zero infrastructure.**

</div>
