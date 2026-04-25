from sqlalchemy import create_engine, text

DB_PATH = "C:/Users/HP/OneDrive/Desktop/F. AI DATABASE/factora_ai.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)

print("📍 Using database:", DB_PATH)

with engine.begin() as conn:
    # ------------------------------------------------------------
    # news_analysis table
    # ------------------------------------------------------------
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS news_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_text TEXT NOT NULL,
            manipulation_score FLOAT,
            verification_score FLOAT,
            verdict TEXT,
            primary_signal TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """))

    # ------------------------------------------------------------
    # top_news table (FINAL STRUCTURE)
    # ------------------------------------------------------------
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS top_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            published TEXT,
            category TEXT NOT NULL,
            summary TEXT NOT NULL,
            fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """))

print("✅ Tables CREATED successfully")

