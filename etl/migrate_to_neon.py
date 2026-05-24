import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()

# Local PostgreSQL
local_password = quote_plus(os.getenv("DB_PASS"))
local_engine = create_engine(
    f"postgresql+psycopg2://postgres:{local_password}@localhost:5432/sales_forecast"
)

# Neon PostgreSQL
neon_url = os.getenv("NEON_DB_URL")
neon_engine = create_engine(neon_url)

def migrate_table(table_name, local_eng, neon_eng):
    print(f"Migrating {table_name}...")
    df = pd.read_sql(f"SELECT * FROM {table_name}", local_eng)
    df.to_sql(
        table_name.split('.')[1],
        neon_eng,
        schema=table_name.split('.')[0],
        if_exists='replace',
        index=False,
        chunksize=10000
    )
    print(f"  Done — {len(df)} rows migrated")

if __name__ == "__main__":
    migrate_table("mart.daily_sales", local_engine, neon_engine)
    migrate_table("mart.store_performance", local_engine, neon_engine)
    migrate_table("mart.forecasts", local_engine, neon_engine)
    print("\nAll tables migrated to Neon successfully!")