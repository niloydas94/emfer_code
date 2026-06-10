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

