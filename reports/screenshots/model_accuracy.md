# Model Accuracy Report — Store 44 Sales Forecasting

## Train / Test Split
- Train: 2015-01-01 → 2017-05-31 (880 days)
- Test:  2017-06-01 → 2017-08-15 (76 days)
- Store: Store 44, Quito, Pichincha (#1 ranked store by revenue)

## Results

| Model | MAE | RMSE | MAPE |
|---|---|---|---|
| Naive (last value) | - | - | 19.30% |
| Moving Average (28-day) | - | - | - |
| Seasonal Naive (last year) | - | - | - |
| **SARIMA(1,1,0)(1,0,1)[7]** | - | - | **8.58%** |

## Improvement Over Best Baseline
- Best baseline MAPE: 19.30% (Naive)
- ARIMA MAPE: 8.58%
- **Improvement: 55.5%**

## Best Model
SARIMA(1,1,0)(1,0,1)[7] with weekly seasonal period.

## Notes
- Forecasts 90 days ahead with confidence intervals
- Results written to mart.forecasts in PostgreSQL
- Forecast output saved to models/forecast_output.csv