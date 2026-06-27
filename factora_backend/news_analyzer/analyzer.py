"""
analyzer.py — Factora AI
Main analysis pipeline. Entry point for all external calls.

Usage (from Django views.py):
    from analyzer import run_factora_analysis
    result = run_factora_analysis(request_text)
"""

from typing import Dict, Any, Optional, List
import re
import string
import unicodedata

from utils import normalize, tokenize, get_word_count
from sources import detect_sources
from categories import detect_news_category
from scoring import analyze_manipulation

# ---------------------------------------------------------------------------
# STATIC RESPONSES
# ---------------------------------------------------------------------------

GREETING_WORDS = {
    "hi", "hello", "hey", "yo", "wassup", "hii", "sup", "howdy",
    "namaste", "salaam", "hola",
}

FOUNDER_PHRASES = [
    "who is your founder", "who are your founders",
    "who created you", "who made you", "your founders",
    "tell me about your founders", "who built you",
]

RESPONSES = {
    "founder":  "Factora AI was built by VEDANT BABAR and YUVRAJ DESAI.",
    "greeting": "Hi, I am Factora AI. Paste a news article and I will analyze it for you.",
    "question": "I am designed to analyze news articles for credibility. Please paste a full news report.",
    "too_short": "Please enter a valid news article (at least 15 words) for a proper analysis.",
    "empty":    "No text received. Please paste a news article.",
}


# ---------------------------------------------------------------------------
# TEXT PREPARATION
# ---------------------------------------------------------------------------

def prepare_text(text: str) -> Dict[str, Any]:
    """Normalize and tokenize the input text for downstream analysis."""
    normalized = normalize(text)
    words = tokenize(text)
    return {
        "original_text":   text,
        "normalized_text": normalized,
        "words":           words,
        "word_count":      len(words),
    }


# ---------------------------------------------------------------------------
# INPUT TYPE CLASSIFIER
# ---------------------------------------------------------------------------

def detect_input_type(text: str) -> tuple[str, Optional[str]]:
    """
    Classify input before running full analysis.

    Returns (input_type, early_response).
    input_type is one of: "news" | "founder" | "greeting" | "question" | "too_short" | "empty"
    early_response is None when input_type is "news" (proceed to full analysis).
    """
    if not text or not text.strip():
        return "empty", RESPONSES["empty"]

    cleaned = text.strip().lower()
    word_count = len(cleaned.split())

    if any(phrase in cleaned for phrase in FOUNDER_PHRASES):
        return "founder", RESPONSES["founder"]

    if cleaned in GREETING_WORDS or word_count <= 1:
        return "greeting", RESPONSES["greeting"]

    if cleaned.endswith("?") or word_count < 6:
        return "question", RESPONSES["question"]

    if word_count < 15:
        return "too_short", RESPONSES["too_short"]

    return "news", None


# ---------------------------------------------------------------------------
# SUMMARY ENGINE
# ---------------------------------------------------------------------------

