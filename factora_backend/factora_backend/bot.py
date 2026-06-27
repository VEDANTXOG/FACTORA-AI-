from typing import Dict, Any, Optional
import re
import string
import unicodedata
from collections import defaultdict

# ---------------------------------------------------------------------------
# TRUSTED SOURCES
# ---------------------------------------------------------------------------
TRUSTED_SOURCES = [
    'reuters.com', 'apnews.com', 'afp.com', 'upi.com',
    'bbc.com', 'cnn.com', 'aljazeera.com', 'dw.com', 'france24.com',
    'nytimes.com', 'theguardian.com', 'washingtonpost.com', 'wsj.com',
    'economist.com', 'time.com', 'axios.com', 'politico.com',
    'bloomberg.com', 'financialtimes.com', 'cnbc.com', 'forbes.com',
    'businessinsider.com', 'marketscreener.com',
    'thehindu.com', 'indianexpress.com', 'hindustantimes.com', 'ndtv.com',
    'timesofindia.indiatimes.com', 'scroll.in', 'thewire.in',
    'news18.com', 'deccanherald.com', 'firstpost.com', 'livemint.com',
    'moneycontrol.com',
    'nature.com', 'science.org', 'sciencemag.org', 'sciencedirect.com',
    'pnas.org', 'cell.com', 'annualreviews.org',
    'sciencedaily.com', 'phys.org',
    'thelancet.com', 'nejm.org', 'bmj.com', 'jamanetwork.com',
    'who.int', 'cdc.gov', 'nih.gov', 'nhs.uk',
    'medicalnewstoday.com', 'statnews.com',
    'techcrunch.com', 'theverge.com', 'wired.com', 'arstechnica.com',
    'zdnet.com', 'technologyreview.com', 'thenextweb.com',
    'engadget.com', 'cnet.com', 'slashdot.org',
    'mit.edu', 'stanford.edu',
    'openai.com', 'deepmind.com', 'ai.googleblog.com',
    'foreignpolicy.com', 'foreignaffairs.com',
    'brookings.edu', 'csis.org', 'iiss.org',
    'carnegieendowment.org', 'chathamhouse.org',
    'cfr.org', 'un.org', 'nato.int', 'imf.org', 'worldbank.org',
    'morningstar.com', 'seekingalpha.com', 'investopedia.com',
    'sec.gov', 'nasdaq.com', 'nyse.com',
    'npr.org', 'pbs.org',
    'abc.net.au', 'cbc.ca', 'rfi.fr',
    'sverigesradio.se',
    'japantimes.co.jp', 'straitstimes.com',
    'scmp.com', 'koreaherald.com', 'channelnewsasia.com',
    'espn.com', 'espncricinfo.com', 'cricbuzz.com',
    'skysports.com', 'cbssports.com', 'nbcsports.com',
    'foxsports.com', 'theathletic.com',
    'fifa.com', 'uefa.com', 'olympics.com', 'insidethegames.biz',
    'formula1.com', 'motorsport.com',
    'atptour.com', 'wtatennis.com',
    'nba.com', 'nfl.com', 'mlb.com',
    'icc-cricket.com', 'rugbyworldcup.com',
    'newyorker.com', 'theatlantic.com',
    'propublica.org', 'theintercept.com',
    'kyodonews.net', 'en.yna.co.kr', 'lemonde.fr',
    'elpais.com', 'independent.co.uk', 'spiegel.de', 'corriere.it',
    'nhk.or.jp', 'nikkei.com', 'barrons.com', 'marketwatch.com',
    'africanews.com', 'newscientist.com', 'medscape.com', 'eurosurveillance.org',
    'spectrum.ieee.org', 'theregister.com', 'restofworld.org',
    'deepmind.google', 'anthropic.com',
    'huggingface.co', 'rand.org', 'project-syndicate.org',
    'asiasociety.org', 'ec.europa.eu', 'federalreserve.gov',
    'occrp.org', 'bellingcat.com', 'thebureauinvestigates.com',
    'fullfact.org', 'politifact.com', 'snopes.com',
]

# Precompute a set for O(1) lookup
TRUSTED_SOURCES_SET = set(TRUSTED_SOURCES)

