import pandas as pd
import numpy as np
from sqlalchemy import text
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'etl'))
from config import get_engine
from pmdarima import auto_arima
import warnings
warnings.filterwarnings('ignore')

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

def calculate_metrics(actual, predicted, model_name):
    actual    = np.array(actual)
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

    train = df[df.index < '2017-06-01']['total_sales']
    test  = df[df.index >= '2017-06-01']['total_sales']

    print(f"Train size: {len(train)} days")
    print(f"Test size : {len(test)} days")

    print("\nRunning auto_arima to find best parameters...")
    print("(This may take 3-5 minutes — please wait...)")

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
        trace=True
    )

    print(f"\nBest model: {model.order} x {model.seasonal_order}")
    print(model.summary())

    print("\nGenerating forecast on test set...")
    predictions, conf_int = model.predict(
        n_periods=len(test),
        return_conf_int=True
    )

    result = calculate_metrics(test, predictions, "ARIMA")

    print("\nGenerating 90-day future forecast...")
    future_forecast, future_ci = model.predict(
        n_periods=90,
        return_conf_int=True
    )

    last_date = df.index[-1]
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=90
    )

    forecast_df = pd.DataFrame({
        'forecast_date'   : future_dates,
        'predicted_sales' : future_forecast,
        'lower_ci'        : future_ci[:, 0],
        'upper_ci'        : future_ci[:, 1]
    })

    print("\nFirst 10 days of 90-day forecast:")
    print(forecast_df.head(10).to_string(index=False))

    forecast_df.to_csv('models/forecast_output.csv', index=False)
    print("\nForecast saved to models/forecast_output.csv")
    print(f"\nFinal ARIMA MAPE: {result['MAPE']}%")
    print(f"Best baseline MAPE: 14.74%")
    improvement = ((14.74 - result['MAPE']) / 14.74) * 100
    print(f"Improvement over best baseline: {improvement:.2f}%")