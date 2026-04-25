from sqlalchemy import create_engine, text
import os

DB_PATH = r"C:\Users\HP\OneDrive\Desktop\F. AI\factora_ai.db"

print("🔍 Checking DB path exists:", os.path.exists(DB_PATH))

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    echo=False,
    future=True
)

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table'")
    )
    print("📦 Tables found:")
    for row in result:
        print(" -", row[0])
