import plotly.graph_objects as go
#import ipywidgets as widgets
from IPython.display import display, clear_output
#from ipywidgets import Output
import pandas as pd
import plotly.express as px

def get_fund_colors(funds):
    colors = px.colors.qualitative.Plotly
    return {
        fund: colors[idx % len(colors)]
        for idx, fund in enumerate(sorted(funds))
    }

# Plot NAV over time
def plot_nav(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['nav'],
        mode='lines',
        name='NAV',
        line=dict(color='cyan')
    ))
    fig.update_layout(
        title='📈 NAV Over Time',
        xaxis_title='Date',
        yaxis_title='NAV',
        template='plotly_dark'
    )
    return fig

#Plot CAGR distribution
#Rolling cagr plot for multiple funds
def plot_rolling_cagr_mul_mf(df, n):
    if df['fund_name'].nunique() == 1:
      col_cagr = f'cagr_{n}_years'
      fig = go.Figure()
      fig.add_trace(go.Scatter(
          x=df['current_date'],
          y=df[col_cagr],
          mode='lines',
          name=f'{n}Y Rolling CAGR',
          line=dict(color='purple')
      ))

      p10 = df[col_cagr].quantile(0.10)
      p50 = df[col_cagr].median()
      p90 = df[col_cagr].quantile(0.90)
    

      # Percentile bands
      fig.add_hline(y=p10, line_dash='dot', line_color='red', annotation_text='10th percentile')
      fig.add_hline(y=p50, line_dash='dash', line_color='yellow', annotation_text='Median')
      fig.add_hline(y=p90, line_dash='dot', line_color='green', annotation_text='90th percentile')

      fig.update_layout(
          title=f'📉 Rolling {n}-Year CAGR',
          xaxis_title='Date',
          yaxis_title='CAGR (%)',
          template='plotly_dark'
      )
    else:
      col_cagr = f'cagr_{n}_years'
      fig = go.Figure()
      fund_colors = get_fund_colors(df['fund_name'].unique())

      # Loop over each fund
      for fund in df['fund_name'].unique():
          fund_df = df[df['fund_name'] == fund]

          fig.add_trace(go.Scatter(
              x=fund_df['current_date'],
              y=fund_df[col_cagr],
              mode='lines',
              name=fund,
              line=dict(color=fund_colors[fund])
          ))

      fig.update_layout(
          title=f'📉 Rolling {n}-Year CAGR',
          xaxis_title='Date',
          yaxis_title='CAGR (%)',
          template='plotly_dark',
          legend=dict(
              orientation="h",        # horizontal legend
              yanchor="top",
              y=-0.25,                # move below the chart
              xanchor="center",
              x=0.5
          )
      )


    return fig

#Rolling returns summary
def rolling_returns_summary(df, n):
    col_cagr = f'cagr_{n}_years'

    # Compute percentiles
    percentiles = df[col_cagr].quantile([0, 0.05, 0.10, 0.25, 0.5, 0.75, 0.90, 0.95, 1.0]).round(2) #.astype(int)

    # Construct summary DataFrame
    summary_df = pd.DataFrame({
        'fund_name': [df['fund_name'].iloc[0]],
        'start_date': [df['past_date'].min().date()],
        'end_date': [df['current_date'].max().date()],
        'metric': [f'{n}Y CAGR'],
        f'latest_{n}_year_cagr': [df[col_cagr].iloc[-1].round(2)],
        'mean': [round(df[col_cagr].mean(), 2)],
        'std_dev': [round(df[col_cagr].std(), 2)],
        'min': [percentiles.loc[0.00]],
        'p5': [percentiles.loc[0.05]],
        'p10': [percentiles.loc[0.10]],
        'p25': [percentiles.loc[0.25]],
        'median': [round(percentiles.loc[0.50], 2)],
        'p75': [percentiles.loc[0.75]],
        'p90': [percentiles.loc[0.90]],
        'p95': [percentiles.loc[0.95]],
        'max': [percentiles.loc[1.00]],
    }) 

    summary_df = summary_df.sort_values(by=f'median', ascending=False)
    return summary_df


