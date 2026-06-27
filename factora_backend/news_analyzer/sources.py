"""
sources.py — Factora AI
Trusted source registry and source detection engine.
Supports both domain matching and plain-text name matching.
"""

from typing import Dict, List
import re
from utils import normalize

# ---------------------------------------------------------------------------
# TRUSTED SOURCE REGISTRY
# Each entry: (canonical_domain, display_name, plain_text_aliases)
# ---------------------------------------------------------------------------

SOURCE_REGISTRY: List[Dict] = [
    # Wire agencies
    {"domain": "reuters.com",          "name": "Reuters",          "aliases": ["reuters"]},
    {"domain": "apnews.com",           "name": "AP News",           "aliases": ["ap news", "associated press", "apnews"]},
    {"domain": "afp.com",              "name": "AFP",               "aliases": ["afp", "agence france-presse"]},
    {"domain": "upi.com",              "name": "UPI",               "aliases": ["upi"]},

    # Global broadcasters
    {"domain": "bbc.com",              "name": "BBC",               "aliases": ["bbc", "bbc news"]},
    {"domain": "cnn.com",              "name": "CNN",               "aliases": ["cnn"]},
    {"domain": "aljazeera.com",        "name": "Al Jazeera",        "aliases": ["al jazeera", "aljazeera"]},
    {"domain": "dw.com",               "name": "DW",                "aliases": ["deutsche welle", "dw news"]},
    {"domain": "france24.com",         "name": "France 24",         "aliases": ["france 24", "france24"]},
    {"domain": "abc.net.au",           "name": "ABC Australia",     "aliases": ["abc australia"]},
    {"domain": "cbc.ca",               "name": "CBC",               "aliases": ["cbc", "cbc news"]},
    {"domain": "rfi.fr",               "name": "RFI",               "aliases": ["rfi", "radio france internationale"]},
    {"domain": "npr.org",              "name": "NPR",               "aliases": ["npr", "national public radio"]},
    {"domain": "pbs.org",              "name": "PBS",               "aliases": ["pbs"]},
    {"domain": "nhk.or.jp",            "name": "NHK",               "aliases": ["nhk"]},

    # Major newspapers
    {"domain": "nytimes.com",          "name": "New York Times",    "aliases": ["new york times", "nytimes", "nyt"]},
    {"domain": "theguardian.com",      "name": "The Guardian",      "aliases": ["the guardian", "guardian"]},
    {"domain": "washingtonpost.com",   "name": "Washington Post",   "aliases": ["washington post", "wapo"]},
    {"domain": "wsj.com",              "name": "Wall Street Journal","aliases": ["wall street journal", "wsj"]},
    {"domain": "economist.com",        "name": "The Economist",     "aliases": ["the economist", "economist"]},
    {"domain": "time.com",             "name": "TIME",              "aliases": ["time magazine"]},
    {"domain": "axios.com",            "name": "Axios",             "aliases": ["axios"]},
    {"domain": "politico.com",         "name": "Politico",          "aliases": ["politico"]},
    {"domain": "bloomberg.com",        "name": "Bloomberg",         "aliases": ["bloomberg"]},
    {"domain": "financialtimes.com",   "name": "Financial Times",   "aliases": ["financial times", "ft"]},
    {"domain": "cnbc.com",             "name": "CNBC",              "aliases": ["cnbc"]},
    {"domain": "forbes.com",           "name": "Forbes",            "aliases": ["forbes"]},
    {"domain": "businessinsider.com",  "name": "Business Insider",  "aliases": ["business insider"]},
    {"domain": "independent.co.uk",    "name": "The Independent",   "aliases": ["the independent", "independent"]},
    {"domain": "newyorker.com",        "name": "New Yorker",        "aliases": ["new yorker"]},
    {"domain": "theatlantic.com",      "name": "The Atlantic",      "aliases": ["the atlantic", "atlantic"]},

    # Indian sources
    {"domain": "thehindu.com",         "name": "The Hindu",         "aliases": ["the hindu", "thehindu"]},
    {"domain": "indianexpress.com",    "name": "Indian Express",    "aliases": ["indian express", "ie"]},
    {"domain": "hindustantimes.com",   "name": "Hindustan Times",   "aliases": ["hindustan times", "ht"]},
    {"domain": "ndtv.com",             "name": "NDTV",              "aliases": ["ndtv"]},
    {"domain": "timesofindia.indiatimes.com", "name": "Times of India", "aliases": ["times of india", "toi"]},
    {"domain": "scroll.in",            "name": "Scroll",            "aliases": ["scroll.in", "scroll"]},
    {"domain": "thewire.in",           "name": "The Wire",          "aliases": ["the wire"]},
    {"domain": "news18.com",           "name": "News18",            "aliases": ["news18"]},
    {"domain": "deccanherald.com",     "name": "Deccan Herald",     "aliases": ["deccan herald"]},
    {"domain": "firstpost.com",        "name": "Firstpost",         "aliases": ["firstpost"]},
    {"domain": "livemint.com",         "name": "Livemint",          "aliases": ["livemint", "mint"]},
    {"domain": "moneycontrol.com",     "name": "Moneycontrol",      "aliases": ["moneycontrol"]},
    {"domain": "theprint.in",          "name": "The Print",         "aliases": ["the print", "theprint"]},
    {"domain": "wionews.com",          "name": "WION",              "aliases": ["wion"]},
    {"domain": "zeenews.india.com",    "name": "Zee News",          "aliases": ["zee news"]},
    {"domain": "aninews.in",           "name": "ANI",               "aliases": ["ani", "asian news international"]},
    {"domain": "pti.in",               "name": "PTI",               "aliases": ["pti", "press trust of india"]},

    # Science / Health
    {"domain": "nature.com",           "name": "Nature",            "aliases": ["nature journal", "nature"]},
    {"domain": "science.org",          "name": "Science",           "aliases": ["science journal"]},
    {"domain": "thelancet.com",        "name": "The Lancet",        "aliases": ["the lancet", "lancet"]},
    {"domain": "nejm.org",             "name": "NEJM",              "aliases": ["new england journal", "nejm"]},
    {"domain": "bmj.com",              "name": "BMJ",               "aliases": ["bmj", "british medical journal"]},
    {"domain": "who.int",              "name": "WHO",               "aliases": ["who", "world health organization"]},
    {"domain": "cdc.gov",              "name": "CDC",               "aliases": ["cdc", "centers for disease control"]},
    {"domain": "nih.gov",              "name": "NIH",               "aliases": ["nih", "national institutes of health"]},
    {"domain": "nhs.uk",               "name": "NHS",               "aliases": ["nhs"]},

    # Technology / AI
    {"domain": "techcrunch.com",       "name": "TechCrunch",        "aliases": ["techcrunch"]},
    {"domain": "theverge.com",         "name": "The Verge",         "aliases": ["the verge", "verge"]},
    {"domain": "wired.com",            "name": "Wired",             "aliases": ["wired"]},
    {"domain": "arstechnica.com",      "name": "Ars Technica",      "aliases": ["ars technica"]},
    {"domain": "technologyreview.com", "name": "MIT Tech Review",   "aliases": ["mit technology review", "tech review"]},
    {"domain": "openai.com",           "name": "OpenAI",            "aliases": ["openai"]},
    {"domain": "anthropic.com",        "name": "Anthropic",         "aliases": ["anthropic"]},
    {"domain": "deepmind.google",      "name": "DeepMind",          "aliases": ["deepmind", "google deepmind"]},

    # Policy / Think tanks / Intl orgs
    {"domain": "foreignpolicy.com",    "name": "Foreign Policy",    "aliases": ["foreign policy"]},
    {"domain": "brookings.edu",        "name": "Brookings",         "aliases": ["brookings institution", "brookings"]},
    {"domain": "rand.org",             "name": "RAND",              "aliases": ["rand corporation", "rand"]},
    {"domain": "un.org",               "name": "United Nations",    "aliases": ["united nations", "un"]},
    {"domain": "imf.org",              "name": "IMF",               "aliases": ["imf", "international monetary fund"]},
    {"domain": "worldbank.org",        "name": "World Bank",        "aliases": ["world bank"]},
    {"domain": "nato.int",             "name": "NATO",              "aliases": ["nato"]},
    {"domain": "imd.gov.in",           "name": "IMD",               "aliases": ["imd", "india meteorological department", "met department", "weather department"]},
    {"domain": "noaa.gov",             "name": "NOAA",              "aliases": ["noaa", "national weather service"]},

    # Sports
    {"domain": "espn.com",             "name": "ESPN",              "aliases": ["espn"]},
    {"domain": "espncricinfo.com",     "name": "ESPNcricinfo",      "aliases": ["espncricinfo", "cricinfo"]},
    {"domain": "cricbuzz.com",         "name": "Cricbuzz",          "aliases": ["cricbuzz"]},
    {"domain": "fifa.com",             "name": "FIFA",              "aliases": ["fifa"]},
    {"domain": "olympics.com",         "name": "Olympics",          "aliases": ["olympics", "ioc"]},
    {"domain": "icc-cricket.com",      "name": "ICC",               "aliases": ["icc", "international cricket council"]},

    # Fact-checkers
    {"domain": "fullfact.org",         "name": "Full Fact",         "aliases": ["full fact", "fullfact"]},
    {"domain": "politifact.com",       "name": "PolitiFact",        "aliases": ["politifact"]},
    {"domain": "snopes.com",           "name": "Snopes",            "aliases": ["snopes"]},
    {"domain": "factcheck.org",        "name": "FactCheck.org",     "aliases": ["factcheck"]},
    {"domain": "boomlive.in",          "name": "BoomLive",          "aliases": ["boom live", "boomlive"]},
    {"domain": "altnews.in",           "name": "AltNews",           "aliases": ["altnews", "alt news"]},

    # Investigative
    {"domain": "propublica.org",       "name": "ProPublica",        "aliases": ["propublica"]},
    {"domain": "occrp.org",            "name": "OCCRP",             "aliases": ["occrp"]},
    {"domain": "bellingcat.com",       "name": "Bellingcat",        "aliases": ["bellingcat"]},
]

