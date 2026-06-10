import pandas as pd


def calculate_cagr(start_value, end_value, start_date, end_date):
    years = (end_date - start_date).days / 365.25

    if years <= 0 or start_value <= 0:
        return None

    return ((end_value / start_value) ** (1 / years) - 1) * 100


def calculate_xirr(cashflows):
    if not cashflows:
        return None

    first_date = cashflows[0]["date"]

    def net_present_value(rate):
        total = 0

        for cashflow in cashflows:
            years = (cashflow["date"] - first_date).days / 365.25
            total += cashflow["amount"] / ((1 + rate) ** years)

        return total

    low_rate = -0.9999
    high_rate = 10
    low_value = net_present_value(low_rate)
    high_value = net_present_value(high_rate)

    if low_value * high_value > 0:
        return None

    for _ in range(100):
        mid_rate = (low_rate + high_rate) / 2
        mid_value = net_present_value(mid_rate)

        if abs(mid_value) < 0.0001:
            return mid_rate * 100

        if low_value * mid_value < 0:
            high_rate = mid_rate
            high_value = mid_value
        else:
            low_rate = mid_rate
            low_value = mid_value

    return mid_rate * 100


def get_nearest_nav_on_or_after(nav_history, target_date):
    available_nav = nav_history[nav_history["date"] >= target_date]

    if available_nav.empty:
        return None

    return available_nav.sort_values("date").iloc[0]


def calculate_lumpsum_returns(nav_history, amount, n_years):
    results = []
    value_history = []
    excluded_funds = []

    for fund_name, fund_nav in nav_history.groupby("fund_name"):
        fund_nav = fund_nav.sort_values("date").reset_index(drop=True)
        fund_start_date = fund_nav["date"].min()
        fund_end_date = fund_nav["date"].max()
        fund_age_years = (fund_end_date - fund_start_date).days / 365.25

        if fund_age_years < n_years:
            excluded_funds.append({
                "fund_name": fund_name,
                "available_years": fund_age_years
            })
            continue

        target_start_date = fund_end_date - pd.DateOffset(years=n_years)
        start_nav_row = get_nearest_nav_on_or_after(fund_nav, target_start_date)

        if start_nav_row is None:
            excluded_funds.append({
                "fund_name": fund_name,
                "available_years": fund_age_years
            })
            continue

        latest_nav_row = fund_nav.iloc[-1]
        units = amount / start_nav_row["nav"]
        current_value = units * latest_nav_row["nav"]
        gain_loss = current_value - amount
        absolute_return_pct = (gain_loss / amount) * 100
        cagr_pct = calculate_cagr(
            amount,
            current_value,
            start_nav_row["date"],
            latest_nav_row["date"]
        )

        results.append({
            "Fund Name": fund_name,
            "Start Date": start_nav_row["date"].date(),
            "End Date": latest_nav_row["date"].date(),
            "Total Invested": amount,
            "Current Value": current_value,
            "Gain / Loss": gain_loss,
            "Absolute Return (%)": absolute_return_pct,
            "CAGR (%)": cagr_pct,
        })

        fund_value_history = fund_nav[fund_nav["date"] >= start_nav_row["date"]].copy()
        fund_value_history["fund_name"] = fund_name
        fund_value_history["investment_value"] = fund_value_history["nav"] * units
        fund_value_history["total_invested"] = amount
        value_history.append(
            fund_value_history[["date", "fund_name", "investment_value", "total_invested"]]
        )

    return _build_output(results, value_history, excluded_funds)


def calculate_sip_returns(nav_history, monthly_amount, n_years):
    results = []
    value_history = []
    excluded_funds = []

    for fund_name, fund_nav in nav_history.groupby("fund_name"):
        fund_nav = fund_nav.sort_values("date").reset_index(drop=True)
        fund_start_date = fund_nav["date"].min()
        fund_end_date = fund_nav["date"].max()
        fund_age_years = (fund_end_date - fund_start_date).days / 365.25

        if fund_age_years < n_years:
            excluded_funds.append({
                "fund_name": fund_name,
                "available_years": fund_age_years
            })
            continue

        target_start_date = fund_end_date - pd.DateOffset(years=n_years)
        first_sip_row = get_nearest_nav_on_or_after(fund_nav, target_start_date)

        if first_sip_row is None:
            excluded_funds.append({
                "fund_name": fund_name,
                "available_years": fund_age_years
            })
            continue

        sip_dates = [
            first_sip_row["date"] + pd.DateOffset(months=month_number)
            for month_number in range(n_years * 12)
        ]

        purchases = []

        for sip_date in sip_dates:
            purchase_nav_row = get_nearest_nav_on_or_after(fund_nav, sip_date)

            if purchase_nav_row is None:
                continue

            purchases.append({
                "date": purchase_nav_row["date"],
                "units": monthly_amount / purchase_nav_row["nav"],
                "amount": monthly_amount,
            })

        if not purchases:
            excluded_funds.append({
                "fund_name": fund_name,
                "available_years": fund_age_years
            })
            continue

        purchases_df = pd.DataFrame(purchases)
        latest_nav_row = fund_nav.iloc[-1]
        total_units = purchases_df["units"].sum()
        total_invested = purchases_df["amount"].sum()
        current_value = total_units * latest_nav_row["nav"]
        gain_loss = current_value - total_invested
        absolute_return_pct = (gain_loss / total_invested) * 100
        cashflows = [
            {
                "date": row["date"],
                "amount": -row["amount"]
            }
            for _, row in purchases_df.iterrows()
        ]
        cashflows.append({
            "date": latest_nav_row["date"],
            "amount": current_value
        })
        xirr_pct = calculate_xirr(cashflows)

        results.append({
            "Fund Name": fund_name,
            "Start Date": purchases_df["date"].min().date(),
            "End Date": latest_nav_row["date"].date(),
            "Total Invested": total_invested,
            "Current Value": current_value,
            "Gain / Loss": gain_loss,
            "Absolute Return (%)": absolute_return_pct,
            "XIRR (%)": xirr_pct,
            "Installments": len(purchases_df),
        })

        fund_value_history = fund_nav[fund_nav["date"] >= purchases_df["date"].min()].copy()
        fund_value_history["fund_name"] = fund_name
        fund_value_history["investment_value"] = 0.0
        fund_value_history["total_invested"] = 0.0

        for idx, row in fund_value_history.iterrows():
            completed_purchases = purchases_df[purchases_df["date"] <= row["date"]]
            cumulative_units = completed_purchases["units"].sum()
            cumulative_invested = completed_purchases["amount"].sum()

            fund_value_history.at[idx, "investment_value"] = cumulative_units * row["nav"]
            fund_value_history.at[idx, "total_invested"] = cumulative_invested

        value_history.append(
            fund_value_history[["date", "fund_name", "investment_value", "total_invested"]]
        )

    return _build_output(results, value_history, excluded_funds)


def _build_output(results, value_history, excluded_funds):
    if results:
        results_df = pd.DataFrame(results)
    else:
        results_df = pd.DataFrame()

    if value_history:
        value_history_df = pd.concat(value_history, ignore_index=True)
    else:
        value_history_df = pd.DataFrame()

    return results_df, value_history_df, excluded_funds
