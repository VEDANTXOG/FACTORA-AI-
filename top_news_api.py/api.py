from sqlalchemy import create_engine, text

DB_PATH = "C:/Users/HP/OneDrive/Desktop/F. AI DATABASE/factora_ai.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

CATEGORIES = [
    "World",
    "India",
    "Business",
    "Technology",
    "Health"
]

def get_top_news(limit_per_category=5):
    result = {}

    with engine.connect() as conn:
        for category in CATEGORIES:
            rows = conn.execute(
                text("""
                    SELECT title, summary, source, link, published
                    FROM top_news
                    WHERE category = :category
                    ORDER BY fetched_at DESC
                    LIMIT :limit
                """),
                {"category": category, "limit": limit_per_category}
            ).fetchall()

            result[category] = [
                {
                    "title": row.title,
                    "summary": row.summary,
                    "source": row.source,
                    "link": row.link,
                    "published": row.published
                }
                for row in rows
            ]

    return result


# Test run (for you only)
if __name__ == "__main__":
    news = get_top_news()
    for cat, items in news.items():
        print(f"\n🟢 {cat}")
        for i, n in enumerate(items, 1):
            print(f"{i}. {n['title']} ({n['source']})")
