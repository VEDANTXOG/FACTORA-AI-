"""
views.py — Factora AI (Django)
REST API endpoint for news analysis.

Paste this into your Django app's views.py.
Make sure analyzer.py, scoring.py, categories.py, sources.py, utils.py
are all in the same directory (or on the Python path).
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from factora_backend.bot import run_factora_analysis

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _score_to_percent(value: float) -> str:
    """Convert a 0.0–1.0 float to a readable percentage string."""
    return f"{round(value * 100)}%"


def _format_response(result: dict) -> dict:
    """
    Transform the internal result dict into a clean, frontend-ready JSON shape.
    Converts raw floats to percentage strings for display.
    """
    if result["type"] != "news":
        # Non-news input (greeting, question, etc.)
        return {
            "type":    result["type"],
            "message": result.get("response", ""),
        }

    m = result["manipulation"]
    v = result["verification"]
    e = result["explanation"]

    return {
        "type":     "news",
        "verdict":  m["verdict"],
        "category": result["category"],
        "summary":  result["summary"],

        "scores": {
            "manipulation_score": _score_to_percent(m["manipulation_score"]),
            "credibility_score":  _score_to_percent(m["credibility_score"]),
            "confidence":         _score_to_percent(m["confidence"]),
            "confidence_label":   m["confidence"],
        },

        "sources": {
            "status":  v["status"],
            "found":   v["sources"],
        },

        "explanation": {
            "headline":          e["headline"],
            "reasoning":         e["reasoning"],
            "confidence_label":  e["confidence_label"],
            "full_report":       e["full_report"],
        },

        "signal_breakdown": m["signal_counts"],

        # Shown only when verdict is Suspicious/Fake
        "fake_reasons":     m.get("fake_reasons", []),
        # Shown only when article has positive signals
        "positive_signals": m.get("positive_signals", []),
    }


# ---------------------------------------------------------------------------
# API VIEW
# ---------------------------------------------------------------------------

@csrf_exempt
@require_POST
def analyze_news(request):
    """
    POST /api/analyze/
    Body (JSON): { "text": "<news article>" }

    Returns: full Factora AI analysis as JSON.
    """
    # ── Parse request body ─────────────────────────────────────────────────
    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON. Send: { \"text\": \"<article>\" }"},
            status=400,
        )

    text = body.get("text", "").strip()

    if not text:
        return JsonResponse(
            {"error": "Missing 'text' field in request body."},
            status=400,
        )

    # ── Run analysis ───────────────────────────────────────────────────────
    try:
        raw_result = run_factora_analysis(text)
        response_data = _format_response(raw_result)
        return JsonResponse(response_data, status=200)
    except Exception as exc:
        logger.exception("Factora analysis failed: %s", exc)
        return JsonResponse(
            {"error": "Analysis failed. Please try again."},
            status=500,
        )


# ---------------------------------------------------------------------------
# OPTIONAL: health-check endpoint
# ---------------------------------------------------------------------------

def health_check(request):
    """GET /api/health/ — confirms the API is running."""
    return JsonResponse({"status": "ok", "service": "Factora AI"})
