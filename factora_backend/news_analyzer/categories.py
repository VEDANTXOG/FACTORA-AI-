"""
categories.py — Factora AI
News category detection using weighted keyword scoring and priority ordering.
Covers 15 categories including Weather, Geography, Disaster, Environment.
"""

from typing import Dict, List
from collections import defaultdict
import re
from utils import normalize

# ---------------------------------------------------------------------------
# PRIORITY ORDER (used to break scoring ties)
# Higher in list = higher priority
# ---------------------------------------------------------------------------
PRIORITY_ORDER: List[str] = [
    "Politics", "Defense", "World", "Disaster", "Weather",
    "Environment", "Economy", "Business", "Health", "Science",
    "Technology", "AI", "Sports", "Geography", "General",
]

# ---------------------------------------------------------------------------
# CATEGORY KEYWORDS
# Each keyword adds 1 point. Multi-word phrases work because we check full text.
# ---------------------------------------------------------------------------
CATEGORY_KEYWORDS: Dict[str, List[str]] = {

    "Politics": [
        "election", "minister", "government", "parliament", "policy", "president",
        "legislation", "ballot", "democrat", "republican", "senate", "congress",
        "cabinet", "bureaucracy", "opposition", "coalition", "governance", "mayor",
        "voters", "referendum", "lobbyist", "sanctions", "impeachment",
        "european union", "eu", "iran", "irgc", "revolutionary guard",
        "terrorist", "terrorism", "designation", "foreign policy",
        "ruling party", "prime minister", "chief minister", "lok sabha", "rajya sabha",
        "assembly elections", "municipal", "panchayat",
    ],

    "World": [
        "international", "global", "nato", "un", "diplomacy", "treaty",
        "geopolitics", "bilateral", "summit", "foreign affairs", "border",
        "humanitarian", "embassy", "ambassador", "multilateral", "refugee",
        "migration", "peacekeeping", "territory", "overseas", "world bank",
        "foreign minister", "foreign secretary", "state department",
    ],

    "Defense": [
        "army", "military", "missile", "defense", "weapons", "troops",
        "warfare", "pentagon", "arsenal", "navy", "air force", "infantry",
        "ballistic", "warship", "ammunition", "deployment", "intelligence",
        "espionage", "security forces", "insurgency", "counterterrorism",
        "battalion", "artillery", "airstrike", "drone strike", "ceasefire",
        "nuclear", "armed forces", "isro", "drdo",
    ],

    "Economy": [
        "inflation", "gdp", "recession", "budget", "fiscal", "interest rate",
        "currency", "central bank", "deficit", "taxation", "monetary",
        "deflation", "trade gap", "exports", "imports", "commodity",
        "economic growth", "austerity", "consumer price", "treasury",
        "rbi", "federal reserve", "repo rate", "exchange rate", "forex",
        "trade deficit", "current account", "balance of payments",
    ],

    "Business": [
        "company", "ceo", "startup", "stock", "revenue", "ipo",
        "merger", "acquisition", "shares", "equity", "enterprise",
        "venture capital", "bankruptcy", "dividend", "stakeholder", "profit",
        "quarterly", "corporation", "market cap", "investment", "founder",
        "nasdaq", "sensex", "nifty", "bse", "nse",
        "fundraise", "unicorn", "valuation", "series a", "series b",
    ],

    "Health": [
        "vaccine", "hospital", "disease", "virus", "infection", "outbreak",
        "pandemic", "epidemic", "health", "medical", "surgery", "treatment",
        "cancer", "diabetes", "heart disease", "mental health", "who",
        "cdc", "nih", "clinical trial", "drug approval", "fda", "patient",
        "mortality", "morbidity", "public health", "healthcare", "doctors",
        "quarantine", "isolation", "symptoms", "diagnosis",
    ],

    "Science": [
        "research", "study", "discovery", "experiment", "laboratory",
        "scientists", "researcher", "journal", "findings", "hypothesis",
        "physics", "chemistry", "biology", "astronomy", "space",
        "nasa", "isro", "satellite", "telescope", "genome", "dna",
        "quantum", "particle", "molecule", "microscope", "fossil",
        "evolution", "climate science", "oceanography",
    ],

    "Technology": [
        "software", "internet", "platform", "cloud", "tech", "app",
        "cybersecurity", "hardware", "encryption", "semiconductor",
        "blockchain", "crypto", "database", "connectivity", "mobile",
        "gadget", "silicon", "telecom", "digital", "startup",
        "5g", "broadband", "smartphone", "operating system",
        "hack", "data breach", "phishing", "malware",
    ],

    "AI": [
        "artificial intelligence", "machine learning", "llm", "chatbot",
        "generative ai", "neural network", "deep learning", "nlp",
        "computer vision", "automation", "robotics", "algorithm", "gpt",
        "transformer model", "data science", "synthetic media", "inference",
        "training data", "predictive", "openai", "anthropic", "deepmind",
        "large language model", "gemini", "claude", "copilot",
    ],

    "Sports": [
        "athletics", "football", "soccer", "basketball", "tennis", "cricket",
        "nfl", "nba", "premier league", "epl", "champions league", "world cup",
        "olympics", "grand slam", "super bowl", "tournament", "championship",
        "athlete", "coach", "match", "score", "playoffs", "hat-trick",
        "knockout", "formula 1", "f1", "ufc", "boxing", "golf", "mlb", "nhl",
        "test match", "ipl", "bcci", "fifa", "uefa", "icc",
    ],

    "Weather": [
        "heatwave", "heat wave", "temperature", "celsius", "fahrenheit",
        "humidity", "rainfall", "monsoon", "drought", "thunderstorm",
        "lightning", "fog", "mist", "smog", "cold wave", "snowfall",
        "blizzard", "weather forecast", "meteorological", "imd",
        "western disturbance", "cyclone warning", "rainfall deficit",
        "heat index", "wind speed", "atmospheric pressure",
        "weather alert", "yellow alert", "orange alert", "red alert",
    ],

    "Disaster": [
        "earthquake", "flood", "tsunami", "landslide", "avalanche",
        "volcano", "eruption", "wildfire", "forest fire", "hurricane",
        "typhoon", "cyclone", "tornado", "storm surge", "rescue",
        "relief operations", "ndrf", "disaster management", "casualties",
        "missing persons", "evacuation", "damage", "devastation",
        "structural collapse", "building collapse", "accident", "explosion",
        "fire brigade", "rescue teams",
    ],

    "Environment": [
        "climate change", "global warming", "carbon emissions",
        "greenhouse gas", "deforestation", "pollution", "air quality",
        "aqi", "particulate matter", "pm2.5", "plastic waste",
        "biodiversity", "endangered species", "coral reef",
        "ozone layer", "renewable energy", "solar", "wind energy",
        "sustainability", "net zero", "cop28", "paris agreement",
        "ipcc", "sea level rise", "glacier melt", "ecosystem",
    ],

    "Geography": [
        "latitude", "longitude", "topography", "terrain", "altitude",
        "peninsula", "plateau", "delta", "basin", "valley", "mountain range",
        "coastline", "island", "archipelago", "continent", "ocean",
        "river", "lake", "glacier", "desert", "tundra", "rainforest",
        "geographic survey", "census", "population density",
    ],
}