# ---------------------------------------------------------------------------
# CATEGORY SOURCE MAP
# ---------------------------------------------------------------------------
CATEGORY_SOURCE_MAP: Dict[str, set] = {
    "Politics": {
        "reuters.com", "apnews.com", "afp.com",
        "bbc.com", "cnn.com", "aljazeera.com", "dw.com", "france24.com",
        "nytimes.com", "theguardian.com", "washingtonpost.com",
        "wsj.com", "economist.com", "politico.com", "axios.com",
        "foreignpolicy.com", "foreignaffairs.com",
        "brookings.edu", "csis.org", "cfr.org",
        "carnegieendowment.org", "chathamhouse.org", "un.org",
    },
    "World": {
        "reuters.com", "apnews.com", "afp.com",
        "bbc.com", "cnn.com", "aljazeera.com", "dw.com", "france24.com",
        "nytimes.com", "theguardian.com",
        "npr.org", "pbs.org", "cbc.ca", "abc.net.au", "rfi.fr",
        "japantimes.co.jp", "straitstimes.com", "scmp.com",
    },
    "Economy": {
        "bloomberg.com", "financialtimes.com", "cnbc.com", "wsj.com",
        "economist.com", "forbes.com", "businessinsider.com",
        "marketscreener.com", "moneycontrol.com", "livemint.com",
        "morningstar.com", "seekingalpha.com", "investopedia.com",
        "imf.org", "worldbank.org",
    },
    "Business": {
        "bloomberg.com", "financialtimes.com", "wsj.com", "forbes.com",
        "cnbc.com", "businessinsider.com", "marketscreener.com",
        "moneycontrol.com", "livemint.com",
        "sec.gov", "nasdaq.com", "nyse.com",
    },
    "Health": {
        "who.int", "cdc.gov", "nih.gov", "nhs.uk",
        "nejm.org", "thelancet.com", "bmj.com", "jamanetwork.com",
        "medicalnewstoday.com", "statnews.com",
    },
    "Science": {
        "nature.com", "science.org", "sciencemag.org",
        "cell.com", "pnas.org", "sciencedaily.com", "phys.org",
        "mit.edu", "stanford.edu",
    },
    "Technology": {
        "techcrunch.com", "theverge.com", "wired.com", "arstechnica.com",
        "zdnet.com", "technologyreview.com", "thenextweb.com",
        "engadget.com", "cnet.com", "slashdot.org",
        "mit.edu", "stanford.edu", "openai.com", "deepmind.com",
    },
    "Defense": {
        "reuters.com", "apnews.com", "bbc.com", "aljazeera.com",
        "foreignpolicy.com", "foreignaffairs.com",
        "csis.org", "iiss.org", "rand.org", "nato.int",
    },
    "Sports": {
        "espn.com", "espncricinfo.com", "cricbuzz.com",
        "bbc.com", "skysports.com", "cbssports.com", "nbcsports.com",
        "foxsports.com", "theathletic.com",
        "fifa.com", "uefa.com", "olympics.com",
        "icc-cricket.com", "rugbyworldcup.com",
        "formula1.com", "nba.com", "nfl.com", "mlb.com",
    },
}

PRIORITY_ORDER = [
    "Politics", "World", "Defense", "Economy",
    "Business", "Sports", "Technology", "AI",
]

