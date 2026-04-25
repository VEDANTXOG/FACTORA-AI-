from typing import Dict, Any
import re
import string
import unicodedata
from collections import defaultdict

# TRUSTED SOURCES
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
    'mit.edu/news', 'stanford.edu/news',
    'openai.com/blog', 'deepmind.com/blog', 'ai.googleblog.com',
    'foreignpolicy.com', 'foreignaffairs.com',
    'brookings.edu', 'csis.org', 'iiss.org',
    'carnegieendowment.org', 'chathamhouse.org',
    'cfr.org', 'un.org', 'nato.int', 'imf.org', 'worldbank.org',
    'morningstar.com', 'seekingalpha.com', 'investopedia.com',
    'sec.gov', 'nasdaq.com', 'nyse.com',
    'npr.org', 'pbs.org/newshour',
    'abc.net.au/news', 'cbc.ca/news', 'rfi.fr',
    'sverigesradio.se',
    'japantimes.co.jp', 'straitstimes.com',
    'scmp.com', 'koreaherald.com',
    'channelnewsasia.com',
    'espn.com', 'espncricinfo.com', 'cricbuzz.com',
    'bbc.com/sport', 'skysports.com', 'cbssports.com', 'nbcsports.com',
    'foxsports.com', 'sports.yahoo.com', 'theathletic.com',
    'sportstar.thehindu.com',
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
    'deepmind.google', 'machinelearning.apple.com', 'anthropic.com',
    'huggingface.co/blog', 'rand.org', 'project-syndicate.org',
    'asiasociety.org', 'ec.europa.eu', 'federalreserve.gov',
    'occrp.org', 'bellingcat.com', 'thebureauinvestigates.com',
    'fullfact.org', 'politifact.com', 'snopes.com'
]


# CATEGORY MAPPINGS
CATEGORY_SOURCE_MAP = {
    "Politics": {
        "reuters.com", "apnews.com", "afp.com",
        "bbc.com", "cnn.com", "aljazeera.com", "dw.com", "france24.com",
        "nytimes.com", "theguardian.com", "washingtonpost.com",
        "wsj.com", "economist.com",
        "politico.com", "axios.com",
        "foreignpolicy.com", "foreignaffairs.com",
        "brookings.edu", "csis.org", "cfr.org",
        "carnegieendowment.org", "chathamhouse.org",
        "un.org"
    },
    "World": {
        "reuters.com", "apnews.com", "afp.com",
        "bbc.com", "cnn.com", "aljazeera.com", "dw.com", "france24.com",
        "nytimes.com", "theguardian.com",
        "npr.org", "pbs.org",
        "cbc.ca", "abc.net.au", "rfi.fr",
        "japantimes.co.jp", "straitstimes.com",
        "scmp.com"
    },
    "Economy": {
        "bloomberg.com", "financialtimes.com",
        "cnbc.com", "wsj.com", "economist.com",
        "forbes.com", "businessinsider.com",
        "marketscreener.com",
        "moneycontrol.com", "livemint.com",
        "morningstar.com", "seekingalpha.com",
        "investopedia.com",
        "imf.org", "worldbank.org"
    },
    "Business": {
        "bloomberg.com", "financialtimes.com",
        "wsj.com", "forbes.com", "cnbc.com",
        "businessinsider.com",
        "marketscreener.com",
        "moneycontrol.com", "livemint.com",
        "sec.gov", "nasdaq.com", "nyse.com"
    },
    "Health": {
        "who.int", "cdc.gov", "nih.gov", "nhs.uk",
        "nejm.org", "thelancet.com", "bmj.com",
        "jamanetwork.com",
        "medicalnewstoday.com", "statnews.com"
    },
    "Science": {
        "nature.com", "science.org", "sciencemag.org",
        "cell.com", "pnas.org",
        "sciencedaily.com", "phys.org",
        "mit.edu", "stanford.edu"
    },
    "Technology": {
        "techcrunch.com", "theverge.com", "wired.com",
        "arstechnica.com", "zdnet.com",
        "technologyreview.com", "thenextweb.com",
        "engadget.com", "cnet.com", "slashdot.org",
        "mit.edu", "stanford.edu",
        "openai.com", "deepmind.com", "ai.googleblog.com"
    },
    "Defense": {
        "reuters.com", "apnews.com",
        "bbc.com", "aljazeera.com",
        "foreignpolicy.com", "foreignaffairs.com",
        "csis.org", "iiss.org", "rand.org",
        "nato.int", "defense.gov"
    },
    "Sports": {
        "espn.com", "espncricinfo.com", "cricbuzz.com",
        "bbc.com/sport", "skysports.com",
        "cbssports.com", "nbcsports.com",
        "foxsports.com", "sports.yahoo.com", "theathletic.com",
        "fifa.com", "uefa.com", "olympics.com",
        "icc-cricket.com", "rugbyworldcup.com",
        "formula1.com", "nba.com", "nfl.com", "mlb.com"
    }
}

