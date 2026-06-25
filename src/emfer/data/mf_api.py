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


def add_nav_indicators(nav_history):
    nav_history = nav_history.copy()
    nav_history["date"] = pd.to_datetime(nav_history["date"])
    nav_history["nav"] = pd.to_numeric(nav_history["nav"])
    sort_columns = ["date"]

    if "fund_name" in nav_history.columns:
        sort_columns = ["fund_name", "date"]

    nav_history = nav_history.sort_values(sort_columns).reset_index(drop=True)
    group_columns = ["fund_name"] if "fund_name" in nav_history.columns else None

    if group_columns:
        nav_groups = nav_history.groupby(group_columns, group_keys=False)["nav"]
        nav_history["ma_50"] = nav_groups.transform(lambda nav: nav.rolling(window=50).mean())
        nav_history["ma_200"] = nav_groups.transform(lambda nav: nav.rolling(window=200).mean())
        nav_history["drawdown_pct"] = nav_groups.transform(lambda nav: (nav / nav.cummax() - 1) * 100)
    else:
        nav_history["ma_50"] = nav_history["nav"].rolling(window=50).mean()
        nav_history["ma_200"] = nav_history["nav"].rolling(window=200).mean()
        nav_history["drawdown_pct"] = (nav_history["nav"] / nav_history["nav"].cummax() - 1) * 100

    return nav_history


def calculate_days_to_new_high(nav_history):
    nav_history = nav_history.sort_values("date").reset_index(drop=True)

    if nav_history.empty:
        return {
            "average_days_to_new_high": None,
            "median_days_to_new_high": None,
            "longest_days_to_new_high": None,
            "current_days_since_high": None,
        }

    peak_nav = nav_history["nav"].iloc[0]
    peak_date = nav_history["date"].iloc[0]
    below_peak_start_date = None
    recovery_days = []

    for _, row in nav_history.iterrows():
        current_nav = row["nav"]
        current_date = row["date"]

        if current_nav > peak_nav:
            if below_peak_start_date is not None:
                recovery_days.append((current_date - below_peak_start_date).days)
                below_peak_start_date = None

            peak_nav = current_nav
            peak_date = current_date
        elif current_nav < peak_nav and below_peak_start_date is None:
            below_peak_start_date = current_date

    current_days_since_high = (nav_history["date"].iloc[-1] - peak_date).days

    if not recovery_days:
        return {
            "average_days_to_new_high": None,
            "median_days_to_new_high": None,
            "longest_days_to_new_high": None,
            "current_days_since_high": current_days_since_high,
        }

    recovery_days_series = pd.Series(recovery_days)

    return {
        "average_days_to_new_high": round(recovery_days_series.mean()),
        "median_days_to_new_high": round(recovery_days_series.median()),
        "longest_days_to_new_high": int(recovery_days_series.max()),
        "current_days_since_high": current_days_since_high,
    }


def calculate_peak_nav_stats(nav_history):
    nav_history = nav_history.sort_values("date").reset_index(drop=True)

    if nav_history.empty:
        return {
            "peak_nav": None,
            "peak_date": None,
            "latest_nav": None,
            "distance_from_peak_pct": None,
        }

    peak_row = nav_history.loc[nav_history["nav"].idxmax()]
    latest_row = nav_history.iloc[-1]
    distance_from_peak_pct = (latest_row["nav"] / peak_row["nav"] - 1) * 100

    return {
        "peak_nav": float(peak_row["nav"]),
        "peak_date": peak_row["date"],
        "latest_nav": float(latest_row["nav"]),
        "distance_from_peak_pct": float(round(distance_from_peak_pct, 2)),
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

