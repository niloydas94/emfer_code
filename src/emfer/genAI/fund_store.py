# Fund Store
def create_fund_store(df_rolling_returns, df_summary):
    fund_store = {}
    for fund in df_rolling_returns['fund_name'].unique():
        fund_store[fund] = {
            'rolling_nav_cagr': df_rolling_returns[df_rolling_returns['fund_name'] == fund],
            'summary': df_summary[df_summary['fund_name'] == fund]
        }
    return fund_store

# Building RAG context
def build_rag_context(fund_store):
    context_parts = []

    for fund_name, data in fund_store.items():
        rolling_nav_cagr = data['rolling_nav_cagr']
        summary = data['summary']

        context_parts.append(f"""
                            Fund Name: {fund_name}
                            
                            Summary:
                            {summary.to_string(index=False)}

                            Rolling NAV and CAGR Analysis:
                            {rolling_nav_cagr.to_string(index=False)}
                            """)

    return "\n\n---\n\n".join(context_parts)
