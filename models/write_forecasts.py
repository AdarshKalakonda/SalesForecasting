import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'etl'))
from config import get_connection

STORE_NBR     = 44
FAMILY        = 'TOTAL'
MODEL_VERSION = 'sarima_v1'
CSV_PATH      = os.path.join(os.path.dirname(__file__), 'forecast_output.csv')

def write_forecasts():
    df = pd.read_csv(CSV_PATH, parse_dates=['forecast_date'])

    rows = [
        (
            STORE_NBR,
            FAMILY,
            row['forecast_date'].date(),
            round(row['predicted_sales'], 4),
            round(row['lower_ci'], 4),
            round(row['upper_ci'], 4),
            MODEL_VERSION,
        )
        for _, row in df.iterrows()
    ]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE mart.forecasts")
            cur.executemany(
                """
                INSERT INTO mart.forecasts
                    (store_nbr, family, forecast_date, predicted_sales,
                     lower_ci, upper_ci, model_version, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                rows,
            )
        conn.commit()
        print(f"Truncated mart.forecasts and inserted {len(rows)} rows.")
    finally:
        conn.close()

if __name__ == "__main__":
    write_forecasts()
