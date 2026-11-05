#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
#  SKILLUP DIGEST v2.0 "WORLD EDITION"  —  your personal daily newspaper
# ----------------------------------------------------------------------------
#  What it does (every day, automatically, on GitHub's free servers):
#    1. SCANS   ~60 direct RSS feeds + Google News across 23 world regions
#    2. CLEANS  keeps news from the last 48 hours, opportunities from the
#               last 7 days, removes duplicates (today AND across days)
#    3. TAGS    every item [GLOBAL] or [NEPAL], AI/Health items float on top
#    4. BUILDS  one professional PDF with 17 color-coded sections
#    5. EMAILS  it to your inbox via Gmail
#
#  v2.0 covers EVERY field: AI/tech, world, business, science, space, health,
#  climate, sports, entertainment, Nepal + courses, certifications,
#  scholarships, internships, hackathons, webinars, conferences, fellowships.
#
#  Schedule: runs at 23:15 UTC = 5:00 AM Nepal time (NPT, UTC+5:45).
#  Cost: $0. Credentials live in GitHub Secrets — never in this file.
#
#  Run locally:  python main.py        (PDF is saved to ./digest_output/
#                                       and emailed only if GMAIL_APP_PASSWORD
#                                       environment variable is set)
# ============================================================================

import os
import re
import sys
import json
import time
import html
import random
import smtplib
import hashlib
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formatdate
from urllib.parse import quote_plus, urlsplit

import requests
import feedparser
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)
from reportlab.platypus.flowables import HRFlowable

# ============================================================================
# 1. SETTINGS — everything you might ever want to change lives right here
# ============================================================================

def _env(name, default):
    """Read an env var safely. GitHub passes secrets you never created as an
    EMPTY string (not as 'unset') — an empty value must fall back to the
    default, otherwise int('') crashes and '' breaks the sender address."""
    val = os.environ.get(name, "").strip()
    return val or default

# --- Email account ----------------------------------------------------------
# GMAIL_APP_PASSWORD is a 16-character App Password — set it as a GitHub
# Secret (or export it locally). It is NEVER written in this file.
GMAIL_USER         = _env("GMAIL_USER", "Kusalkandel0@gmail.com")
# Auto-clean the app password: Google displays it WITH spaces ("abcd efgh ijkl
# mnop") and hidden newlines sneak in on paste — both break login silently.
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "") \
    .replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
RECIPIENT_EMAIL    = _env("RECIPIENT_EMAIL", GMAIL_USER)
#   ^ To add more recipients later, set the RECIPIENT_EMAIL secret to a
#     comma-separated list, e.g.  "you@gmail.com,friend@gmail.com"

# --- SMTP server (only change this if you send from a NON-Gmail provider) ----
#    Gmail default:  smtp.gmail.com  port 465 (SSL)
#    Outlook/Hotmail: SMTP_HOST=smtp.office365.com  SMTP_PORT=587
#    Yahoo:           SMTP_HOST=smtp.mail.yahoo.com SMTP_PORT=465
#    Zoho:            SMTP_HOST=smtp.zoho.com       SMTP_PORT=465
SMTP_HOST = _env("SMTP_HOST", "smtp.gmail.com")
try:
    SMTP_PORT = int(_env("SMTP_PORT", "465"))
except ValueError:
    SMTP_PORT = 465

# --- Time windows & performance ----------------------------------------------
NEWS_MAX_AGE_HOURS  = 48      # news older than this is dropped
OPP_MAX_AGE_DAYS    = 7       # opportunities older than this are dropped
ENTRIES_PER_QUERY   = 25      # how many RSS entries to read per Google query
DIRECT_FEED_ENTRIES = 60      # how many entries to read per direct RSS feed
MAX_SUMMARY_CHARS   = 220     # one-line summary length in the PDF
FETCH_WORKERS       = 10      # parallel HTTP downloads (I/O bound -> threads)
REQUEST_JITTER      = (0.05, 0.25)  # polite random pause per request (secs)
SEEN_FILE           = _env("SEEN_FILE", "seen.json")  # cross-day dedup memory
OUTPUT_DIR          = "digest_output"  # local PDF output folder
SEEN_RETENTION_DAYS = 60              # forget hashes after 60 days

HTTP_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
                   "SkillUpDigest/2.0")
}

# --- The ONE editable world-region dictionary -------------------------------
#    gl   = geolocation country code     hl = interface language
#    ceid = Google News locale id
#    All 23 regions below were LIVE-TESTED (HTTP 200 + real results).
#    Add a country by copying a line, e.g. "IT": {"gl":"it","hl":"en","ceid":"IT:en"}
REGIONS = {
    "US": {"gl": "us", "hl": "en", "ceid": "US:en"},
    "UK": {"gl": "uk", "hl": "en", "ceid": "UK:en"},
    "IN": {"gl": "in", "hl": "en", "ceid": "IN:en"},
    "NP": {"gl": "np", "hl": "en", "ceid": "NP:en"},   # Nepal
    "AU": {"gl": "au", "hl": "en", "ceid": "AU:en"},   # Australia
    "CA": {"gl": "ca", "hl": "en", "ceid": "CA:en"},   # Canada
    "SG": {"gl": "sg", "hl": "en", "ceid": "SG:en"},   # Singapore
    "NZ": {"gl": "nz", "hl": "en", "ceid": "NZ:en"},   # New Zealand
    "ZA": {"gl": "za", "hl": "en", "ceid": "ZA:en"},   # South Africa
    "NG": {"gl": "ng", "hl": "en", "ceid": "NG:en"},   # Nigeria
    "KE": {"gl": "ke", "hl": "en", "ceid": "KE:en"},   # Kenya
    "PK": {"gl": "pk", "hl": "en", "ceid": "PK:en"},   # Pakistan
    "BD": {"gl": "bd", "hl": "en", "ceid": "BD:en"},   # Bangladesh
    "LK": {"gl": "lk", "hl": "en", "ceid": "LK:en"},   # Sri Lanka
    "PH": {"gl": "ph", "hl": "en", "ceid": "PH:en"},   # Philippines
    "MY": {"gl": "my", "hl": "en", "ceid": "MY:en"},   # Malaysia
    "AE": {"gl": "ae", "hl": "en", "ceid": "AE:en"},   # UAE
    "IE": {"gl": "ie", "hl": "en", "ceid": "IE:en"},   # Ireland
    "DE": {"gl": "de", "hl": "en", "ceid": "DE:en"},   # Germany
    "FR": {"gl": "fr", "hl": "en", "ceid": "FR:en"},   # France
    "BR": {"gl": "br", "hl": "en", "ceid": "BR:en"},   # Brazil
    "JP": {"gl": "jp", "hl": "en", "ceid": "JP:en"},   # Japan
    "ID": {"gl": "id", "hl": "en", "ceid": "ID:en"},   # Indonesia
}

