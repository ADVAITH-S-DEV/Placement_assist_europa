import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

password = "Placementeuropa%40123"

hosts_to_try = [
    # Direct connection
    f"postgresql://postgres:{password}@db.azednberofnovtgcpaqi.supabase.co:5432/postgres",
    # Session pooler (pgbouncer)
    f"postgresql://postgres.azednberofnovtgcpaqi:{password}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres",
    # Transaction pooler  
    f"postgresql://postgres.azednberofnovtgcpaqi:{password}@aws-0-ap-south-1.pooler.supabase.com:5432/postgres",
]

for url in hosts_to_try:
    print(f"\nTrying: {url[:60]}...")
    try:
        conn = psycopg2.connect(url, connect_timeout=8, sslmode='require')
        print("SUCCESS!")
        conn.close()
        break
    except Exception as e:
        print(f"FAILED: {e}")
