from collections import defaultdict
import re
import string
import unicodedata
import uuid
from typing import Dict, Any

# ============================================================
# SESSION / CACHE
# ============================================================

USER_ID = str(uuid.uuid4())
VERIFICATION_CACHE = {}

# ============================================================
# TRUSTED SOURCES
# ============================================================

TRUSTED_SOURCES = """
reuters.com apnews.com afp.com upi.com
bbc.com cnn.com aljazeera.com dw.com france24.com
nytimes.com theguardian.com washingtonpost.com wsj.com
economist.com politico.com axios.com
bloomberg.com financialtimes.com cnbc.com forbes.com
thehindu.com indianexpress.com hindustantimes.com ndtv.com
nature.com science.org sciencemag.org
who.int cdc.gov nih.gov
techcrunch.com theverge.com wired.com
openai.com deepmind.com ai.googleblog.com
""".split()

# ============================================================
# CATEGORY KEYWORDS
# ============================================================

CATEGORY_KEYWORDS = {
    "Politics": ["election", "government", "minister", "parliament", "policy"],
    "World": ["international", "global", "united nations", "war", "conflict"],
    "Defense": ["military", "army", "missile", "defense"],
    "Economy": ["inflation", "gdp", "economy", "recession"],
    "Business": ["company", "startup", "shares", "stock", "ceo"],
    "Technology": ["technology", "software", "internet", "ai"],
    "AI": ["artificial intelligence", "machine learning", "chatbot"]
}

PRIORITY_ORDER = [
    "Politics", "World", "Defense", "Economy",
    "Business", "Technology", "AI"
]

# ============================================================
# VALIDATION
# ============================================================

def validate_input(text: str) -> Dict[str, Any]:
    if not text.strip():
        return {"valid": False, "reason": "Empty input"}
    if len(text.split()) < 15:
        return {"valid": False, "reason": "Text too short"}
    return {"valid": True}

# ============================================================
# TEXT PREP
# ============================================================

def prepare_text_for_ai(text: str) -> Dict[str, Any]:
    lowered = unicodedata.normalize("NFKC", text).lower()
    words = lowered.translate(
        str.maketrans("", "", string.punctuation)
    ).split()
    return {"original_text": text, "words": words}

# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_news_category(text: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
    scores = defaultdict(int)

    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in clean:
                scores[category] += 1

    if not scores:
        return "General"

    max_score = max(scores.values())
    candidates = [k for k, v in scores.items() if v == max_score]

    for p in PRIORITY_ORDER:
        if p in candidates:
            return p

    return candidates[0]

# ============================================================
# MANIPULATION ANALYSIS
# ============================================================

def analyze_manipulation(prepared: Dict[str, Any]) -> Dict[str, Any]:
    words = prepared["words"]

    emotional = {"shocking", "panic", "disaster"}
    urgency = {"breaking", "urgent"}

    emotion_score = sum(w in emotional for w in words)
    urgency_score = sum(w in urgency for w in words)

    manipulation = min((emotion_score + urgency_score) / 5, 1.0)

    if manipulation >= 0.6:
        verdict = "Likely Fake"
    elif manipulation >= 0.4:
        verdict = "Suspicious"
    else:
        verdict = "Likely Real"

    return {
        "verdict": verdict,
        "manipulation_score": round(manipulation, 2),
        "verification_score": round(1.0 - manipulation, 2)
    }

# ============================================================
# EXTERNAL VERIFICATION (HEURISTIC)
# ============================================================

def external_context_check(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    found = [s for s in TRUSTED_SOURCES if s.split(".")[0] in text_lower]

    return {
        "status": "Coverage found" if found else "No confirmed coverage",
        "sources": found[:3]
    }

# ============================================================
# SUMMARY
# ============================================================

def generate_actual_summary(text: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:2])

# ============================================================
# ✅ DJANGO ENTRY POINT (ONLY FUNCTION DJANGO CALLS)
# ============================================================

def analyze_news_api(news_text: str) -> dict:

    validation = validate_input(news_text)
    if not validation["valid"]:
        return {"error": True, "reason": validation["reason"]}

    category = detect_news_category(news_text)
    prepared = prepare_text_for_ai(news_text)
    analysis = analyze_manipulation(prepared)

    if analysis["verdict"] == "Likely Fake":
        verification = {"status": "Skipped", "sources": []}
    else:
        verification = external_context_check(news_text)

    summary = generate_actual_summary(news_text)

    return {
        "error": False,
        "category": category,
        "analysis": analysis,
        "verification": verification,
        "summary": summary
    }