# Region groups (edit freely — every code must exist in REGIONS above)
R_WIDE   = ["US", "UK", "IN", "NP", "AU", "CA", "SG", "ZA", "NG", "KE",
            "AE", "PH", "NZ", "PK", "LK", "BD", "MY", "IE"]      # world news
R_TOP    = ["US", "UK", "IN", "NP", "AU", "CA", "SG", "ZA", "NG", "KE",
            "AE", "PH", "DE", "FR", "BR", "JP"]                   # top stories
R_CORE   = ["US", "UK", "IN", "NP", "AU", "CA"]                  # general news
R_SCHOL  = ["US", "UK", "IN", "NP", "CA", "AU", "DE", "SG", "ZA", "NG",
            "KE", "PK", "BD", "LK", "PH", "MY", "AE", "IE", "NZ", "JP"]  # scholarships
R_GRANT  = ["US", "UK", "IN", "NP", "CA", "AU", "DE", "KE", "NG", "ZA",
            "PH", "BD", "LK", "PK"]                               # fellowships/grants

# --- PDF sections: exact order, exact colors, exact caps --------------------
#    v2.0: 17 sections (9 news + 8 opportunities), total cap 312 items.
SECTIONS = [
    # ---------------- NEWS (last 48 h) ----------------
    {"key": "ai_tech",      "title": "AI & TECHNOLOGY",                "color": "#1D4ED8", "cap": 20},
    {"key": "world",        "title": "WORLD NEWS",                     "color": "#334155", "cap": 22},
    {"key": "business",     "title": "BUSINESS & STARTUPS",            "color": "#047857", "cap": 16},
    {"key": "science",      "title": "SCIENCE & SPACE",                "color": "#7C3AED", "cap": 16},
    {"key": "health",       "title": "HEALTH & MEDICINE",              "color": "#0F766E", "cap": 18},
    {"key": "environment",  "title": "CLIMATE & ENVIRONMENT",          "color": "#65A30D", "cap": 14},
    {"key": "sports",       "title": "SPORTS",                         "color": "#EA580C", "cap": 14},
    {"key": "entertainment","title": "ENTERTAINMENT & CULTURE",        "color": "#DB2777", "cap": 14},
    {"key": "nepal",        "title": "NEPAL & SOUTH ASIA",             "color": "#BE123C", "cap": 16},
    # ------------ OPPORTUNITIES (last 7 days) -----------
    {"key": "courses",      "title": "TRAINING & FREE COURSES",        "color": "#4338CA", "cap": 24},
    {"key": "certs",        "title": "CERTIFICATIONS",                 "color": "#7E22CE", "cap": 22},
    {"key": "scholar",      "title": "SCHOLARSHIPS & FUNDING",         "color": "#15803D", "cap": 24},
    {"key": "intern",       "title": "INTERNSHIPS & GRAD PROGRAMS",    "color": "#C2410C", "cap": 24},
    {"key": "hack",         "title": "HACKATHONS & COMPETITIONS",      "color": "#DC2626", "cap": 20},
    {"key": "events",       "title": "WEBINARS & WORKSHOPS",           "color": "#0E7490", "cap": 18},
    {"key": "conferences",  "title": "CONFERENCES & CAREER FAIRS",     "color": "#B45309", "cap": 12},
    {"key": "grants",       "title": "FELLOWSHIPS, GRANTS & EXCHANGES","color": "#1E3A8A", "cap": 18},
]
SECTION_BY_KEY = {s["key"]: s for s in SECTIONS}
NEWS_SECTION_KEYS = {"ai_tech", "world", "business", "science", "health",
                     "environment", "sports", "entertainment", "nepal"}

# --- News search terms (TYPE 1: last 48 h) -----------------------------------
#    "__top__" = Google News TOP STORIES feed for that region (no search term).
NEWS_QUERIES = {
    "ai_tech": {"regions": ["US", "UK", "IN", "NP", "AU", "CA", "SG"],
                "terms": ["artificial intelligence", "machine learning",
                          "data science", "cybersecurity", "smartphone launch",
                          "gadget review", "semiconductor chip", "robotics",
                          "virtual reality", "openai chatgpt"]},
    "world":   {"regions": R_WIDE,
                "terms": ["__top__", "world news", "breaking news",
                          "international politics", "geopolitics conflict",
                          "united nations", "global summit"]},
    "business": {"regions": ["US", "UK", "IN", "NP", "CA", "SG", "AE"],
                 "terms": ["startup funding", "venture capital", "stock market",
                           "economy inflation", "merger acquisition",
                           "new business launch", "cryptocurrency bitcoin"]},
    "science": {"regions": ["US", "UK", "IN", "AU", "CA"],
                "terms": ["space launch", "nasa isro spacex", "astronomy discovery",
                          "physics quantum", "new species discovery",
                          "research breakthrough", "ancient archaeology",
                          "mathematics discovery"]},
    "health":  {"regions": ["US", "UK", "IN", "NP", "AU", "NG"],
                "terms": ["health research", "public health", "disease outbreak",
                          "mental health", "nutrition fitness",
                          "medical breakthrough", "hospital healthcare",
                          "medicine drug"]},
    "environment": {"regions": ["US", "UK", "IN", "AU", "KE", "NP"],
                    "terms": ["climate change", "global warming",
                              "renewable energy", "extreme weather flood",
                              "wildlife conservation", "pollution air quality",
                              "sustainability"]},
    "sports":  {"regions": ["US", "UK", "IN", "NP", "AU", "CA"],
                "terms": ["football soccer", "cricket match", "olympic sports",
                          "basketball", "tennis", "formula 1 racing",
                          "sports championship"]},
    "entertainment": {"regions": ["US", "UK", "IN", "NP", "AU"],
                      "terms": ["movie release", "music release",
                                "streaming series", "celebrity entertainment",
                                "video game launch", "art culture",
                                "book literature"]},
    "nepal":   {"regions": ["NP", "IN"],
                "terms": ["Nepal", "Kathmandu", "Nepal politics", "Nepal economy",
                          "Nepal education", "Nepal technology", "Nepal sports",
                          "Nepal tourism", "Nepal health", "South Asia"]},
}