# Flat domain set for O(1) lookup
TRUSTED_DOMAINS: set = {s["domain"] for s in SOURCE_REGISTRY}

# Build alias → display_name map for fast name-based lookup
_ALIAS_MAP: Dict[str, str] = {}
for _entry in SOURCE_REGISTRY:
    for _alias in _entry["aliases"]:
        _ALIAS_MAP[_alias] = _entry["name"]


# ---------------------------------------------------------------------------
# SOURCE DETECTION ENGINE
# ---------------------------------------------------------------------------

def detect_sources(text: str) -> Dict:
    """
    Detect trusted sources mentioned in the article.

    Strategy (in order):
    1. URL/domain match — most reliable
    2. Plain-text alias match using word boundaries — catches "Reuters", "BBC", etc.

    Returns:
        status  : "Coverage found" | "Likely real reporting" | "No confirmed coverage"
        sources : list of display names found (deduplicated, max 5)
        matched_domains : raw domains found (for internal use)
    """
    text_lower = normalize(text)
    found_names: list = []
    found_domains: list = []

    # --- Pass 1: domain / URL matching ---
    for entry in SOURCE_REGISTRY:
        domain = entry["domain"]
        base = domain.split("/")[0]           # strip path suffix
        domain_core = base.rsplit(".", 1)[0]  # strip TLD
        if re.search(r"\b" + re.escape(domain_core) + r"\b", text_lower):
            if entry["name"] not in found_names:
                found_names.append(entry["name"])
                found_domains.append(domain)

    # --- Pass 2: plain-text alias matching ---
    for alias, display_name in _ALIAS_MAP.items():
        if display_name in found_names:
            continue  # already found via domain
        if re.search(r"\b" + re.escape(alias) + r"\b", text_lower):
            found_names.append(display_name)

    # --- Credibility heuristics (for articles with no named source) ---
    credible_signals = sum([
        get_word_count(text) > 40,
        "," in text,
        any(w in text_lower for w in ["said", "according to", "official", "confirmed"]),
        any(w in text_lower for w in ["government", "ministry", "authorities", "department"]),
        len(re.findall(r"[A-Z][a-z]{2,}", text)) > 5,  # proper nouns
        bool(re.search(r"\b\d+\s*°[CF]\b", text)),     # temperature data
        bool(re.search(r"\b\d{4}\b", text)),            # year references
    ])

    if found_names:
        status = "Coverage found"
    elif credible_signals >= 4:
        status = "Likely real-world reporting (no source named)"
    elif credible_signals >= 2:
        status = "Partial credibility signals detected"
    else:
        status = "No confirmed coverage"

    return {
        "status": status,
        "sources": found_names[:5],
        "matched_domains": found_domains[:5],
        "credible_signal_count": credible_signals,
    }


def get_word_count(text: str) -> int:
    return len(text.split())
