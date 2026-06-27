"""
scoring.py — Factora AI
Manipulation detection, credibility scoring, and verdict engine.
All scores are guaranteed to be in [0.0, 1.0].
"""

from typing import Dict, Any, List
import re
from utils import (
    normalize, tokenize, count_phrases, count_numbers,
    count_proper_nouns, has_all_caps_abuse,
    count_repeated_punctuation, has_geographic_signals, clamp,
)

# ---------------------------------------------------------------------------
# SIGNAL LEXICONS
# All phrases are checked against the full lowercased text (not word tokens)
# so multi-word phrases work correctly.
# ---------------------------------------------------------------------------

EMOTIONAL_PHRASES: List[str] = [
    "shocking", "terrifying", "panic", "miracle", "disaster",
    "horrifying", "unbelievable", "unprecedented", "never seen before",
    "historic crisis", "catastrophic", "explosive revelation",
    "heartbreaking", "outrageous", "jaw-dropping", "spine-chilling",
    "devastating blow", "total collapse",
]

URGENCY_PHRASES: List[str] = [
    "breaking", "urgent", "act now", "limited time", "just happened",
    "immediate", "crisis", "emergency", "developing story",
    "happening now", "live update", "last minute", "final warning",
]

SENSATIONAL_PHRASES: List[str] = [
    "you won't believe", "shocking truth", "they don't want you to know",
    "secret revealed", "exposed", "cover-up", "mainstream media won't",
    "hidden agenda", "what they're hiding", "the truth about",
    "wake up", "share before deleted", "banned information",
    "doctors don't want you to know", "suppressed", "whistleblower reveals",
]

AUTHORITY_VAGUE_PHRASES: List[str] = [
    "experts say", "sources say", "officials claim", "studies show",
    "research confirms", "according to insiders", "anonymous officials",
    "unnamed sources", "insiders reveal", "high-level sources",
    "top officials say", "government sources confirm",
]

CREDIBLE_PHRASES: List[str] = [
    "according to", "confirmed by", "reported by", "announced",
    "stated", "official statement", "press release", "spokesperson",
    "data shows", "figures indicate", "survey found", "published in",
    "told reporters", "in a statement", "verified", "on record",
]

CONSPIRACY_PHRASES: List[str] = [
    "new world order", "deep state", "globalist", "plandemic",
    "microchip", "5g causes", "flat earth", "crisis actor",
    "false flag", "illuminati", "population control", "mind control",
    "chemtrails", "they are hiding", "shadow government",
]

FEAR_BAIT_PHRASES: List[str] = [
    "you are in danger", "your life at risk", "danger alert",
    "this will destroy", "collapse is coming", "end times",
    "world war 3", "mass extinction", "economic collapse imminent",
    "catastrophic failure", "total shutdown",
]

MIRACLE_PHRASES: List[str] = [
    "miracle cure", "doctors hate", "instant results",
    "guaranteed", "100% effective", "this one trick",
    "ancient secret", "big pharma doesn't want", "natural cure",
    "permanent fix", "eliminates completely",
]

FACTUAL_SIGNAL_WORDS: List[str] = [
    "said", "according to", "official", "confirmed", "stated",
    "announced", "released", "published", "reported", "found",
    "government", "ministry", "authorities", "department",
    "university", "institute", "study", "data",
]


# ---------------------------------------------------------------------------
# SCORING ENGINE
# ---------------------------------------------------------------------------

