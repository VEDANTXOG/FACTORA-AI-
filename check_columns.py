from sqlalchemy import create_engine, text

DB_PATH = "C:/Users/HP/OneDrive/Desktop/F. AI DATABASE/factora_ai.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(top_news)"))
    print("\n📋 Columns in top_news:\n")
    for row in result:
        print(row[1])
