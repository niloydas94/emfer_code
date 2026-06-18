#@title Fetching MF NAV data
import pandas as pd
import requests

from src.emfer.config.settings import BASE_MFAPI_URL

def get_all_schemes():
    url = f'{BASE_MFAPI_URL}'
    return pd.DataFrame(requests.get(url).json())

def fetch_nav_history(mf_scheme_code):
    url = f'{BASE_MFAPI_URL}/{mf_scheme_code}'

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    nav_data = data['data']

    df = pd.DataFrame(nav_data)

    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df['nav'] = pd.to_numeric(df['nav'])

    df = df.sort_values('date')

    fund_name = data['meta']['scheme_name']
    df['fund_name'] = fund_name

    return df, fund_name


def clean_nav_history(nav_history):
    nav_history = nav_history.sort_values("date").reset_index(drop=True)
    valid_nav_history = nav_history[nav_history["nav"] > 0]

    if valid_nav_history.empty:
        return nav_history.iloc[0:0].copy(), {
            "trimmed_start_rows": len(nav_history),
            "removed_later_rows": 0,
            "effective_start_date": None,
            "invalid_dates": nav_history["date"].dt.date.tolist(),
        }

    effective_start_date = valid_nav_history["date"].iloc[0]
    rows_before_valid_start = nav_history[nav_history["date"] < effective_start_date]
    nav_history_after_start = nav_history[nav_history["date"] >= effective_start_date]
    invalid_rows_after_start = nav_history_after_start[nav_history_after_start["nav"] <= 0]
    cleaned_nav_history = nav_history_after_start[nav_history_after_start["nav"] > 0].copy()

    return cleaned_nav_history, {
        "trimmed_start_rows": len(rows_before_valid_start),
        "removed_later_rows": len(invalid_rows_after_start),
        "effective_start_date": effective_start_date.date(),
        "invalid_dates": invalid_rows_after_start["date"].dt.date.tolist(),
    }


def detect_nav_anomalies(nav_history):
    nav_history = nav_history.sort_values("date").copy()
    nav_history["previous_nav"] = nav_history["nav"].shift(1)
    nav_history["nav_ratio"] = nav_history["nav"] / nav_history["previous_nav"]

    anomaly_rows = nav_history[
        (nav_history["previous_nav"] > 0)
        & (
            (nav_history["nav_ratio"] <= 0.20)
            | (nav_history["nav_ratio"] >= 5)
        )
    ]

    return anomaly_rows[["date", "previous_nav", "nav", "nav_ratio"]].to_dict("records")