# ---------------------------------------------------------------------------
# CATEGORY KEYWORDS
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS: Dict[str, list] = {
    "Politics": [
        "election", "minister", "government", "parliament", "policy", "president",
        "legislation", "ballot", "democrat", "republican", "senate", "congress",
        "cabinet", "bureaucracy", "opposition", "coalition", "governance", "mayor",
        "voters", "referendum", "lobbyist", "sanctions", "impeachment", "authority",
        "european union", "eu", "iran", "irgc", "revolutionary guard",
        "terrorist", "terrorism", "designation", "foreign policy",
    ],
    "World": [
        "international", "global", "nato", "un", "diplomacy", "treaty",
        "geopolitics", "bilateral", "summit", "foreign affairs", "border",
        "humanitarian", "embassy", "ambassador", "multilateral", "refugee",
        "migration", "peacekeeping", "territory", "overseas", "world bank",
    ],
    "Defense": [
        "army", "military", "missile", "defense", "weapons", "troops",
        "warfare", "pentagon", "arsenal", "navy", "air force", "infantry",
        "ballistic", "warship", "ammunition", "deployment", "intelligence",
        "espionage", "security forces", "insurgency", "counterterrorism",
        "battalion", "artillery",
    ],
    "Economy": [
        "inflation", "gdp", "recession", "budget", "fiscal", "interest rate",
        "currency", "central bank", "deficit", "taxation", "macroeconomics",
        "monetary", "deflation", "trade gap", "exports", "imports", "commodity",
        "economic growth", "austerity", "consumer price", "treasury",
    ],
    "Business": [
        "company", "ceo", "startup", "stock", "revenue", "ipo",
        "merger", "acquisition", "shares", "equity", "enterprise",
        "venture capital", "bankruptcy", "dividend", "stakeholder", "profit",
        "quarterly", "corporation", "market cap", "investment", "founder",
        "nasdaq",
    ],
    "Sports": [
        "athletics", "football", "soccer", "basketball", "tennis", "cricket",
        "nfl", "nba", "premier league", "epl", "champions league", "world cup",
        "olympics", "grand slam", "super bowl", "tournament", "championship",
        "athlete", "coach", "match", "score", "playoffs", "hat-trick",
        "knockout", "formula 1", "f1", "ufc", "boxing", "golf", "mlb", "nhl",
    ],
    "Technology": [
        "software", "internet", "platform", "cloud", "tech", "cybersecurity",
        "hardware", "encryption", "semiconductor", "bandwidth", "blockchain",
        "crypto", "database", "connectivity", "app", "mobile", "nanotechnology",
        "biotech", "gadget", "silicon", "telecom", "digital",
    ],
    "AI": [
        "artificial intelligence", "machine learning", "llm", "chatbot",
        "generative ai", "neural network", "deep learning", "nlp",
        "computer vision", "automation", "robotics", "algorithm", "gpt",
        "transformer model", "data science", "synthetic media", "inference",
        "training data", "predictive",
    ],
}

# ---------------------------------------------------------------------------
# MANIPULATION SIGNALS
# Phrases checked against the full lowercased text (not word tokens)
# so multi-word phrases work correctly.
# ---------------------------------------------------------------------------
EMOTIONAL_PHRASES = [
    "shocking", "terrifying", "panic", "miracle", "disaster",
    "horrifying", "unbelievable", "unprecedented", "never seen before",
    "historic crisis", "catastrophic", "explosive revelation",
]

URGENCY_PHRASES = [
    "breaking", "urgent", "act now", "limited time", "just happened",
    "immediate", "crisis", "emergency", "developing story",
]

AUTHORITY_PHRASES = [
    "experts say", "sources say", "officials claim",
    "studies show", "research confirms", "according to insiders",
    "anonymous officials", "unnamed sources",
]