# --- Opportunity search terms (TYPE 2: last 7 days, synonym groups) ---------
OPP_QUERIES = [
    {"section": "courses", "regions": ["US", "UK", "IN", "NP", "CA", "SG", "PH", "NG"],
     "terms": ["free online course", "MOOC free", "coursera free course",
               "edX free course", "udemy free course", "google free course",
               "harvard free course", "free course certificate",
               "ai free course", "coding course free"]},
    {"section": "certs",   "regions": ["US", "UK", "IN", "NP", "CA", "AU", "SG", "PH"],
     "terms": ["free certification", "google certification", "aws certification",
               "azure certification", "cisco certification",
               "cybersecurity certification", "data science certification",
               "cloud certification"]},
    {"section": "scholar", "regions": R_SCHOL,
     "terms": ["scholarship", "fully funded scholarship",
               "undergraduate scholarship", "masters scholarship",
               "phd scholarship", "scholarship international students",
               "chevening scholarship", "fulbright", "daad scholarship",
               "commonwealth scholarship"]},
    {"section": "intern",  "regions": ["US", "UK", "IN", "NP", "CA", "AU",
                                       "SG", "PH", "AE", "NZ"],
     "terms": ["internship", "summer internship", "paid internship",
               "remote internship", "graduate program", "entry level job",
               "graduate trainee", "fresher job"]},
    {"section": "hack",    "regions": ["US", "UK", "IN", "NP", "CA", "AU", "SG", "PH"],
     "terms": ["hackathon", "online hackathon", "coding competition",
               "programming contest", "innovation challenge",
               "startup competition", "case competition", "essay competition"]},
    {"section": "events",  "regions": ["US", "UK", "IN", "NP", "CA", "AU", "SG"],
     "terms": ["free webinar", "online workshop", "virtual event",
               "masterclass free", "tech meetup", "training program free",
               "coding bootcamp free"]},
    {"section": "conferences", "regions": ["US", "UK", "IN", "NP", "AU", "SG", "AE"],
     "terms": ["tech conference", "student conference", "call for papers",
               "career fair", "education fair", "startup summit"]},
    {"section": "grants",  "regions": R_GRANT,
     "terms": ["fellowship", "research grant", "youth fellowship",
               "leadership fellowship", "un fellowship", "ngo grant",
               "innovation grant", "exchange program", "volunteer abroad"]},
]