PRIORITY_ORDER = ["Politics", "World", "Defense", "Economy", "Business", "Sports", "Technology", "AI"]

CATEGORY_KEYWORDS = {
    "Politics": [
        "election", "minister", "government", "parliament", "policy", "president",
        "legislation", "ballot", "democrat", "republican", "senate", "congress",
        "cabinet", "bureaucracy", "opposition", "coalition", "governance", "mayor",
        "voters", "referendum", "lobbyist", "sanctions", "impeachment", "authority",
        "european union", "eu", "iran", "irgc", "revolutionary guard",
        "terrorist", "terrorism", "designation", "foreign policy"
    ],
    "World": [
        "international", "global", "nato", "un", "diplomacy", "treaty",
        "geopolitics", "bilateral", "summit", "foreign affairs", "border", "humanitarian",
        "embassy", "ambassador", "multilateral", "expatriate", "refugee", "migration",
        "peacekeeping", "envoys", "territory", "overseas", "continent", "world bank"
    ],
    "Defense": [
        "army", "military", "missile", "defense", "weapons", "troops",
        "warfare", "pentagon", "arsenal", "navy", "air force", "infantry",
        "ballistic", "warship", "ammunition", "deployment", "intelligence", "espionage",
        "security forces", "insurgency", "counterterrorism", "battalion", "artillery"
    ],
    "Economy": [
        "inflation", "gdp", "recession", "budget", "fiscal", "interest rate",
        "currency", "central bank", "deficit", "taxation", "microeconomics", "macroeconomics",
        "monetary", "deflation", "trade gap", "exports", "imports", "commodity",
        "economic growth", "austerity", "index", "consumer price", "treasury"
    ],
    "Business": [
        "company", "ceo", "startup", "stock", "revenue", "ipo",
        "merger", "acquisition", "shares", "equity", "enterprise", "venture capital",
        "bankruptcy", "dividend", "stakeholder", "profit", "quarterly", "corporation",
        "market cap", "investment", "commercial", "founder", "trade", "nasdaq"
    ],
    "Sports": [
        "athletics", "football", "soccer", "basketball", "tennis", "cricket",
        "nfl", "nba", "premier league", "epl", "champions league", "world cup",
        "olympics", "grand slam", "super bowl", "tournament", "championship",
        "athlete", "coach", "match", "score", "playoffs", "offside", "hat-trick",
        "knockout", "formula 1", "f1", "ufc", "boxing", "golf", "mlb", "nhl"
    ],
    "Technology": [
        "software", "internet", "platform", "cloud", "tech",
        "cybersecurity", "hardware", "encryption", "semiconductor", "bandwidth", "infrastructure",
        "blockchain", "crypto", "database", "connectivity", "app", "mobile",
        "nanotechnology", "biotech", "gadget", "silicon", "telecom", "digital"
    ],
    "AI": [
        "artificial intelligence", "machine learning", "llm", "chatbot", "generative ai",
        "neural network", "deep learning", "nlp", "computer vision", "automation", "robotics",
        "algorithm", "gpt", "transformer model", "data science", "turing",
        "synthetic media", "inference", "training data", "predictive"
    ]
}

def validate_sources_for_category(category: str, sources: list) -> list:
    allowed = CATEGORY_SOURCE_MAP.get(category)
    if not allowed:
        return sources
    return [s for s in sources if s in allowed]

def prepare_text_for_ai(text: str) -> Dict[str, Any]:
    lowered = unicodedata.normalize("NFKC", text).lower()
    words = lowered.translate(str.maketrans("", "", string.punctuation)).split()
    return {
        "original_text": text,
        "words": words
    }

