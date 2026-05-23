import pandas as pd
import numpy as np
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'etl'))
from config import get_engine, get_connection
from pmdarima import auto_arima
import warnings
warnings.filterwarnings('ignore')

TRAIN_CUTOFF  = '2017-06-01'
FORECAST_DAYS = 90
MODEL_VERSION = 'sarima_v1'
FAMILY        = 'TOTAL'


def get_daily_sales(store_nbr, engine):
    query = text("""
        SELECT date, SUM(total_sales) AS total_sales
        FROM mart.daily_sales
        WHERE store_nbr = :s
        GROUP BY date
        ORDER BY date
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"s": store_nbr})
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df


def calculate_mape(actual, predicted):
    actual    = np.array(actual)
    predicted = np.array(predicted)
    return float(np.mean(np.abs((actual - predicted) /
                  np.where(actual == 0, 1, actual))) * 100)


def forecast_store(store_nbr, engine):
    """Fit SARIMA for one store; return (mape, list-of-row-tuples) or (None, None)."""
    df = get_daily_sales(store_nbr, engine)

    train = df[df.index < TRAIN_CUTOFF]['total_sales']
    test  = df[df.index >= TRAIN_CUTOFF]['total_sales']

    if len(train) < 60 or len(test) == 0:
        return None, None

    model = auto_arima(
        train,
        seasonal=True,
        m=7,
        start_p=0, max_p=3,
        start_q=0, max_q=3,
        d=None,
        start_P=0, max_P=2,
        start_Q=0, max_Q=2,
        D=None,
        information_criterion='aic',
        stepwise=True,
        suppress_warnings=True,
        error_action='ignore',
        trace=False,
    )

    test_preds = model.predict(n_periods=len(test))
    mape = calculate_mape(test, test_preds)

    future_preds, future_ci = model.predict(
        n_periods=FORECAST_DAYS,
        return_conf_int=True,
    )

    last_date    = df.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=FORECAST_DAYS,
    )

    rows = [
        (
            int(store_nbr),
            FAMILY,
            date.date(),
            round(float(pred), 4),
            round(float(ci[0]), 4),
            round(float(ci[1]), 4),
            MODEL_VERSION,
        )
        for date, pred, ci in zip(future_dates, future_preds, future_ci)
    ]

    return mape, rows


def write_to_db(all_rows):
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
                all_rows,
            )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    engine      = get_engine()
    all_rows    = []
    summary     = []
    total       = 54

    print(f"Running SARIMA for {total} stores — this will take a while...\n")

    for store_nbr in range(1, total + 1):
        try:
            mape, rows = forecast_store(store_nbr, engine)
            if rows is None:
                print(f"Store {store_nbr}/{total} — skipped (insufficient data)")
                continue
            all_rows.extend(rows)
            summary.append({"store_nbr": store_nbr, "MAPE": round(mape, 2)})
            print(f"Store {store_nbr}/{total} done — MAPE: {mape:.2f}%")
        except Exception as e:
            print(f"Store {store_nbr}/{total} — ERROR: {e}")

    print(f"\nTruncating mart.forecasts and inserting {len(all_rows)} rows...")
    write_to_db(all_rows)
    print(f"Done. {len(all_rows)} rows written to mart.forecasts.")

    summary_df = pd.DataFrame(summary)
    out_path   = os.path.join(os.path.dirname(__file__), 'all_stores_forecast_summary.csv')
    summary_df.to_csv(out_path, index=False)
    print(f"\nSummary saved to models/all_stores_forecast_summary.csv")
    print(f"\n{summary_df.to_string(index=False)}")
