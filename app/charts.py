import plotly.graph_objects as go
import pandas as pd


def plot_forecast(actuals: pd.DataFrame, forecasts: pd.DataFrame) -> go.Figure:
    """Line chart of actual vs predicted sales with CI band."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=actuals['date'],
        y=actuals['total_sales'],
        name='Actual Sales',
        line=dict(color='#2196F3', width=2),
    ))

    fig.add_trace(go.Scatter(
        x=forecasts['forecast_date'],
        y=forecasts['upper_ci'],
        name='Upper CI',
        line=dict(width=0),
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=forecasts['forecast_date'],
        y=forecasts['lower_ci'].clip(lower=0),
        name='Confidence Interval',
        fill='tonexty',
        fillcolor='rgba(255, 152, 0, 0.2)',
        line=dict(width=0),
    ))
    fig.add_trace(go.Scatter(
        x=forecasts['forecast_date'],
        y=forecasts['predicted_sales'],
        name='Predicted Sales',
        line=dict(color='#FF9800', width=2, dash='dash'),
    ))

    fig.update_layout(
        title='Actual vs Forecasted Sales — Store 44',
        xaxis_title='Date',
        yaxis_title='Sales',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    return fig


def plot_rolling_avg(df: pd.DataFrame) -> go.Figure:
    """30-day rolling average line chart."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_sales'],
        name='Daily Sales',
        line=dict(color='#90CAF9', width=1),
        opacity=0.5,
    ))
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_sales'].rolling(30).mean(),
        name='30-Day Rolling Avg',
        line=dict(color='#1565C0', width=2),
    ))

    fig.update_layout(
        title='30-Day Rolling Average — Store 44',
        xaxis_title='Date',
        yaxis_title='Sales',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
    )
    return fig


def plot_metrics_table(mae: float, rmse: float, mape: float) -> go.Figure:
    """Styled table showing SARIMA model accuracy metrics."""
    fig = go.Figure(go.Table(
        header=dict(
            values=['<b>Model</b>', '<b>MAE</b>', '<b>RMSE</b>', '<b>MAPE</b>'],
            fill_color='#1565C0',
            font=dict(color='white', size=13),
            align='center',
            height=36,
        ),
        cells=dict(
            values=[
                ['SARIMA (1,1,0)(1,0,1)[7]'],
                [f'{mae:,.2f}'],
                [f'{rmse:,.2f}'],
                [f'{mape:.2f}%'],
            ],
            fill_color='#F5F5F5',
            align='center',
            height=32,
            font=dict(size=13),
        ),
    ))
    fig.update_layout(title='Model Accuracy Metrics', margin=dict(t=40, b=0))
    return fig