def detect_news_category(text: str) -> str:
    clean_text = re.sub(r'[^a-zA-Z0-9\\s]', '', text.lower())
    scores = defaultdict(int)
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
    text = prepared["original_text"].lower()
    words = prepared["words"]
    EMOTIONAL = {"shocking", "terrifying", "panic", "miracle", "disaster", "horrifying", "unbelievable", "unprecedented", "never seen before", "historic crisis"}
    URGENCY = {"breaking", "urgent", "act now", "limited time", "just happened", "immediate", "crisis", "emergency"}
    AUTHORITY = {"experts say", "sources say", "officials claim", "studies show", "research confirms"}
    emotion = sum(1 for w in words if w in EMOTIONAL)
    urgency = sum(1 for p in URGENCY if p in text)
    authority = sum(1 for p in AUTHORITY if p in text)
    manipulation_score = min((emotion + urgency * 2) / max(len(words), 10), 1.0)
    verification_score = 1.0 - min((authority + emotion * 0.5) / 5, 0.4)
    if manipulation_score >= 0.6:
        verdict = "Fake"
    elif manipulation_score >= 0.4:
        verdict = "Suspicious"
    elif verification_score < 0.4:
        verdict = "Suspicious"
    else:
        verdict = "Real"
    top_signal = max(
        ("emotion", emotion),
        ("urgency", urgency),
        ("authority", authority),
        key=lambda x: x[1]
    )[0]
    fake_reasons = [
        "no trusted sources reported it",
        "exaggerated language used", 
        "claim is unrealistic"
    ]
    return {
        "verdict": verdict,
        "manipulation_score": round(manipulation_score, 2),
        "credibility_score": round(verification_score, 2),
        "top_signal": top_signal,
        "fake_reasons": fake_reasons if verdict == "Fake" else []
    }

def external_context_check(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    found_sources = [source for source in TRUSTED_SOURCES if source.split('.')[0] in text_lower]
    credible_signals = sum([
        len(text.split()) > 40,
        ',' in text,
        any(w in text_lower for w in ["said", "according to", "official"]),
        any(w in text_lower for w in ["government", "ministry", "authorities"]),
        len(re.findall(r'[A-Z][a-z]+', text)) > 5  # Proper nouns
    ])
    if found_sources:
        status = "Coverage found"
    elif credible_signals >= 3:
        status = "Likely real-world reporting (no source cited)"
    else:
        status = "No confirmed coverage"
    return {"status": status, "sources": found_sources[:3]}

def generate_actual_summary(news_text: str, max_sentences: int = 2) -> str:
    sentences = re.split(r'(?<=[.!?])\\s+', news_text.strip())
    if not sentences:
        return "Summary unavailable."
    # Take longest sentences
    sentences.sort(key=len, reverse=True)
    return '. '.join(sentences[:max_sentences]).strip() + '.'

def detect_input_type(text: str) -> tuple[str, str]:
    cleaned = text.strip().lower()
    word_count = len(cleaned.split())
    
    # Founder questions
    founder_phrases = ["who is your founder","founder","who are your founders" "who created you", "who made you", "your founders"]
    if any(phrase in cleaned for phrase in founder_phrases):
        return "founder", "VEDANT BABAR and YUVRAJ DESAI are my founders."
                  
    # Greetings
    greetings = {"hi", "hello", "hey", "yo", "wassup", "hii"}
    if cleaned in greetings or word_count == 1:
        return "greeting", "👋 Hi, I am Factora AI. Paste a news article and I will analyze it for you."
    
    # General questions / short
    if cleaned.endswith("?") or word_count < 5:
        return "question", "🤖 I am designed to analyze news articles. Please paste a news report."
    
    # Too short invalid
    if word_count < 15:
        return "invalid", "⚠️ Please enter a valid news article for analysis."
    
    return "news", None

def run_factora_analysis(text: str) -> Dict[str, Any]:
    input_type, response_msg = detect_input_type(text)
    if input_type != "news":
        return {
            "type": input_type,
            "response": response_msg
        }
    
    # News analysis
    prepared = prepare_text_for_ai(text)
    manipulation = analyze_manipulation(prepared)
    verification = external_context_check(text)
    category = detect_news_category(text)
    summary = generate_actual_summary(text)
    # Validate sources
    if verification["status"] == "Coverage found" and verification.get("sources"):
        verification["sources"] = validate_sources_for_category(category, verification["sources"])
        if not verification["sources"]:
            verification["status"] = "No confirmed coverage"
    # Adjust verdict if unverified
    if verification["status"] == "No confirmed coverage" and manipulation["verdict"] in ["Real"]:
        manipulation["verdict"] = "Suspicious"
        manipulation["credibility_score"] = min(manipulation["credibility_score"], 0.4)
    return {
        "type": "news",
        "manipulation": manipulation,
        "verification": verification,
        "category": category,
        "summary": summary
    }
