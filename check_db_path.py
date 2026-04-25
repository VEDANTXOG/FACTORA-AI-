import os
from sqlalchemy import create_engine

engine = create_engine("sqlite:///factora_ai.db")

print("📍 Database absolute path:")
print(os.path.abspath("factora_ai.db"))
