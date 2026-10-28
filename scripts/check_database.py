import os

import psycopg
from dotenv import load_dotenv

load_dotenv()
with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    row = conn.execute(
        "select extname from pg_extension where extname='vector'"
    ).fetchone()
print(
    "Vector extension is installed"
    if row
    else "Vector extension is not installed"
)
