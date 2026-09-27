import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    dbname="postgres",  # se connecter à la base système, pas garnominigames_dev
    user=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD", ""),
    host=os.getenv("PGHOST", "localhost"),
    port=os.getenv("PGPORT", "5432"),
    autocommit=True,
)

with conn.cursor() as cur:
    cur.execute("DROP DATABASE IF EXISTS garnominigames_dev;")
    cur.execute("CREATE DATABASE garnominigames_dev;")

conn.close()
print("Base de données réinitialisée.")