from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from analyzer.logic.analyzer import analyze_news_api


# ============================================================
# API: Analyze News Text
# ============================================================
@csrf_exempt
def analyze_news_view(request):
    """
    POST JSON:
    {
        "text": "news content here"
    }
    """

    if request.method != "POST":
        return JsonResponse(
            {"error": True, "message": "Only POST method allowed"},
            status=405
        )

    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": True, "message": "Invalid JSON"},
            status=400
        )

    news_text = body.get("text", "").strip()

    if not news_text:
        return JsonResponse(
            {"error": True, "message": "Text field is required"},
            status=400
        )

    # 🔥 Call your core AI logic
    result = analyze_news_api(news_text)

    return JsonResponse(result, safe=False)