SENSATIONAL_PHRASES = [
    "you won't believe", "shocking truth", "they don't want you to know",
    "secret revealed", "exposed", "cover-up", "mainstream media won't",
    "hidden agenda",
]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase + unicode-normalize a string."""
    return unicodedata.normalize("NFKC", text).lower()


def _count_phrases(text_lower: str, phrases: list) -> int:
    """Count how many phrases from the list appear in the text."""
    return sum(1 for p in phrases if p in text_lower)


def validate_sources_for_category(category: str, sources: list) -> list:
    """Filter a source list to only those relevant for the given category."""
    allowed = CATEGORY_SOURCE_MAP.get(category)
    if not allowed:
        return sources
    return [s for s in sources if s in allowed]


def prepare_text_for_ai(text: str) -> Dict[str, Any]:
    """Normalise text and split into clean word tokens."""
    lowered = _normalize(text)
    words = lowered.translate(str.maketrans("", "", string.punctuation)).split()
    return {
        "original_text": text,
        "normalized_text": lowered,
        "words": words,
    }


# ---------------------------------------------------------------------------
# CORE ANALYSIS FUNCTIONS
# ---------------------------------------------------------------------------

def detect_news_category(text: str) -> str:
    """
    Detect the most likely news category using keyword scoring.
    Ties are broken using PRIORITY_ORDER.
    """
    # FIX: use a proper regex — \\s was a bug (literal backslash-s)
    clean_text = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
    scores: Dict[str, int] = defaultdict(int)

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in clean_text:
                scores[category] += 1

    if not scores:
        return "General"

    max_score = max(scores.values())
    candidates = [cat for cat, score in scores.items() if score == max_score]

    for priority in PRIORITY_ORDER:
        if priority in candidates:
            return priority

    return candidates[0]


def analyze_manipulation(prepared: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score the article for manipulation signals.

    Returns verdict, scores (0.0–1.0), the strongest detected signal,
    and a list of specific reasons derived from what was actually found.
    """
    text_lower = prepared["normalized_text"]

    emotion_count = _count_phrases(text_lower, EMOTIONAL_PHRASES)
    urgency_count = _count_phrases(text_lower, URGENCY_PHRASES)
    authority_count = _count_phrases(text_lower, AUTHORITY_PHRASES)
    sensational_count = _count_phrases(text_lower, SENSATIONAL_PHRASES)

    # FIX: score is now signal-density (per 100 words) so longer articles
    # are not unfairly penalised.
    word_count = max(len(prepared["words"]), 10)
    raw_score = (
        emotion_count * 1.5
        + urgency_count * 2.0
        + sensational_count * 3.0
    ) / (word_count / 100)

    manipulation_score = min(raw_score / 10.0, 1.0)

    # Credibility rises when the article uses proper attribution language,
    # and is dragged down by unverified authority phrases.
    credibility_score = round(
        1.0 - min((authority_count * 0.15 + emotion_count * 0.1), 0.5), 2
    )

    # Verdict
    if manipulation_score >= 0.55 or sensational_count >= 2:
        verdict = "Fake"
    elif manipulation_score >= 0.30 or sensational_count == 1:
        verdict = "Suspicious"
    elif credibility_score < 0.5:
        verdict = "Suspicious"
    else:
        verdict = "Real"

    # FIX: derive the top signal from what was actually detected
    signal_map = {
        "emotion": emotion_count,
        "urgency": urgency_count,
        "sensationalism": sensational_count,
        "authority_claim": authority_count,
    }
    top_signal = max(signal_map, key=signal_map.get)  # type: ignore[arg-type]
    # If nothing was detected at all, signal is "none"
    if signal_map[top_signal] == 0:
        top_signal = "none"

    # FIX: build reasons from what was actually found, not hardcoded strings
    fake_reasons = []
    if verdict in ("Fake", "Suspicious"):
        if emotion_count > 0:
            fake_reasons.append("exaggerated or emotionally charged language detected")
        if urgency_count > 0:
            fake_reasons.append("artificial urgency phrases found")
        if sensational_count > 0:
            fake_reasons.append("sensational / clickbait language present")
        if authority_count > 0:
            fake_reasons.append("unverified authority claims (e.g. 'experts say', 'sources claim')")
        if not fake_reasons:
            fake_reasons.append("low overall credibility score")

    return {
        "verdict": verdict,
        "manipulation_score": round(manipulation_score, 2),
        "credibility_score": credibility_score,
        "top_signal": top_signal,
        "signal_counts": {
            "emotion": emotion_count,
            "urgency": urgency_count,
            "sensationalism": sensational_count,
            "authority_claim": authority_count,
        },
        "fake_reasons": fake_reasons,
    }


def external_context_check(text: str) -> Dict[str, Any]:
    """
    Check whether any trusted sources are mentioned in the article text.
    Uses proper domain matching to avoid false positives.
    """
    text_lower = _normalize(text)
    found_sources = []

    for source in TRUSTED_SOURCES:
        # FIX: extract the base domain cleanly, avoiding partial-word matches
        # e.g. "reuters" matches "reuters" not "deteriorating"
        base = source.split("/")[0]  # strip path (e.g. bbc.com/sport -> bbc.com)
        domain_name = base.rsplit(".", 1)[0]  # strip TLD  (bbc.com -> bbc)
        # Only match if it appears as a whole word boundary
        if re.search(r"\b" + re.escape(domain_name) + r"\b", text_lower):
            found_sources.append(source)

    credible_signals = sum([
        len(text.split()) > 40,
        "," in text,
        any(w in text_lower for w in ["said", "according to", "official"]),
        any(w in text_lower for w in ["government", "ministry", "authorities"]),
        len(re.findall(r"[A-Z][a-z]+", text)) > 5,  # proper nouns
    ])

    if found_sources:
        status = "Coverage found"
    elif credible_signals >= 3:
        status = "Likely real-world reporting (no source cited)"
    else:
        status = "No confirmed coverage"

    return {
        "status": status,
        "sources": found_sources[:3],
        "credible_signals": credible_signals,
    }


