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