def analyze_manipulation(prepared: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive manipulation analysis.

    Returns:
        verdict             : "Real" | "Suspicious" | "Fake"
        manipulation_score  : float [0.0 – 1.0]
        credibility_score   : float [0.0 – 1.0]
        confidence          : float [0.0 – 1.0]
        top_signal          : str
        signal_counts       : dict of raw counts
        fake_reasons        : list[str]  (empty if Real)
        positive_signals    : list[str]  (credibility boosts observed)
    """
    text_lower = normalize(prepared["original_text"])
    original_text = prepared["original_text"]
    words = prepared["words"]
    word_count = max(len(words), 10)

    # ---- Count all signals ----
    emotion_count    = count_phrases(text_lower, EMOTIONAL_PHRASES)
    urgency_count    = count_phrases(text_lower, URGENCY_PHRASES)
    sensational_count= count_phrases(text_lower, SENSATIONAL_PHRASES)
    vague_auth_count = count_phrases(text_lower, AUTHORITY_VAGUE_PHRASES)
    credible_count   = count_phrases(text_lower, CREDIBLE_PHRASES)
    conspiracy_count = count_phrases(text_lower, CONSPIRACY_PHRASES)
    fear_count       = count_phrases(text_lower, FEAR_BAIT_PHRASES)
    miracle_count    = count_phrases(text_lower, MIRACLE_PHRASES)
    factual_count    = count_phrases(text_lower, FACTUAL_SIGNAL_WORDS)

    # Structural signals
    numeric_count    = count_numbers(original_text)
    proper_noun_count= count_proper_nouns(original_text)
    caps_abuse       = has_all_caps_abuse(original_text)
    repeated_punct   = count_repeated_punctuation(original_text)
    geo_signals      = has_geographic_signals(original_text)

    # ---- MANIPULATION SCORE ----
    # Uses density (per 100 words) so article length doesn't unfairly skew results.
    bad_raw = (
        emotion_count    * 1.5
        + urgency_count  * 1.2
        + sensational_count * 3.0
        + conspiracy_count  * 3.5
        + fear_count     * 2.0
        + miracle_count  * 2.5
        + vague_auth_count  * 0.8
        + (2.0 if caps_abuse else 0.0)
        + repeated_punct * 0.5
    )

    # Density normalisation: divide by word_count/100, then scale to 0-1
    manipulation_density = bad_raw / (word_count / 100)
    manipulation_score = clamp(manipulation_density / 15.0)  # 15 = saturation threshold

    # ---- CREDIBILITY SCORE ----
    good_raw = (
        credible_count    * 2.0
        + factual_count   * 0.5
        + min(numeric_count, 5) * 1.5       # up to 5 data points counted
        + min(proper_noun_count, 10) * 0.3  # up to 10 proper nouns
        + (2.0 if geo_signals else 0.0)
        + (1.0 if word_count > 50 else 0.0)
    )
    credibility_base = clamp(good_raw / 20.0)  # 20 = saturation threshold

    # Penalise credibility for bad signals
    credibility_penalty = clamp(
        vague_auth_count * 0.08
        + conspiracy_count * 0.15
        + sensational_count * 0.10
        + (0.10 if caps_abuse else 0.0)
    )
    credibility_score = clamp(credibility_base - credibility_penalty)

    # ---- CONFIDENCE SCORE ----
    # How sure are we about our own verdict?
    total_signals = bad_raw + good_raw
    confidence = clamp(min(total_signals, 20) / 20.0 * 0.7 + 0.30)

    # ---- VERDICT ----
    if conspiracy_count >= 2 or miracle_count >= 2:
        verdict = "Fake"
    elif sensational_count >= 2 or (fear_count >= 2 and credible_count == 0):
        verdict = "Fake"
    elif manipulation_score >= 0.55:
        verdict = "Fake"
    elif manipulation_score >= 0.28 or sensational_count == 1 or conspiracy_count == 1:
        verdict = "Suspicious"
    elif credibility_score < 0.35:
        verdict = "Suspicious"
    elif geo_signals and numeric_count >= 1 and manipulation_score < 0.15:
        # Specific + data-backed + low manipulation → Real
        verdict = "Real"
    elif credibility_score >= 0.55 and manipulation_score < 0.20:
        verdict = "Real"
    else:
        verdict = "Suspicious"

    # ---- TOP SIGNAL ----
    signal_map = {
        "emotion":       emotion_count,
        "urgency":       urgency_count,
        "sensationalism":sensational_count,
        "conspiracy":    conspiracy_count,
        "fear_bait":     fear_count,
        "miracle_claim": miracle_count,
        "vague_authority": vague_auth_count,
        "credible_attribution": credible_count,
    }
    top_signal_key = max(signal_map, key=signal_map.get)   # type: ignore[arg-type]
    top_signal = top_signal_key if signal_map[top_signal_key] > 0 else "none"

    # ---- FAKE REASONS (dynamic) ----
    fake_reasons: List[str] = []
    if verdict in ("Fake", "Suspicious"):
        if sensational_count:
            fake_reasons.append("sensational or clickbait language detected")
        if conspiracy_count:
            fake_reasons.append("conspiracy-style wording present")
        if fear_count:
            fake_reasons.append("fear-bait phrases found")
        if miracle_count:
            fake_reasons.append("miracle / pseudoscientific claims detected")
        if emotion_count:
            fake_reasons.append("emotionally charged language used")
        if urgency_count:
            fake_reasons.append("artificial urgency phrases found")
        if vague_auth_count and credible_count == 0:
            fake_reasons.append("unverified authority claims with no named sources")
        if caps_abuse:
            fake_reasons.append("ALL CAPS abuse detected (3+ consecutive all-caps words)")
        if repeated_punct:
            fake_reasons.append(f"repeated punctuation abuse ({repeated_punct} instance(s): !!!, ???)")
        if not fake_reasons:
            fake_reasons.append("low overall credibility signals")

    # ---- POSITIVE SIGNALS ----
    positive_signals: List[str] = []
    if credible_count:
        positive_signals.append("proper attribution language used (e.g. 'according to', 'confirmed by')")
    if numeric_count:
        positive_signals.append(f"contains {numeric_count} measurable data point(s)")
    if proper_noun_count >= 3:
        positive_signals.append("specific named entities (people, places, organisations) present")
    if geo_signals:
        positive_signals.append("geographic specificity detected")
    if factual_count >= 2:
        positive_signals.append("factual reporting tone detected")

    return {
        "verdict": verdict,
        "manipulation_score": round(manipulation_score, 3),
        "credibility_score":  round(credibility_score, 3),
        "confidence":         round(confidence, 3),
        "top_signal":         top_signal,
        "signal_counts": {
            "emotion":         emotion_count,
            "urgency":         urgency_count,
            "sensationalism":  sensational_count,
            "conspiracy":      conspiracy_count,
            "fear_bait":       fear_count,
            "miracle_claim":   miracle_count,
            "vague_authority": vague_auth_count,
            "credible_attribution": credible_count,
            "numeric_data_points":  numeric_count,
            "proper_nouns":    proper_noun_count,
            "all_caps_abuse":  int(caps_abuse),
            "repeated_punct":  repeated_punct,
        },
        "fake_reasons":    fake_reasons,
        "positive_signals": positive_signals,
    }