def generate_summary(text: str, max_sentences: int = 2) -> str:
    """
    Generate a 1–2 sentence summary of the article.

    Strategy:
    - Always include the opening sentence (the journalistic lede).
    - Add the single most data-rich remaining sentence (most numbers/entities).
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if len(s.strip()) > 20]

    if not sentences:
        return "Summary unavailable."

    if len(sentences) == 1:
        return sentences[0] + ("" if sentences[0].endswith(".") else ".")

    lede = sentences[0]
    rest = sentences[1:]

    def richness(s: str) -> int:
        """Score a sentence by how much factual content it has."""
        return (
            len(re.findall(r"\b\d+(?:[.,]\d+)?", s))   # numbers
            + len(re.findall(r"[A-Z][a-z]{2,}", s))    # proper nouns
        )

    best_rest = max(rest, key=richness)

    summary = lede.rstrip(".!?") + ". " + best_rest.strip()
    if not summary.endswith((".", "!", "?")):
        summary += "."
    return summary


# ---------------------------------------------------------------------------
# EXPLANATION REPORT ENGINE
# ---------------------------------------------------------------------------

def generate_explanation(
    verdict: str,
    manipulation: Dict[str, Any],
    verification: Dict[str, Any],
    category: str,
    prepared: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a professional, human-readable explanation report.

    Returns:
        headline        : one-line verdict summary
        reasoning       : list of specific bullet-point reasons
        confidence_label: "High" | "Moderate" | "Low"
        full_report     : formatted multi-line string for display
    """
    text_lower = prepared["normalized_text"]
    signal_counts = manipulation["signal_counts"]
    confidence = manipulation["confidence"]

    reasoning: List[str] = []

    # --- Credibility positives ---
    if signal_counts.get("credible_attribution", 0) > 0:
        reasoning.append("Proper attribution language used (e.g. 'according to', 'confirmed by')")
    if signal_counts.get("numeric_data_points", 0) >= 1:
        reasoning.append(f"Contains {signal_counts['numeric_data_points']} measurable data point(s) (numbers, temperatures, percentages)")
    if signal_counts.get("proper_nouns", 0) >= 3:
        reasoning.append("Specific named entities (people, organisations, locations) present")

    # Geography detection (inline re to avoid import loop)
    if any(re.search(p, text_lower) for p in [r"\b\d+\s*°[CF]\b", r"\b(state|district|province|region)\b"]):
        reasoning.append("Geographic specificity detected — location names and/or measurements present")

    # --- Verdict-specific reasoning ---
    if verdict == "Real":
        reasoning.append("Neutral, journalistic tone — no manipulation language detected")
        if verification["status"] in ("Coverage found", "Likely real-world reporting (no source named)"):
            reasoning.append(f"Source verification: {verification['status']}")
        if category in ("Weather", "Health", "Science", "Disaster"):
            reasoning.append(f"Category '{category}' — claim type matches known real-world reporting patterns")

    elif verdict == "Suspicious":
        reasoning.append("Some credibility signals present but verification is incomplete")
        if signal_counts.get("vague_authority", 0):
            reasoning.append("Vague authority claims detected (e.g. 'experts say') without named sources")
        if verification["status"] == "No confirmed coverage":
            reasoning.append("No trusted news sources found mentioning this story")
        if manipulation["manipulation_score"] >= 0.20:
            reasoning.append(f"Moderate manipulation signal detected (score: {round(manipulation['manipulation_score'] * 100)}%)")

    elif verdict == "Fake":
        if signal_counts.get("sensationalism", 0):
            reasoning.append("Sensational / clickbait language strongly present")
        if signal_counts.get("conspiracy", 0):
            reasoning.append("Conspiracy-style wording detected")
        if signal_counts.get("fear_bait", 0):
            reasoning.append("Fear-bait phrases identified")
        if signal_counts.get("miracle_claim", 0):
            reasoning.append("Pseudoscientific or miracle claims present")
        if signal_counts.get("all_caps_abuse", 0):
            reasoning.append("ALL CAPS abuse (3+ consecutive all-caps words) — common in misinformation")
        if signal_counts.get("repeated_punct", 0):
            reasoning.append("Repeated punctuation abuse (!!!, ???) — hallmark of sensational content")
        if verification["status"] == "No confirmed coverage":
            reasoning.append("No trusted source coverage found for this claim")

    # --- Manipulation reasons (from scoring) ---
    for reason in manipulation.get("fake_reasons", []):
        if reason not in reasoning:
            reasoning.append(reason.capitalize())

    # --- Positive signals ---
    for signal in manipulation.get("positive_signals", []):
        if signal not in reasoning:
            reasoning.append(signal.capitalize())

    # --- Confidence label ---
    if confidence >= 0.70:
        confidence_label = "High"
    elif confidence >= 0.45:
        confidence_label = "Moderate"
    else:
        confidence_label = "Low"

    # --- Headline ---
    verdict_headlines = {
        "Real":       "This article appears to be REAL reporting.",
        "Suspicious": "This article has SUSPICIOUS signals — verify before sharing.",
        "Fake":       "This article shows strong indicators of being FAKE or manipulated.",
    }
    headline = verdict_headlines.get(verdict, "Analysis complete.")

    # --- Full formatted report ---
    bullets = "\n".join(f"  • {r}" for r in reasoning) if reasoning else "  • No strong signals detected."
    full_report = (
        f"VERDICT: {verdict}\n"
        f"{headline}\n\n"
        f"Reasoning:\n{bullets}\n\n"
        f"Confidence: {confidence_label} ({round(confidence * 100)}%)"
    )

    return {
        "headline": headline,
        "reasoning": reasoning,
        "confidence_label": confidence_label,
        "full_report": full_report,
    }