# ---------------------------------------------------------------------------
# CATEGORY BONUS SIGNALS
# Extra points given to a category based on measurable data patterns.
# Helps correctly categorize articles without explicit keyword matches.
# ---------------------------------------------------------------------------
CATEGORY_BONUS_PATTERNS: Dict[str, List[str]] = {
    "Weather": [
        r"\b\d+\s*°[CF]\b",                     # temperature readings
        r"\b\d+\s*mm\s*(?:of\s*)?rain",         # rainfall data
        r"\b\d+\s*(?:kmph|kph|mph)\b",          # wind speed
        r"\bday\s+\d+\b",                        # "second straight day"
    ],
    "Science": [
        r"\b\d+(?:\.\d+)?\s*(?:nanometer|nm|ev|kev|mev|gev)\b",
        r"\bpeer.reviewed\b",
        r"\bpublished in\b",
    ],
    "Economy": [
        r"\$\s*\d+(?:\.\d+)?\s*(?:billion|million|trillion)",
        r"₹\s*\d+(?:\.\d+)?\s*(?:crore|lakh)",
        r"\b\d+(?:\.\d+)?\s*%\s*(?:gdp|growth|inflation)\b",
    ],
    "Disaster": [
        r"\b\d+\s*(?:dead|killed|deaths|fatalities)\b",
        r"\b\d+\s*(?:injured|missing|displaced|evacuated)\b",
        r"\bmagnitude\s*\d+(?:\.\d+)?\b",       # earthquake magnitude
    ],
}


# ---------------------------------------------------------------------------
# DETECTION ENGINE
# ---------------------------------------------------------------------------

def detect_news_category(text: str) -> str:
    """
    Detect the most relevant news category for the given article.

    Algorithm:
    1. Count keyword matches per category.
    2. Add bonus points from regex patterns.
    3. Break ties using PRIORITY_ORDER.

    Returns the category name string.
    """
    clean_text = re.sub(r"[^a-zA-Z0-9\s°%$₹.,]", " ", text.lower())
    scores: Dict[str, int] = defaultdict(int)

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in clean_text:
                scores[category] += 1

    # Bonus pattern scoring
    for category, patterns in CATEGORY_BONUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, clean_text):
                scores[category] += 2  # bonus weight

    if not scores:
        return "General"

    max_score = max(scores.values())
    candidates = [cat for cat, score in scores.items() if score == max_score]

    for priority in PRIORITY_ORDER:
        if priority in candidates:
            return priority

    return candidates[0]