# --- Direct RSS feeds (every URL LIVE-TESTED on 2026-11-06 unless marked) ----
#    kind: "news" = 48h window, undated entries dropped
#          "agg"  = 7d window, each entry auto-classified into a section
#    section: fixed section for the feed (agg feeds classify per entry)
#    tag:     "Nepal" forces the [NEPAL] tag, default is [GLOBAL]
DIRECT_FEEDS = [
    # ---- AI & Technology ----
    {"name": "BBC Technology",    "kind": "news", "section": "ai_tech",
     "url": "https://feeds.bbci.co.uk/news/technology/rss.xml"},
    {"name": "TechCrunch",        "kind": "news", "section": "ai_tech",
     "url": "https://techcrunch.com/feed/"},
    {"name": "The Verge",         "kind": "news", "section": "ai_tech",
     "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "MIT Tech Review (AI)", "kind": "news", "section": "ai_tech",
     "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed"},
    {"name": "Wired",             "kind": "news", "section": "ai_tech",
     "url": "https://www.wired.com/feed/rss"},
    {"name": "Ars Technica",      "kind": "news", "section": "ai_tech",
     "url": "https://feeds.arstechnica.com/arstechnica/index"},
    {"name": "IEEE Spectrum AI",  "kind": "news", "section": "ai_tech",
     "url": "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss"},
    {"name": "Hacker News",       "kind": "news", "section": "ai_tech",
     "url": "https://hnrss.org/frontpage"},
    {"name": "dev.to",            "kind": "news", "section": "ai_tech",
     "url": "https://dev.to/feed"},
    {"name": "Engadget",          "kind": "news", "section": "ai_tech",
     "url": "https://www.engadget.com/rss.xml"},
    {"name": "Tom's Hardware",    "kind": "news", "section": "ai_tech",
     "url": "https://www.tomshardware.com/feeds.xml"},
    {"name": "TechRadar",         "kind": "news", "section": "ai_tech",
     "url": "https://www.techradar.com/feeds.xml"},
    {"name": "HackerNoon",        "kind": "news", "section": "ai_tech",
     "url": "https://hackernoon.com/feed"},
    {"name": "The Next Web",      "kind": "news", "section": "ai_tech",
     "url": "https://thenextweb.com/feed"},
    # to-verify: returned 429 (rate-limit) from the test server; may work fine
    # from GitHub's servers. If it floods your logs with [warn], delete it.
    {"name": "VentureBeat AI",    "kind": "news", "section": "ai_tech",
     "url": "https://venturebeat.com/category/ai/feed/"},
    # ---- World News ----
    {"name": "BBC World",         "kind": "news", "section": "world",
     "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera",        "kind": "news", "section": "world",
     "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "Guardian World",    "kind": "news", "section": "world",
     "url": "https://www.theguardian.com/world/rss"},
    {"name": "CNN World",         "kind": "news", "section": "world",
     "url": "http://rss.cnn.com/rss/edition_world.rss"},
    {"name": "NYT World",         "kind": "news", "section": "world",
     "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"},
    {"name": "DW English",        "kind": "news", "section": "world",
     "url": "https://rss.dw.com/rdf/rss-en-world"},
    {"name": "NPR World",         "kind": "news", "section": "world",
     "url": "https://feeds.npr.org/1004/rss.xml"},
    {"name": "France24 EN",       "kind": "news", "section": "world",
     "url": "https://www.france24.com/en/rss"},
    {"name": "The Independent",   "kind": "news", "section": "world",
     "url": "https://www.independent.co.uk/rss?topic=world"},
    # ---- Business & Startups ----
    {"name": "BBC Business",      "kind": "news", "section": "business",
     "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {"name": "Guardian Business", "kind": "news", "section": "business",
     "url": "https://www.theguardian.com/uk/business/rss"},
    {"name": "CNBC Top News",     "kind": "news", "section": "business",
     "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    {"name": "Business Standard", "kind": "news", "section": "business",
     "url": "https://www.business-standard.com/rss/home_page_top_stories.rss"},
    # ---- Science & Space ----
    {"name": "ScienceDaily",      "kind": "news", "section": "science",
     "url": "https://www.sciencedaily.com/rss/all.xml"},
    {"name": "Phys.org",          "kind": "news", "section": "science",
     "url": "https://phys.org/rss-feed/"},
    {"name": "Space.com",         "kind": "news", "section": "science",
     "url": "https://www.space.com/rss"},
    {"name": "NASA",              "kind": "news", "section": "science",
     "url": "https://www.nasa.gov/news-release/feed/"},
    {"name": "Quanta Magazine",   "kind": "news", "section": "science",
     "url": "https://api.quantamagazine.org/feed/"},
    {"name": "Science Magazine",  "kind": "news", "section": "science",
     "url": "https://www.science.org/rss/news_current.xml"},
    {"name": "Nature",            "kind": "news", "section": "science",
     "url": "https://www.nature.com/nature.rss"},
    # ---- Health & Medicine ----
    {"name": "BBC Health",        "kind": "news", "section": "health",
     "url": "https://feeds.bbci.co.uk/news/health/rss.xml"},
    {"name": "STAT News",         "kind": "news", "section": "health",
     "url": "https://www.statnews.com/feed/"},
    {"name": "WHO News",          "kind": "news", "section": "health",
     "url": "https://www.who.int/rss-feeds/news-english.xml"},
    {"name": "Medical Xpress",    "kind": "news", "section": "health",
     "url": "https://medicalxpress.com/rss-feed/"},
    {"name": "NPR Health",        "kind": "news", "section": "health",
     "url": "https://feeds.npr.org/1128/rss.xml"},
    # ---- Climate & Environment ----
    {"name": "Guardian Environment", "kind": "news", "section": "environment",
     "url": "https://www.theguardian.com/environment/rss"},
    {"name": "Grist",             "kind": "news", "section": "environment",
     "url": "https://grist.org/feed/"},
    # ---- Sports ----
    {"name": "BBC Sport",         "kind": "news", "section": "sports",
     "url": "https://feeds.bbci.co.uk/sport/rss.xml"},
    {"name": "Sky Sports",        "kind": "news", "section": "sports",
     "url": "https://www.skysports.com/rss/12040"},
    {"name": "Guardian Sport",    "kind": "news", "section": "sports",
     "url": "https://www.theguardian.com/sport/rss"},
    {"name": "Times of India Sports", "kind": "news", "section": "sports",
     "url": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms"},
    # ---- Entertainment & Culture ----
    {"name": "Variety",           "kind": "news", "section": "entertainment",
     "url": "https://variety.com/feed/"},
    {"name": "Hollywood Reporter","kind": "news", "section": "entertainment",
     "url": "https://www.hollywoodreporter.com/feed/"},
    {"name": "Billboard Music",   "kind": "news", "section": "entertainment",
     "url": "https://www.billboard.com/c/music/music-news/feed/"},
    {"name": "Rolling Stone",     "kind": "news", "section": "entertainment",
     "url": "https://www.rollingstone.com/feed/"},
    {"name": "Polygon Games",     "kind": "news", "section": "entertainment",
     "url": "https://www.polygon.com/rss/index.xml"},
    {"name": "IGN Games",         "kind": "news", "section": "entertainment",
     "url": "https://feeds.ign.com/ign/games-all"},
    # ---- Nepal & South Asia ----
    {"name": "Kathmandu Post",    "kind": "news", "section": "nepal", "tag": "Nepal",
     "url": "https://kathmandupost.com/rss"},
    {"name": "OnlineKhabar English", "kind": "news", "section": "nepal", "tag": "Nepal",
     "url": "https://english.onlinekhabar.com/feed"},
    {"name": "Ratopati",          "kind": "news", "section": "nepal", "tag": "Nepal",
     "url": "https://www.ratopati.com/feed"},
    {"name": "Khabarhub English", "kind": "news", "section": "nepal", "tag": "Nepal",
     "url": "https://english.khabarhub.com/feed/"},
    {"name": "Nepali Times",      "kind": "news", "section": "nepal", "tag": "Nepal",
     "url": "https://nepalitimes.com/feed"},
    {"name": "Nepal Press",       "kind": "news", "section": "nepal", "tag": "Nepal",
     "url": "https://nepalpress.com/feed/"},
    {"name": "Himal Press",       "kind": "news", "section": "nepal", "tag": "Nepal",
     "url": "https://www.himalpress.com/feed"},
    {"name": "The Hindu National","kind": "news", "section": "nepal",
     "url": "https://www.thehindu.com/news/national/feeder/default.rss"},
    # ---- Opportunity aggregators (auto-classified per entry) ----
    {"name": "Opportunity Desk",  "kind": "agg",
     "url": "https://opportunitydesk.org/feed/"},
    {"name": "Opportunities For Africans", "kind": "agg",
     "url": "https://www.opportunitiesforafricans.com/feed/"},
    {"name": "Scholars4Dev",      "kind": "agg",
     "url": "https://www.scholars4dev.com/feed/"},
    {"name": "WeWorkRemotely",    "kind": "agg",
     "url": "https://weworkremotely.com/categories/remote-programming-jobs.rss"},
    {"name": "Internshala Blog",  "kind": "agg",
     "url": "https://blog.internshala.com/feed/"},
    {"name": "Eurodesk Youth",    "kind": "agg",
     "url": "https://eurodesk.eu/feed/"},
    # ---- Courses & certifications ----
    {"name": "freeCodeCamp",      "kind": "agg",
     "url": "https://www.freecodecamp.org/news/rss/"},
    {"name": "Coursera Blog",     "kind": "agg",
     "url": "https://blog.coursera.org/feed/"},
    {"name": "Open Culture",      "kind": "agg",
     "url": "https://www.openculture.com/feed"},
    # to-verify: returned 403 (bot-block) from the test server; often works
    # from GitHub's servers. Delete if it keeps warning.
    {"name": "Class Central",     "kind": "agg",
     "url": "https://www.classcentral.com/report/feed/"},
]

# --- Priority words: AI & Health items float to the top of EVERY section ----
AI_BOOST_WORDS     = ["artificial intelligence", "machine learning", "deep learning",
                      "data science", "data scientist", "neural network", " llm",
                      "chatgpt", "generative ai", " ai ", "openai", "gemini"]
HEALTH_BOOST_WORDS = ["health", "medical", "medicine", "disease", "vaccine",
                      "hospital", "clinic", "public health", "mental health",
                      "nursing", "epidemic", "outbreak", "patient", "cancer"]

NEPAL_HINT_WORDS   = ["nepal", "nepali", "kathmandu", "pokhara", "biratnagar"]

# --- Auto-classification rules for aggregator feeds (order matters) ---------
AGG_CLASSIFY_RULES = [
    ("hack",        ["hackathon", "coding competition", "programming contest",
                     "innovation challenge", "codefest", "datathon", "olympiad",
                     "competition", "contest", "challenge"]),
    ("conferences", ["conference", "summit", "expo", "career fair",
                     "education fair", "meetup", "forum", "symposium"]),
    ("grants",      ["fellowship", "research grant", " grant", "grants",
                     "funding", "exchange program", "volunteer", "residency",
                     "incubator", "accelerator", "ambassador"]),
    ("intern",      ["internship", "trainee", "graduate program", "graduate scheme",
                     "management trainee", "entry level", "fresher", "vacancy",
                     "remote job", "hiring", "career opportunity"]),
    ("scholar",     ["scholarship", "bursary", "fully funded", "financial aid",
                     "stipend", "tuition"]),
    ("events",      ["webinar", "workshop", "masterclass", "info session",
                     "live session", "training"]),
    ("certs",       ["certification", "certificate"]),
    ("courses",     ["free course", "online course", "mooc", "course",
                     "bootcamp", "upskill", "learn", "class"]),
]

# --- Deadline extraction patterns (rendered in red in the PDF) ---------------
DEADLINE_PATTERNS = [
    re.compile(r"deadline[:\s]*(([A-Z][a-z]+\s+\d{1,2})(?:,?\s+\d{4})?)"),
    re.compile(r"deadline[:\s]*(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})"),
    re.compile(r"(?:apply\s+by|apply\s+before|closes?\s+on|last\s+date)"
               r"[:\s]*([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})"),
]

SKIP_TITLE_PREFIXES = ("Author Correction", "Publisher Correction", "Correction",
                       "Editorial", "Matters Arising", "Amendments and Corrections")

NPT = timezone(timedelta(hours=5, minutes=45))   # Nepal Time UTC+5:45
DATE_STR = datetime.now(NPT).strftime("%d %b %Y")
PDF_PATH = os.path.join(OUTPUT_DIR, f"SkillUp-Digest-{datetime.now(NPT):%Y-%m-%d}.pdf")

STATS = {"ok": 0, "fail": 0}
STATS_LOCK = threading.Lock()


# ============================================================================
# 2. SMALL HELPERS
# ============================================================================

def log(msg, level="info"):
    """Timestamped console log. [warn] = one source failed, run continues."""
    tag = {"info": "[i]   ", "warn": "[warn]", "error": "[error]"}[level]
    print(f"{datetime.now(NPT):%H:%M:%S} {tag} {msg}", flush=True)


def clean_text(raw):
    """Strip HTML tags, unescape entities, collapse whitespace, and remove
    glyphs PDF base fonts can't render: arrows (\u25bc), box shapes, emoji
    and country flags (\U0001F1E6-\U0001F1FF render as colored blocks)."""
    if not raw:
        return ""
    txt = re.sub(r"<[^>]+>", " ", str(raw))
    txt = html.unescape(txt)
    txt = re.sub(
        r"[\u2190-\u21FF\u2460-\u24FF\u25A0-\u25FF\u2600-\u27BF\u2B00-\u2BFF"
        r"\uFE00-\uFE0F\uFEFF\U0001F000-\U0001FFFF\U000E0000-\U000E007F]",
        " ", txt)
    return re.sub(r"\s+", " ", txt).strip()


def is_junk_text(text):
    """True for garbage titles/summaries: mostly digits/punctuation, or long
    runs of one character (some feeds emit chart/placeholder junk)."""
    text = (text or "").strip()
    if len(text) < 12:
        return True if text and not text[0].isalpha() else False
    letters = sum(c.isalpha() for c in text)
    if letters < 0.5 * len(text):
        return True
    if re.search(r"(.)\1{5,}", text):
        return True
    return False


def esc(text):
    """Escape for safe use inside ReportLab Paragraph XML."""
    return html.escape(clean_text(text), quote=False)


def esc_url(url):
    """Escape a URL for use inside an href attribute."""
    return html.escape(url or "", quote=True)


def truncate(text, limit=MAX_SUMMARY_CHARS):
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0] + "…"


