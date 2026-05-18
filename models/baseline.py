import pandas as pd
import numpy as np
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'etl'))
from config import get_engine

def get_daily_sales():
    engine = get_engine()
    query = text("""
        SELECT date, SUM(total_sales) AS total_sales
        FROM mart.daily_sales
        WHERE store_nbr = 44
        GROUP BY date
        ORDER BY date
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df

def naive_forecast(train, test):
    last_value = train['total_sales'].iloc[-1]
    predictions = [last_value] * len(test)
    return predictions

def moving_average_forecast(train, test, window=28):
    last_ma = train['total_sales'].rolling(window).mean().iloc[-1]
    predictions = [last_ma] * len(test)
    return predictions

def seasonal_naive_forecast(train, test):
    predictions = []
    for i in range(len(test)):
        idx = -(365 - i) if (365 - i) <= len(train) else 0
        predictions.append(train['total_sales'].iloc[idx])
    return predictions

def calculate_metrics(actual, predicted, model_name):
    actual = np.array(actual)
    predicted = np.array(predicted)
    mae  = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    mape = np.mean(np.abs((actual - predicted) / 
                   np.where(actual == 0, 1, actual))) * 100
    print(f"\n{model_name}:")
    print(f"  MAE  : {mae:,.2f}")
    print(f"  RMSE : {rmse:,.2f}")
    print(f"  MAPE : {mape:.2f}%")
    return {"model": model_name, "MAE": round(mae,2), 
            "RMSE": round(rmse,2), "MAPE": round(mape,2)}

if __name__ == "__main__":
    print("Loading data from PostgreSQL...")
    df = get_daily_sales()

    # Train/test split — chronological
    train = df[df.index < '2017-06-01']
    test  = df[df.index >= '2017-06-01']

    print(f"Train size: {len(train)} days")
    print(f"Test size : {len(test)} days")
    print("\n--- Baseline Model Results ---")

    results = []
    results.append(calculate_metrics(
        test['total_sales'],
        naive_forecast(train, test),
        "Naive (last value)"
    ))
    results.append(calculate_metrics(
        test['total_sales'],
        moving_average_forecast(train, test),
        "Moving Average (28-day)"
    ))
    results.append(calculate_metrics(
        test['total_sales'],
        seasonal_naive_forecast(train, test),
        "Seasonal Naive (last year)"
    ))

    print("\n--- Summary Table ---")
    print(pd.DataFrame(results).to_string(index=False))