def generate_actual_summary(news_text: str, max_sentences: int = 2) -> str:
    """
    Extract the most informative sentences from the article.
    Strategy: prefer the first sentence (usually the lede) +
    the longest remaining sentence (usually the most detail-rich).
    """
    # FIX: correct regex — was \\s+ (literal backslash), now \s+
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", news_text.strip()) if s.strip()]

    if not sentences:
        return "Summary unavailable."

    if len(sentences) == 1:
        return sentences[0]

    # Always include the first sentence (the lede), plus the longest other one
    first = sentences[0]
    rest = sorted(sentences[1:], key=len, reverse=True)
    selected = [first] + rest[: max_sentences - 1]
    return " ".join(selected).strip()


# ---------------------------------------------------------------------------
# INPUT TYPE DETECTION
# ---------------------------------------------------------------------------

GREETING_WORDS = {"hi", "hello", "hey", "yo", "wassup", "hii", "sup", "howdy"}

# FIX: all phrases in one list with proper commas
FOUNDER_PHRASES = [
    "who is your founder",
    "who are your founders",
    "who created you",
    "who made you",
    "your founders",
    "founder",
]

FOUNDER_RESPONSE = (
    "Factora AI was built by VEDANT BABAR and YUVRAJ DESAI."
)

GREETING_RESPONSE = (
    "Hi, I am Factora AI. Paste a news article and I will analyze it for you."
)

QUESTION_RESPONSE = (
    "I am designed to analyze news articles for credibility. "
    "Please paste a full news report to get started."
)

INVALID_RESPONSE = (
    "Please enter a valid news article (at least 15 words) for analysis."
)


def detect_input_type(text: str) -> tuple[str, Optional[str]]:
    """
    Classify the input as: founder | greeting | question | invalid | news.
    Returns (input_type, response_message).
    response_message is None for 'news' type (no early exit).
    """
    cleaned = text.strip().lower()
    word_count = len(cleaned.split())

    if any(phrase in cleaned for phrase in FOUNDER_PHRASES):
        return "founder", FOUNDER_RESPONSE

    if cleaned in GREETING_WORDS or word_count <= 1:
        return "greeting", GREETING_RESPONSE

    if cleaned.endswith("?") or word_count < 5:
        return "question", QUESTION_RESPONSE

    if word_count < 15:
        return "invalid", INVALID_RESPONSE

    return "news", None


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def run_factora_analysis(text: str) -> Dict[str, Any]:
    """
    Full Factora AI analysis pipeline.

    Returns either a short-circuit response (greeting, question, etc.)
    or the full analysis result for a news article.
    """
    if not text or not text.strip():
        return {
            "type": "invalid",
            "response": INVALID_RESPONSE,
        }

    input_type, response_msg = detect_input_type(text)

    if input_type != "news":
        return {
            "type": input_type,
            "response": response_msg,
        }

    prepared = prepare_text_for_ai(text)
    manipulation = analyze_manipulation(prepared)
    verification = external_context_check(text)
    category = detect_news_category(text)
    summary = generate_actual_summary(text)

    # Validate that detected sources actually belong to the detected category
    if verification["status"] == "Coverage found" and verification.get("sources"):
        verified_sources = validate_sources_for_category(category, verification["sources"])
        if not verified_sources:
            verification["status"] = "No confirmed coverage"
        verification["sources"] = verified_sources

    # Downgrade a "Real" verdict if there is genuinely no coverage
    if (
        verification["status"] == "No confirmed coverage"
        and manipulation["verdict"] == "Real"
    ):
        manipulation["verdict"] = "Suspicious"
        manipulation["credibility_score"] = min(
            manipulation["credibility_score"], 0.45
        )
        manipulation["fake_reasons"].append(
            "no trusted source coverage confirmed"
        )

    return {
        "type": "news",
        "category": category,
        "summary": summary,
        "manipulation": manipulation,
        "verification": verification,
    }