def parse_date(entry):
    """Extract a timezone-aware UTC datetime from an RSS entry, or None."""
    for key in ("published_parsed", "updated_parsed"):
        st = entry.get(key)
        if st:
            try:
                return datetime(*st[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return None


def norm_url(url):
    """Canonical form of a URL for dedup (drops tracking params & fragments)."""
    u = (url or "").split("#")[0]
    if "news.google.com" in u:
        return u  # Google News redirect links are unique per article
    p = urlsplit(u)
    return f"{p.scheme}://{p.netloc}{p.path}"


def title_key(title):
    """Fuzzy key so the same story from 2 sources counts once."""
    return re.sub(r"[^a-z0-9]", "", (title or "").lower())[:90]


def hash_key(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def extract_deadline(text):
    """Find 'deadline: ...' style dates in a text; returns a short string."""
    for rx in DEADLINE_PATTERNS:
        m = rx.search(text or "")
        if m:
            return m.group(1).strip()
    if "deadline" in (text or "").lower():
        return "see link"
    return ""


def text_tag(text):
    """Nepal if the text mentions Nepal, else Global."""
    low = (text or "").lower()
    return "Nepal" if any(w in low for w in NEPAL_HINT_WORDS) else "Global"


def is_boost(text):
    """True when an item is AI or Health related (sorts to the top)."""
    low = (text or "").lower()
    return any(w in low for w in AI_BOOST_WORDS) or \
           any(w in low for w in HEALTH_BOOST_WORDS)


def classify_opp(text):
    """Map an aggregator headline to the right opportunity section."""
    low = (text or "").lower()
    for section_key, words in AGG_CLASSIFY_RULES:
        if any(w in low for w in words):
            return section_key
    return None


def fetch(url):
    """GET a URL: small polite jitter, one automatic retry (429/network),
    full error isolation. Returns bytes or None. Thread-safe."""
    for attempt in (1, 2):
        try:
            time.sleep(random.uniform(*REQUEST_JITTER))
            r = requests.get(url, headers=HTTP_HEADERS, timeout=20)
            if r.status_code == 429 and attempt == 1:
                time.sleep(3)          # rate-limited -> back off once
                continue
            if r.status_code != 200:
                log(f"HTTP {r.status_code} -> {url}", "warn")
                with STATS_LOCK:
                    STATS["fail"] += 1
                return None
            with STATS_LOCK:
                STATS["ok"] += 1
            return r.content
        except Exception as exc:
            if attempt == 1:
                time.sleep(2)
                continue
            log(f"fetch failed -> {url} ({type(exc).__name__}: {exc})", "warn")
            with STATS_LOCK:
                STATS["fail"] += 1
            return None
    return None


# ============================================================================
# 3. SEEN.JSON — the digest's memory (dedups across days, keeps repo active)
# ============================================================================

def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return {"urls": data.get("urls", {}), "titles": data.get("titles", {})}
    except Exception:
        return {"urls": {}, "titles": {}}


def prune_seen(seen):
    """Drop hashes older than SEEN_RETENTION_DAYS so the file stays small."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=SEEN_RETENTION_DAYS)) \
        .strftime("%Y-%m-%d")
    for bucket in ("urls", "titles"):
        seen[bucket] = {k: d for k, d in seen[bucket].items() if d >= cutoff}


def save_seen(seen, items):
    """Record ONLY the items that made it into today's PDF, so anything that
    didn't fit under a section cap gets another chance tomorrow."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for it in items:
        seen["urls"][hash_key(norm_url(it["url"]))] = today
        seen["titles"][hash_key(title_key(it["title"]))] = today
    prune_seen(seen)
    with open(SEEN_FILE, "w", encoding="utf-8") as fh:
        json.dump(seen, fh, separators=(",", ":"), sort_keys=True)
    log(f"seen.json saved ({len(seen['urls'])} urls, {len(seen['titles'])} titles)")


# ============================================================================
# 4. COLLECTORS — Google News (23 regions) + direct RSS feeds, in parallel
# ============================================================================

def fetch_google_news(term, region_key, section, days):
    """One Google News RSS query in one world region. term '__top__' fetches
    the region's TOP STORIES feed instead of a search. Never raises."""
    reg = REGIONS[region_key]
    if term == "__top__":
        url = (f"https://news.google.com/rss?gl={reg['gl']}&hl={reg['hl']}"
               f"&ceid={reg['ceid']}")
    else:
        q = f"{term} when:{days}d"
        url = ("https://news.google.com/rss/search?q=" + quote_plus(q) +
               f"&gl={reg['gl']}&hl={reg['hl']}&ceid={reg['ceid']}")
    data = fetch(url)
    if not data:
        return []
    try:
        parsed = feedparser.parse(data)
    except Exception as exc:
        log(f"parse failed for Google News '{term}' [{region_key}]: {exc}", "warn")
        return []

    items = []
    for entry in parsed.entries[:ENTRIES_PER_QUERY]:
        title = clean_text(entry.get("title", ""))
        link = entry.get("link", "")
        if not title or not link or is_junk_text(title):
            continue
        # Google News titles end in " - Source"; the <source> tag is better.
        source = ""
        src_tag = entry.get("source")
        if isinstance(src_tag, dict):
            source = clean_text(src_tag.get("title", ""))
        if not source and " - " in title:
            title, _, source = title.rpartition(" - ")
        elif source and title.endswith(f" - {source}"):
            title = title[: -len(f" - {source}")].strip()
        tag = "Nepal" if region_key == "NP" else text_tag(title)
        deadline = "" if section in NEWS_SECTION_KEYS else extract_deadline(title)
        items.append({
            "title": title, "url": link, "source": source or "Google News",
            "date": parse_date(entry), "summary": "",   # GNews descriptions are
            "tag": tag, "section": section,             # redundant -> skip
            "boost": is_boost(title), "deadline": deadline,
        })
    return items


def fetch_direct_feed(cfg):
    """One direct RSS feed. Aggregator feeds are auto-classified per entry."""
    data = fetch(cfg["url"])
    if not data:
        return []
    try:
        parsed = feedparser.parse(data)
    except Exception as exc:
        log(f"parse failed for {cfg['name']}: {exc}", "warn")
        return []

    items = []
    for entry in parsed.entries[:DIRECT_FEED_ENTRIES]:
        title = clean_text(entry.get("title", ""))
        link = entry.get("link", "")
        if not title or not link or is_junk_text(title):
            continue
        if title.startswith(SKIP_TITLE_PREFIXES):
            continue  # skip journal noise like "Publisher Correction: ..."
        summary = truncate(clean_text(entry.get("summary", "")))
        # Hacker-News-style summaries: drop the 'Article URL: ... Comments.URL: ...' boilerplate
        summary = re.sub(r"(?:Article |Comments\.)?URL:\s*\S+", "", summary).strip(" .")
        if is_junk_text(summary):
            summary = ""   # keep the item, lose the garbage text
        kind = cfg.get("kind", "news")

        section = cfg.get("section")
        if kind == "agg":
            section = classify_opp(title + " " + summary)
            if not section:
                continue  # not an opportunity -> skip silently

        deadline = ""
        if section not in NEWS_SECTION_KEYS:
            deadline = extract_deadline(title + " " + summary)

        items.append({
            "title": title, "url": link, "source": cfg["name"],
            "date": parse_date(entry), "summary": summary,
            "tag": cfg.get("tag") or text_tag(title + " " + summary),
            "section": section, "boost": is_boost(title + " " + summary),
            "deadline": deadline,
        })
    return items


def collect_all():
    """Fetch EVERYTHING in parallel (direct feeds + Google News multi-region).
    Each source is failure-isolated: one bad URL can never crash the run."""
    sections = {s["key"]: [] for s in SECTIONS}

    tasks = []   # (kind, payload)
    for cfg in DIRECT_FEEDS:
        tasks.append(("feed", cfg))
    for section, group in NEWS_QUERIES.items():          # news: 2-day window
        for term in group["terms"]:
            for region in group["regions"]:
                tasks.append(("gnews", (term, region, section, 2)))
    for group in OPP_QUERIES:                            # opportunities: 7-day window
        for term in group["terms"]:
            for region in group["regions"]:
                tasks.append(("gnews", (term, region, group["section"], 7)))

    log(f"Fetching {len(DIRECT_FEEDS)} direct feeds + "
        f"{len(tasks) - len(DIRECT_FEEDS)} Google News queries "
        f"with {FETCH_WORKERS} parallel workers...")

    done = 0
    with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as ex:
        futures = {ex.submit(fetch_direct_feed if kind == "feed"
                             else lambda p: fetch_google_news(p[0], p[1], p[2], p[3]),
                             payload): (kind, payload)
                   for kind, payload in tasks}
        for fut in as_completed(futures):
            kind, payload = futures[fut]
            try:
                got = fut.result()
            except Exception as exc:                  # absolute safety net
                log(f"task crashed ({kind}): {type(exc).__name__}: {exc}", "warn")
                got = []
            for it in got:
                sections[it["section"]].append(it)
            done += 1
            if done % 150 == 0:
                log(f"  progress: {done}/{len(tasks)} sources fetched")

    log(f"Collection done: {STATS['ok']} sources OK, {STATS['fail']} warnings, "
        f"{sum(len(v) for v in sections.values())} raw items collected")
    return sections


# ============================================================================
# 5. PIPELINE — age filter, cross-day dedup, priority sort, section caps
# ============================================================================

def process_sections(raw_sections):
    seen = load_seen()
    url_keys = set(seen["urls"].keys())
    title_keys = set(seen["titles"].keys())

    now = datetime.now(timezone.utc)
    news_cutoff = now - timedelta(hours=NEWS_MAX_AGE_HOURS)
    opp_cutoff = now - timedelta(days=OPP_MAX_AGE_DAYS)

    final, kept_items = {}, []
    dropped_dup, dropped_old = 0, 0

    for sec in SECTIONS:
        bucket = []
        for it in raw_sections.get(sec["key"], []):
            # -- age window ----------------------------------------------
            if sec["key"] in NEWS_SECTION_KEYS:
                if it["date"] is None or it["date"] < news_cutoff:
                    dropped_old += 1
                    continue
            else:
                if it["date"] is not None and it["date"] < opp_cutoff:
                    dropped_old += 1
                    continue
            # -- dedup (across days via seen.json + within this run) ------
            uk = hash_key(norm_url(it["url"]))
            tk = hash_key(title_key(it["title"]))
            if uk in url_keys or tk in title_keys:
                dropped_dup += 1
                continue
            url_keys.add(uk)
            title_keys.add(tk)
            bucket.append(it)

        # -- sort: AI/Health first, then newest (undated last) ------------
        bucket.sort(key=lambda it: (
            0 if it["boost"] else 1,
            0 if it["date"] else 1,
            -(it["date"].timestamp() if it["date"] else 0),
        ))
        final[sec["key"]] = bucket[:sec["cap"]]          # never pad past the cap
        kept_items.extend(final[sec["key"]])

    log(f"Pipeline: {dropped_dup} duplicates removed, {dropped_old} too old, "
        f"{len(kept_items)} items kept for the PDF")
    return final, kept_items


# ============================================================================
# 6. PDF BUILDER — professional 17-section newspaper (ReportLab)
# ============================================================================

ST_COVER_TITLE = ParagraphStyle("cover_title", fontName="Helvetica-Bold",
                                fontSize=30, leading=34, textColor=HexColor("#0F172A"))
ST_COVER_SUB   = ParagraphStyle("cover_sub", fontName="Helvetica", fontSize=11.5,
                                leading=16, textColor=HexColor("#475569"))
ST_COVER_BIG   = ParagraphStyle("cover_big", fontName="Helvetica-Bold", fontSize=17,
                                leading=22, textColor=HexColor("#0F172A"))
ST_COVER_SMALL = ParagraphStyle("cover_small", fontName="Helvetica", fontSize=8.5,
                                leading=13, textColor=HexColor("#64748B"))
ST_COVER_ROW   = ParagraphStyle("cover_row", fontName="Helvetica-Bold", fontSize=9.5,
                                leading=12, textColor=HexColor("#0F172A"))
ST_COVER_CNT   = ParagraphStyle("cover_cnt", fontName="Helvetica-Bold", fontSize=9.5,
                                leading=12, alignment=TA_RIGHT,
                                textColor=HexColor("#334155"))
ST_HDR         = ParagraphStyle("hdr", fontName="Helvetica-Bold", fontSize=11.5,
                                leading=14, textColor=HexColor("#FFFFFF"))
ST_HDR_CNT     = ParagraphStyle("hdr_cnt", fontName="Helvetica-Bold", fontSize=11.5,
                                leading=14, alignment=TA_RIGHT,
                                textColor=HexColor("#FFFFFF"))
ST_ITEM_TITLE  = ParagraphStyle("item_title", fontName="Helvetica-Bold", fontSize=9.6,
                                leading=12.5, textColor=HexColor("#0F172A"))
ST_ITEM_META   = ParagraphStyle("item_meta", fontName="Helvetica", fontSize=7.4,
                                leading=9.5, textColor=HexColor("#64748B"))
ST_ITEM_SUM    = ParagraphStyle("item_sum", fontName="Helvetica", fontSize=8.2,
                                leading=10.8, textColor=HexColor("#334155"))
ST_EMPTY       = ParagraphStyle("empty", fontName="Helvetica-Oblique", fontSize=8.5,
                                leading=11, textColor=HexColor("#94A3B8"))


def _footer(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 7)
    canv.setFillColor(HexColor("#94A3B8"))
    canv.drawCentredString(A4[0] / 2.0, 8 * mm,
                           f"SkillUp Digest  ·  {DATE_STR}  ·  page {canv.getPageNumber()}")
    canv.restoreState()


def _section_header(sec, count):
    hdr = Table(
        [[Paragraph(f'<font color="white"><b>{esc(sec["title"])}</b></font>', ST_HDR),
          Paragraph(f'<font color="white"><b>{count}</b></font>', ST_HDR_CNT)]],
        colWidths=[(A4[0] - 32 * mm) - 16 * mm, 16 * mm],
    )
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), HexColor(sec["color"])),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (0, 0), 9),
        ("RIGHTPADDING",  (-1, -1), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return hdr


def _item_block(it):
    """One item = clickable blue title + tag/source/date meta + summary."""
    title_link = (f'<a href="{esc_url(it["url"])}">'
                  f'<font color="#1D4ED8"><b>{esc(it["title"])}</b></font></a>')
    tag_color = "#BE123C" if it["tag"] == "Nepal" else "#0F766E"
    date_str = it["date"].strftime("%d %b %Y") if it["date"] else "n/a"
    meta = (f'<font color="{tag_color}"><b>[{it["tag"].upper()}]</b></font>'
            f' &nbsp;·&nbsp; {esc(it["source"])} &nbsp;·&nbsp; {date_str}')
    flows = [Paragraph(title_link, ST_ITEM_TITLE),
             Paragraph(meta, ST_ITEM_META)]
    if it["summary"]:
        flows.append(Paragraph(esc(it["summary"]), ST_ITEM_SUM))
    if it["deadline"]:
        flows.append(Paragraph(
            f'<font color="#DC2626"><b>Deadline: {esc(it["deadline"])}</b></font>',
            ST_ITEM_META))
    flows.append(HRFlowable(width="100%", thickness=0.4, color=HexColor("#E2E8F0"),
                            spaceBefore=3, spaceAfter=5))
    return KeepTogether(flows)


def _cover_legend():
    return (f'<font color="#0F766E"><b>[GLOBAL]</b></font> worldwide item'
            f' &nbsp;&nbsp; <font color="#BE123C"><b>[NEPAL]</b></font> '
            f'Nepal &amp; South Asia &nbsp;&nbsp; '
            f'<font color="#DC2626"><b>Deadline:</b></font> '
            f'apply-by date found in the listing')


def build_pdf(sections):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc = SimpleDocTemplate(PDF_PATH, pagesize=A4,
                            leftMargin=16 * mm, rightMargin=16 * mm,
                            topMargin=13 * mm, bottomMargin=15 * mm,
                            title="SkillUp Digest", author="SkillUp Digest")
    total = sum(len(sections[s["key"]]) for s in SECTIONS)
    n_news = sum(len(sections[s["key"]]) for s in SECTIONS
                 if s["key"] in NEWS_SECTION_KEYS)
    n_opp = total - n_news
    story = []

    # ---------------- COVER PAGE ----------------
    story.append(Spacer(1, 20 * mm))
    story.append(Paragraph("SKILLUP DIGEST", ST_COVER_TITLE))
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width="100%", thickness=3, color=HexColor("#1D4ED8"),
                            spaceAfter=6))
    story.append(Paragraph(
        f"Your daily intelligence briefing &nbsp;·&nbsp; {DATE_STR} "
        f"&nbsp;·&nbsp; delivered 5:00 AM NPT", ST_COVER_SUB))
    story.append(Spacer(1, 9 * mm))
    story.append(Paragraph(f"{total} fresh items across {len(SECTIONS)} sections "
                           f"({n_news} news · {n_opp} opportunities)", ST_COVER_BIG))
    story.append(Spacer(1, 1.5 * mm))
    story.append(Paragraph(
        f"Scanned {STATS['ok'] + STATS['fail']} sources in 23 world regions "
        f"({STATS['ok']} OK, {STATS['fail']} warnings) &nbsp;·&nbsp; "
        f"news from the last {NEWS_MAX_AGE_HOURS} h, opportunities from the "
        f"last {OPP_MAX_AGE_DAYS} days", ST_COVER_SMALL))
    story.append(Spacer(1, 6 * mm))

    rows, style_cmds = [], []
    for i, sec in enumerate(SECTIONS):
        rows.append([Paragraph("", ST_COVER_ROW),
                     Paragraph(esc(sec["title"]), ST_COVER_ROW),
                     Paragraph(str(len(sections[sec["key"]])), ST_COVER_CNT)])
        style_cmds.append(("BACKGROUND", (0, i), (0, i), HexColor(sec["color"])))
    tbl = Table(rows, colWidths=[7 * mm, 125 * mm, 22 * mm],
                rowHeights=[7.2 * mm] * len(rows))
    tbl.setStyle(TableStyle(style_cmds + [
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("LINEBELOW",     (0, 0), (-1, -2), 0.5, HexColor("#F1F5F9")),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph(_cover_legend(), ST_COVER_SMALL))
    story.append(Spacer(1, 2.5 * mm))
    story.append(Paragraph(
        "Every title is a clickable link to the original source. AI/ML and "
        "Health items are prioritised inside every section. Generated free by "
        "SkillUp Digest on GitHub Actions.", ST_COVER_SMALL))
    story.append(PageBreak())

    # ---------------- 17 SECTIONS, EXACT ORDER ----------------
    for idx, sec in enumerate(SECTIONS):
        items = sections[sec["key"]]
        story.append(_section_header(sec, len(items)))
        story.append(Spacer(1, 3 * mm))
        if not items:
            story.append(Paragraph(
                "No new items in this section today — sources were scanned but "
                "nothing fresh passed the quality filter.", ST_EMPTY))
        else:
            for it in items:
                story.append(_item_block(it))
        if idx < len(SECTIONS) - 1:                     # no trailing spacer
            story.append(Spacer(1, 7 * mm))             # -> no blank last page

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    log(f"PDF built -> {PDF_PATH}")
    return PDF_PATH


# ============================================================================
# 7. GMAIL DELIVERY
# ============================================================================

def send_email(pdf_path, total, sections):
    """Attach the PDF and send via Gmail SMTP. Returns True/False."""
    if not GMAIL_APP_PASSWORD:
        log("GMAIL_APP_PASSWORD not set — skipping email (PDF saved locally). "
            "On GitHub Actions add the secret; see README Step 4.", "warn")
        return False
    recipients = [e.strip() for e in RECIPIENT_EMAIL.split(",") if e.strip()]
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = f"🎓 SkillUp Digest — {total} updates + news — {DATE_STR}"
    msg["Date"] = formatdate(localtime=True)

    lines = ["Hello!", "", "Here is today's SkillUp Digest.", "",
             f"{total} new items across {len(SECTIONS)} sections:"]
    for sec in SECTIONS:
        lines.append(f"  • {sec['title']}: {len(sections[sec['key']])}")
    lines += ["", "The full PDF newsletter is attached — every title is a "
              "clickable link to the original source.", "",
              f"Sources scanned: {STATS['ok']} OK, {STATS['fail']} warnings.", "",
              "— Generated by SkillUp Digest (GitHub Actions, $0/month)"]
    msg.attach(MIMEText("\n".join(lines), "plain", "utf-8"))

    with open(pdf_path, "rb") as fh:
        attachment = MIMEApplication(fh.read(), _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment",
                          filename=os.path.basename(pdf_path))
    msg.attach(attachment)

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=40) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        log(f"Email sent to {', '.join(recipients)}")
        return True
    except smtplib.SMTPAuthenticationError:
        log("Gmail login REJECTED (535). Checklist: 1) it must be the 16-char "
            "APP password (spaces are auto-removed now), not your Gmail "
            "password; 2) 2-Step Verification still ON at "
            "myaccount.google.com/security; 3) create a fresh app password at "
            "myaccount.google.com/apppasswords and update the secret.", "error")
        return False
    except Exception as exc:
        log(f"Gmail send failed: {type(exc).__name__}: {exc}", "error")
        return False


# ============================================================================
# 8. MAIN
# ============================================================================

def main():
    log("=" * 62)
    log(f"SkillUp Digest v2.0 starting — {DATE_STR} (NPT)")
    log(f"Recipient: {RECIPIENT_EMAIL} | App password set: {bool(GMAIL_APP_PASSWORD)}")
    log("=" * 62)
    try:
        raw = collect_all()
        sections, kept = process_sections(raw)
        total = len(kept)
        # Save dedup memory FIRST — even if the PDF or email step crashes,
        # tomorrow's run must never re-send today's items.
        save_seen(load_seen(), kept)
        pdf_path = build_pdf(sections)
        ok = send_email(pdf_path, total, sections)
        log(f"DONE — {total} items, PDF at {pdf_path}, "
            f"sources {STATS['ok']} ok / {STATS['fail']} warn")
        if not GMAIL_APP_PASSWORD:
            return 0          # local test mode without email — not an error
        return 0 if ok else 1
    except Exception:
        log("UNEXPECTED CRASH:\n" + traceback.format_exc(), "error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
