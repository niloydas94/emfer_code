#@title Rolling Returns Calculation
import re

import pandas as pd
from bisect import bisect_right

# Function to find the nearest available NAV <= target date
def get_nearest_past_index(target_date, date_list):
    idx = bisect_right(date_list, target_date)
    return idx - 1 if idx > 0 else None

# Clean fund names by extracting the portion up to and including "fund"
def clean_fund_name(name):
    match = re.search(r"(.*?\bfund\b)", name, re.IGNORECASE)
    return match.group(1).strip() if match else name.strip()

# Main function to calculate rolling returns
def calculate_rolling_returns(df, n):
    # 1. Make sure data is sorted chronologically
    df = df.sort_values('date').reset_index(drop=True)

    # 2. Extract just the date and nav columns
    dates = df['date'].tolist()
    navs = df['nav'].tolist()

    rolling_cagr_list = []

    # 3. Loop through each date (starting from n_years onward)
    for i, row in df.iterrows():
        current_date = row['date']
        current_nav = row['nav']

        # Target date = n years back
        n_years_back = current_date - pd.DateOffset(years=n)

        # Find the nearest date <= n_years_back
        past_idx = get_nearest_past_index(n_years_back, dates)

        if past_idx is not None:
            past_nav = navs[past_idx]
            past_date = dates[past_idx]

            # Calculate CAGR
            cagr = (current_nav / past_nav) ** (1 / n) - 1

            rolling_cagr_list.append({
                'current_date': current_date,
                'past_date': past_date,
                f'cagr_{n}_years': cagr * 100,  # as %
                'current_nav' : current_nav,
                'past_nav': past_nav,
                'fund_name': row['fund_name'],
                'fund': clean_fund_name(row['fund_name'])
            })

    # 4. Convert to DataFrame
    df_rolling = pd.DataFrame(rolling_cagr_list)

    # Final sort
    df_rolling = df_rolling.sort_values('current_date').reset_index(drop=True)

    col_cagr = f'cagr_{n}_years'

    #p10 = df_rolling[col_cagr].quantile(0.10)
    #p50 = df_rolling[col_cagr].median()
    #p90 = df_rolling[col_cagr].quantile(0.90)

    return df_rolling