# ---------------------------------------------------------------------------
# SOURCE → CATEGORY VALIDATION
# ---------------------------------------------------------------------------

_CATEGORY_DOMAIN_MAP: Dict[str, set] = {
    "Politics": {
        "reuters.com", "apnews.com", "bbc.com", "cnn.com",
        "nytimes.com", "theguardian.com", "washingtonpost.com",
        "wsj.com", "politico.com", "axios.com", "thehindu.com",
        "ndtv.com", "indianexpress.com", "foreignpolicy.com",
        "brookings.edu", "cfr.org", "un.org",
    },
    "Sports": {
        "espn.com", "espncricinfo.com", "cricbuzz.com",
        "skysports.com", "bbc.com", "fifa.com",
        "icc-cricket.com", "olympics.com", "nba.com", "nfl.com",
    },
    "Science": {
        "nature.com", "science.org", "sciencemag.org", "pnas.org",
        "sciencedaily.com", "phys.org", "mit.edu", "stanford.edu",
    },
    "Health": {
        "who.int", "cdc.gov", "nih.gov", "nhs.uk",
        "thelancet.com", "nejm.org", "bmj.com",
    },
    "Technology": {
        "techcrunch.com", "theverge.com", "wired.com",
        "arstechnica.com", "technologyreview.com",
    },
    "Weather": {
        "imd.gov.in", "noaa.gov", "bbc.com", "ndtv.com",
        "thehindu.com", "hindustantimes.com",
    },
}


def _validate_sources_for_category(category: str, sources: List[str]) -> List[str]:
    """Filter out sources that don't cover the detected category."""
    allowed = _CATEGORY_DOMAIN_MAP.get(category)
    if not allowed:
        return sources
    return [s for s in sources if any(d in s.lower() for d in allowed)]


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def run_factora_analysis(text: str) -> Dict[str, Any]:
    """
    Full Factora AI analysis pipeline.

    Input  : raw news article text (or any user input string)
    Output : structured analysis result dict

    For non-news input (greetings, questions, founder queries):
        {
            "type":     "greeting" | "question" | "founder" | "too_short" | "empty",
            "response": str
        }

    For news articles:
        {
            "type":             "news",
            "category":         str,
            "summary":          str,
            "manipulation":     { verdict, manipulation_score, credibility_score,
                                  confidence, top_signal, signal_counts,
                                  fake_reasons, positive_signals },
            "verification":     { status, sources, matched_domains,
                                  credible_signal_count },
            "explanation":      { headline, reasoning, confidence_label, full_report },
        }
    """

    # ── 1. Guard: classify input type ──────────────────────────────────────
    input_type, early_response = detect_input_type(text)
    if input_type != "news":
        return {"type": input_type, "response": early_response}

    # ── 2. Prepare text ────────────────────────────────────────────────────
    prepared = prepare_text(text)

    # ── 3. Run all analysis modules in logical order ───────────────────────
    category     = detect_news_category(text)
    manipulation = analyze_manipulation(prepared)
    verification = detect_sources(text)
    summary      = generate_summary(text)

    # ── 4. Cross-validate sources vs category ──────────────────────────────
    if verification["status"] == "Coverage found" and verification.get("matched_domains"):
        validated = _validate_sources_for_category(category, verification["matched_domains"])
        if not validated and verification["matched_domains"]:
            # Sources exist but don't match category — downgrade status
            verification["status"] = "Sources found (may not cover this topic)"

    # ── 5. Adjust verdict if no coverage for otherwise-Real articles ───────
    if (
        verification["status"] == "No confirmed coverage"
        and manipulation["verdict"] == "Real"
        and manipulation["confidence"] < 0.65
    ):
        manipulation["verdict"] = "Suspicious"
        manipulation["credibility_score"] = min(manipulation["credibility_score"], 0.45)
        manipulation["fake_reasons"].append("no trusted source coverage confirmed for this claim")

    # ── 6. Build explanation report ────────────────────────────────────────
    explanation = generate_explanation(
        verdict=manipulation["verdict"],
        manipulation=manipulation,
        verification=verification,
        category=category,
        prepared=prepared,
    )

    # ── 7. Return full result ──────────────────────────────────────────────
    return {
        "type":         "news",
        "category":     category,
        "summary":      summary,
        "manipulation": manipulation,
        "verification": verification,
        "explanation":  explanation,
    }