# Returns Distribution Chart
def plot_boxplot(df, n, sort_by="returns"):
  col_cagr = f"cagr_{n}_years"

  stats = (
      df
      .groupby("fund")[col_cagr]
      .agg(
          median="median",
          q1=lambda x: x.quantile(0.25),
          q3=lambda x: x.quantile(0.75),
          min_return="min",
          max_return="max"
      )
      .reset_index()
  )

  stats["spread"] = stats["q3"] - stats["q1"]

  sort_options = {
      "returns": ("median", False),
      "spread": ("spread", True),
  }
  sort_column, sort_ascending = sort_options.get(sort_by, sort_options["returns"])
  fund_order = stats.sort_values(sort_column, ascending=sort_ascending)["fund"].tolist()
  fund_colors = get_fund_colors(df["fund"].unique())

  fig = px.box(
      df,
      x="fund",
      y=col_cagr,
      color="fund",
      points="outliers",
      title=f"Rolling {n}Y CAGR Distribution Across Funds",
      template="plotly_dark",
      category_orders={"fund": fund_order},
      color_discrete_map=fund_colors
  )

  fig.update_traces(
      boxmean=True,
      jitter=0.25,
      marker=dict(size=4, opacity=0.35)
  )

  fig.update_layout(
      height=550,
      width=900,
      title_x=0.5,
      showlegend=False,
      xaxis_title="",
      yaxis_title=col_cagr,
      font=dict(size=13),
      margin=dict(l=60, r=40, t=80, b=120)
  )

  fig.update_xaxes(
      tickangle=-25,
      showgrid=False
  )

  fig.update_yaxes(
      gridcolor="rgba(255,255,255,0.1)"
  )

  #Adding smart insights annotations
  best_median = stats.loc[stats["median"].idxmax()]
  most_consistent = stats.loc[stats["spread"].idxmin()]  

  annotation_text = (
      f"<b>Smart Insight</b><br>"
      f"Highest median return: {best_median['fund']} "
      f"({best_median['median']:.2f}%)<br>"
      f"Most consistent fund: {most_consistent['fund']} "
      f"(IQR: {most_consistent['spread']:.2f}%)"
  )

  fig.add_annotation(
      text=annotation_text,
      xref="paper",
      yref="paper",
      x=0.99,
      y=0.98,
      showarrow=False,
      align="left",
      bgcolor="rgba(20,20,20,0.85)",
      bordercolor="rgba(255,255,255,0.25)",
      borderwidth=1,
      font=dict(size=12, color="white")
  )
  #fig.show()
  return fig

# Risk - Returns Matrix
def plot_risk_return_matrix(df, n):
    df = df.copy()

    x_col = f"std_dev"
    y_col = f"median"

    x_mid = df[x_col].median()
    y_mid = df[y_col].median()
    fund_colors = get_fund_colors(df["fund_name"].unique())

    def get_quadrant(row):
        if row[x_col] <= x_mid and row[y_col] >= y_mid:
            return "Best Zone"
        elif row[x_col] > x_mid and row[y_col] >= y_mid:
            return "Aggressive"
        elif row[x_col] <= x_mid and row[y_col] < y_mid:
            return "Stable"
        else:
            return "Weak Zone"

    df["quadrant"] = df.apply(get_quadrant, axis=1)

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color="fund_name",
        symbol="quadrant",
        text=None,
        hover_name="fund_name",
        title=f"Risk - Return Matrix ({n}Y Rolling CAGR)",
        template="plotly_dark",
        color_discrete_map=fund_colors,
        symbol_map={
            "Best Zone": "star",
            "Aggressive": "triangle-up",
            "Stable": "line-ew",
            "Weak Zone": "x"
        }
    )

    fig.add_vline(x=x_mid, line_dash="dash", line_color="gray")
    fig.add_hline(y=y_mid, line_dash="dash", line_color="gray")

    fig.update_xaxes(range=[0, df[x_col].max() * 1.1])

    fig.update_yaxes(
        range=[min(0, df[y_col].min() * 1.1), df[y_col].max() * 1.1]
    )

    x_min = 0
    x_max = df[x_col].max() * 1.1

    y_min = 0
    y_max = df[y_col].max() * 1.1

    x_left = (x_min + x_mid) / 2
    x_right = (x_mid + x_max) / 2
    y_bottom = (y_min + y_mid) / 2
    y_top = (y_mid + y_max) / 2

    fig.add_annotation(x=x_left, y=y_top,
                      text="Low Risk<br>High Return<br><b>⭐ Best Zone</b>",
                      showarrow=False, font=dict(size=10, color="rgba(255,255,255,0.5)"))

    fig.add_annotation(x=x_right, y=y_top,
                      text="High Risk<br>High Return<br><b>🔺 Aggressive Zone</b>",
                      showarrow=False, font=dict(size=10, color="rgba(255,255,255,0.5)"))

    fig.add_annotation(x=x_left, y=y_bottom,
                      text="Low Risk<br>Low Return<br><b>➖ Stable Zone</b>",
                      showarrow=False, font=dict(size=10, color="rgba(255,255,255,0.5)"))

    fig.add_annotation(x=x_right, y=y_bottom,
                      text="High Risk<br>Low Return<br><b>❌ Weak Zone</b>",
                      showarrow=False, font=dict(size=10, color="rgba(255,255,255,0.5)"))

    fig.update_traces(
        marker=dict(
            size=14,
            opacity=0.85,
            line=dict(width=1, color="white")
        )
    )

    for trace in fig.data:
        if "Stable" in trace.name:
            trace.marker.line.color = trace.marker.color
            trace.marker.line.width = 3

    fig.update_xaxes(range=[x_min, x_max])
    fig.update_yaxes(range=[y_min, y_max])

    fig.update_traces(textposition="top center")

    fig.update_layout(
        xaxis_title="Risk: Volatility of Rolling CAGR",
        yaxis_title="Return: Median Rolling CAGR",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            title_text="Fund"
        )
    )

    return fig


