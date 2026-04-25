from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from .models import NewsAnalysis
from django.shortcuts import get_object_or_404

from factora_backend.bot import run_factora_analysis

@csrf_exempt
def analyze_news(request):
    print(f"📨 ANALYZE endpoint hit: {request.method}")
    print(f"   User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')[:100]}")
    print(f"   Content-Length: {request.META.get('CONTENT_LENGTH', '0')}")
    print(f"   Content-Type: {request.META.get('CONTENT_TYPE', 'None')}")
    
    if request.method != "POST":
        print("❌ Rejected: Not POST")
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
        news_text = data.get("text", "")
        print(f"   Text preview: {repr(news_text[:50])}... (len={len(news_text)})")
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not news_text.strip():
        print("❌ Empty text")
        return JsonResponse({"error": "No text provided"}, status=400)

    print("🔄 Running analysis...")
    result = run_factora_analysis(news_text)
    print(f"✅ Analysis type: {result.get('type', 'news')}")
    
    # ALWAYS JSON - Handle ALL cases
    if result.get("type") != "news":
        print("   → Non-news response")
        return JsonResponse({
            "type": result["type"],
            "response": result["response"]
        })

    # News processing with bulletproof JSON
    try:
        manipulation = result["manipulation"]
        verification = result["verification"]
        sources_list = verification.get("sources", []) if verification["status"] == "Coverage found" else []
        sources_str = ", ".join(sources_list) if sources_list else "No credible sources found"
        top_signal = manipulation.get("top_signal", "unknown").title()
        ver_status = verification["status"]
        
        reason_parts = []
        top_signal_lower = top_signal.lower()
        
        # Signal explanations
        signals = []
        if top_signal_lower == "emotion":
            signals.append("Heavy emotional language (shocking, terrifying, panic) creates hype over facts.")
        elif top_signal_lower == "urgency":
            signals.append("Urgency words (breaking, urgent) pressure quick belief without verification.")
        elif top_signal_lower == "authority":
            signals.append("Vague 'experts say' claims lack specific attribution.")
        
        if manipulation["verdict"].lower() == "fake" and manipulation.get("fake_reasons"):
            strong_reasons = manipulation["fake_reasons"]
            reason = f"This is likely fake because:\n1. {strong_reasons[0]}\n2. {strong_reasons[1]}\n3. {strong_reasons[2]}"
        else:
            reason_parts.append(f"- Language manipulation: {signals[0] if signals else 'Subtle patterns detected.'}")
            reason_parts.append(f"- Verification: {ver_status.lower()}.")
            if sources_list:
                reason_parts.append("- Credible sources detected.")
            else:
                reason_parts.append("- Lacks trusted sources.")
            reason = "\n".join(reason_parts)
        
        # Map verdict to uppercase
        verdict_upper = manipulation["verdict"].upper()
        
# FIXED: Removed auto-save from analyze_news() - manual save only via save_article()
        # uid = None  # No DB save
        
        response_data = {
            "type": "news",
            "verdict": verdict_upper,
            "reason": reason,
            "sources": sources_str,
            "category": top_signal,
            "manipulation_score": float(manipulation['manipulation_score']),
            "credibility_score": float(manipulation['credibility_score']),
        }
        print("✅ JSON response sent - NO AUTO-SAVE")
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return JsonResponse({"error": f"Analysis failed: {str(e)}"}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)

def home(request):
    return JsonResponse({"message": "FACTORA AI Backend is Running 🚀", "endpoint": "/analyze/"})

@csrf_exempt
def get_saved_articles(request):
    if request.method == 'GET':
        articles = NewsAnalysis.objects.order_by('-created_at')[:20]
        data = []
        for article in articles:
            data.append({
                'uid': article.uid,
                'news_id': article.news_id,
                'snippet': (article.content[:100] + '...') if len(article.content) > 100 else article.content,
                'verdict': article.verdict,
                'manipulation_score': article.manipulation_score,
                'verification_score': article.verification_score,
                'created_at': article.created_at.isoformat(),
            })
        return JsonResponse({'articles': data})
    return JsonResponse({'error': 'Only GET allowed'}, status=405)

@csrf_exempt
def delete_article(request, uid):
    if request.method == 'DELETE':
        article = get_object_or_404(NewsAnalysis, uid=uid)
        article.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Only DELETE allowed'}, status=405)

@csrf_exempt
def get_article_detail(request, uid):
    if request.method == 'GET':
        article = get_object_or_404(NewsAnalysis, uid=uid)
        return JsonResponse({
            "type": "saved_article",
            "verdict": article.verdict,
            "reason": article.reason,
            "sources": article.sources,
            "category": getattr(article, 'category', 'SAVED'),
            "manipulation_score": float(article.manipulation_score or 0.5),
            "credibility_score": float(article.verification_score or 0.5),
            "content": article.content,
            "news_id": article.news_id,
            "created_at": article.created_at.isoformat()
        })
    return JsonResponse({'error': 'Only GET allowed'}, status=405)

@csrf_exempt
def save_article(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            analysis = NewsAnalysis(
                content=data.get("content", "")[:1000],
                verdict=data.get("verdict", "SUSPICIOUS"),
                reason=data.get("reason", ""),
                sources=data.get("sources", ""),
                manipulation_score=float(data.get("manipulation_score", 50)),
                verification_score=float(data.get("credibility_score", 50)),
            )
            analysis.save()
            return JsonResponse({
                "success": True, 
                "uid": analysis.uid,
                "news_id": analysis.news_id,
                "message": f"Saved as {analysis.news_id}"
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST method allowed"}, status=405)