def build_bar_chart_race(df, n_years, sample_frequency, max_funds):
    col_cagr = f"cagr_{n_years}_years"

    race_df = df.copy()
    race_df["current_date"] = pd.to_datetime(race_df["current_date"])

    frequency_map = {
        "Monthly": "M",
        "Quarterly": "Q",
        "Yearly": "Y",
    }

    race_df["period"] = (
        race_df["current_date"]
        .dt.to_period(frequency_map[sample_frequency])
        .dt.to_timestamp()
    )

    race_df = (
        race_df
        .sort_values("current_date")
        .groupby(["period", "fund"], as_index=False)
        .tail(1)
    )

    frame_dates = sorted(race_df["period"].unique())

    fund_colors = get_fund_colors(race_df["fund"].unique())

    def get_frame_data(frame_date):
        frame_df = race_df[race_df["period"] == frame_date]
        frame_df = frame_df.nlargest(max_funds, col_cagr)
        return frame_df.sort_values(col_cagr, ascending=True)

    first_frame = get_frame_data(frame_dates[0])

    x_min = min(0, race_df[col_cagr].min() * 1.15)
    x_max = max(0, race_df[col_cagr].max() * 1.15)

    fig = go.Figure(
        data=[
            go.Bar(
                x=first_frame[col_cagr],
                y=first_frame["fund"],
                orientation="h",
                marker_color=[fund_colors[fund] for fund in first_frame["fund"]],
                text=[f"{value:.2f}%" for value in first_frame[col_cagr]],
                textposition="outside",
            )
        ],
        layout=go.Layout(
            title=f"Rolling {n_years}Y CAGR Race",
            xaxis=dict(title="Rolling CAGR (%)", range=[x_min, x_max]),
            yaxis=dict(title="", automargin=True),
            template="plotly_dark",
            height=720,
            margin=dict(l=180, r=60, t=160, b=150),
            updatemenus=[
                {
                    "type": "buttons",
                    "showactive": False,
                    "direction": "left",
                    "x": 1,
                    "y": 1.18,
                    "xanchor": "right",
                    "yanchor": "top",
                    "buttons": [
                        {
                            "label": "▶",
                            "method": "animate",
                            "args": [
                                None,
                                {
                                    "frame": {"duration": 500, "redraw": True},
                                    "fromcurrent": True,
                                },
                            ],
                        },
                        {
                            "label": "⏸",
                            "method": "animate",
                            "args": [
                                [None],
                                {
                                    "frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                },
                            ],
                        },
                    ],
                }
            ],
        ),
    )

    fig.frames = [
        go.Frame(
            data=[
                go.Bar(
                    x=get_frame_data(frame_date)[col_cagr],
                    y=get_frame_data(frame_date)["fund"],
                    orientation="h",
                    marker_color=[
                        fund_colors[fund]
                        for fund in get_frame_data(frame_date)["fund"]
                    ],
                    text=[
                        f"{value:.2f}%"
                        for value in get_frame_data(frame_date)[col_cagr]
                    ],
                    textposition="outside",
                )
            ],
            name=str(pd.Timestamp(frame_date).date()),
            layout=go.Layout(
                title_text=(
                    f"Rolling {n_years}Y CAGR Race - "
                    f"{pd.Timestamp(frame_date).date()}"
                )
            ),
        )
        for frame_date in frame_dates
    ]

    fig.update_layout(
        sliders=[
            {
                "active": 0,
                "currentvalue": {"prefix": "Date: "},
                "pad": {"t": 60, "b": 20},
                "steps": [
                    {
                        "label": str(pd.Timestamp(frame_date).date()),
                        "method": "animate",
                        "args": [
                            [str(pd.Timestamp(frame_date).date())],
                            {
                                "frame": {"duration": 300, "redraw": True},
                                "mode": "immediate",
                            },
                        ],
                    }
                    for frame_date in frame_dates
                ],
            }
        ]
    )

    return fig
