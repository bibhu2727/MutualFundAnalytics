-- =====================================================================
-- MUTUAL FUND ANALYTICS - DAY 2: ANALYTICAL SQL QUERIES
-- Database Engine: SQLite
-- Designed by: Senior Fintech Data Analyst & Data Engineer
-- =====================================================================

-- ---------------------------------------------------------------------
-- Query 1: Top 5 Funds by Assets Under Management (AUM)
-- Purpose: Identify the largest mutual funds in the portfolio by their current assets.
-- Expected Business Insight: Helps marketing and distribution teams identify the most popular and dominant schemes in our product offering.
-- ---------------------------------------------------------------------
SELECT 
    df.scheme_code,
    df.fund_name,
    df.amc,
    fa.aum_cr
FROM fact_aum fa
JOIN dim_fund df ON fa.scheme_code = df.scheme_code
ORDER BY fa.aum_cr DESC
LIMIT 5;


-- ---------------------------------------------------------------------
-- Query 2: Average Net Asset Value (NAV) per Month for Each Fund
-- Purpose: Calculate the monthly average NAV for each scheme to observe growth trends.
-- Expected Business Insight: Provides portfolio managers with smoothed historical trendlines, filtering out short-term market noise.
-- ---------------------------------------------------------------------
SELECT 
    df.fund_name,
    dd.year,
    dd.month_name,
    ROUND(AVG(fn.nav), 4) AS avg_nav
FROM fact_nav fn
JOIN dim_fund df ON fn.scheme_code = df.scheme_code
JOIN dim_date dd ON fn.date = dd.date
GROUP BY df.fund_name, dd.year, dd.month, dd.month_name
ORDER BY df.fund_name, dd.year, dd.month;


-- ---------------------------------------------------------------------
-- Query 3: SIP Year-over-Year (YoY) Inflow Growth
-- Purpose: Compare total SIP investment inflows between consecutive fiscal/calendar years.
-- Expected Business Insight: Highlights whether recurring retail investment activity is growing, signaling stable capital inflows.
-- ---------------------------------------------------------------------
WITH AnnualSIP AS (
    SELECT 
        dd.year,
        SUM(ft.amount) AS total_sip_amount
    FROM fact_transactions ft
    JOIN dim_date dd ON ft.transaction_date = dd.date
    WHERE ft.transaction_type = 'SIP'
    GROUP BY dd.year
)
SELECT 
    curr.year AS current_year,
    ROUND(curr.total_sip_amount, 2) AS current_year_amount,
    prev.year AS previous_year,
    ROUND(prev.total_sip_amount, 2) AS previous_year_amount,
    CASE 
        WHEN prev.total_sip_amount IS NULL THEN 'N/A'
        ELSE ROUND(((curr.total_sip_amount - prev.total_sip_amount) / prev.total_sip_amount) * 100.0, 2) || '%'
    END AS yoy_growth_pct
FROM AnnualSIP curr
LEFT JOIN AnnualSIP prev ON curr.year = prev.year + 1
ORDER BY curr.year;


-- ---------------------------------------------------------------------
-- Query 4: Total Transaction Count and Inflows by Investor State
-- Purpose: Analyze the geographic distribution of retail investor activity.
-- Expected Business Insight: Pinpoints high-net-worth states for localized marketing campaigns and distribution channel prioritization.
-- ---------------------------------------------------------------------
SELECT 
    ft.state,
    COUNT(ft.transaction_id) AS total_transactions,
    ROUND(SUM(ft.amount), 2) AS total_invested_amount,
    ROUND(AVG(ft.amount), 2) AS avg_transaction_amount
FROM fact_transactions ft
GROUP BY ft.state
ORDER BY total_invested_amount DESC;


-- ---------------------------------------------------------------------
-- Query 5: Funds with Expense Ratio < 1.00%
-- Purpose: Filter low-cost schemes matching investor preferences for passive/economical direct plans.
-- Expected Business Insight: Assists product managers in curating low-cost investment themes for risk-averse, cost-conscious retail clients.
-- ---------------------------------------------------------------------
SELECT 
    df.scheme_code,
    df.fund_name,
    df.amc,
    fp.expense_ratio
FROM fact_performance fp
JOIN dim_fund df ON fp.scheme_code = df.scheme_code
WHERE fp.expense_ratio < 1.00
ORDER BY fp.expense_ratio ASC;


-- ---------------------------------------------------------------------
-- Query 6: Highest Return Funds (Ranked by 5-Year CAGR Performance)
-- Purpose: Identify top-performing schemes over a long-term horizon.
-- Expected Business Insight: Provides fund advisors with the historical winners to construct growth portfolios for long-term clients.
-- ---------------------------------------------------------------------
SELECT 
    df.fund_name,
    df.category,
    fp.returns_5y AS returns_5y_pct,
    fp.returns_3y AS returns_3y_pct,
    fp.returns_1y AS returns_1y_pct
FROM fact_performance fp
JOIN dim_fund df ON fp.scheme_code = df.scheme_code
ORDER BY fp.returns_5y DESC;


-- ---------------------------------------------------------------------
-- Query 7: Most Popular Asset Management Companies (AMCs)
-- Purpose: Measure concentration of assets under management across fund houses.
-- Expected Business Insight: AMC concentration analysis shows where the firm has the strongest alliances and vendor partnerships.
-- ---------------------------------------------------------------------
SELECT 
    df.amc,
    COUNT(DISTINCT df.scheme_code) AS total_schemes_listed,
    ROUND(SUM(fa.aum_cr), 2) AS total_aum_cr
FROM dim_fund df
JOIN fact_aum fa ON df.scheme_code = fa.scheme_code
GROUP BY df.amc
ORDER BY total_aum_cr DESC;


-- ---------------------------------------------------------------------
-- Query 8: Monthly Transaction Trends by Volume and Amount
-- Purpose: Detect cyclical/seasonal movements in transaction volumes.
-- Expected Business Insight: Helps operational staff budget transaction loads and predicts capital call capacities.
-- ---------------------------------------------------------------------
SELECT 
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(ft.transaction_id) AS transaction_count,
    ROUND(SUM(ft.amount), 2) AS total_amount_invested,
    ROUND(SUM(CASE WHEN ft.transaction_type = 'SIP' THEN ft.amount ELSE 0 END), 2) AS sip_amount,
    ROUND(SUM(CASE WHEN ft.transaction_type = 'Lumpsum' THEN ft.amount ELSE 0 END), 2) AS lumpsum_amount,
    ROUND(SUM(CASE WHEN ft.transaction_type = 'Redemption' THEN ft.amount ELSE 0 END), 2) AS redemption_amount
FROM fact_transactions ft
JOIN dim_date dd ON ft.transaction_date = dd.date
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;


-- ---------------------------------------------------------------------
-- Query 9: Category-wise Average Performance and Costs
-- Purpose: Evaluate overall returns and costs at the category/asset class level.
-- Expected Business Insight: Helps advisors construct multi-asset models and evaluate large-cap category benchmarks.
-- ---------------------------------------------------------------------
SELECT 
    df.category,
    COUNT(df.scheme_code) AS fund_count,
    ROUND(AVG(fp.returns_5y), 2) AS avg_5y_return,
    ROUND(AVG(fp.returns_3y), 2) AS avg_3y_return,
    ROUND(AVG(fp.expense_ratio), 2) AS avg_expense_ratio
FROM dim_fund df
JOIN fact_performance fp ON df.scheme_code = fp.scheme_code
GROUP BY df.category;


-- ---------------------------------------------------------------------
-- Query 10: Inflow vs Outflow and Net Flow Analysis per Scheme
-- Purpose: Analyze liquidity and net capital flows (inflows vs redemptions) for each mutual fund.
-- Expected Business Insight: Identifies structural capital flights or popular funds experiencing high net positive flows.
-- ---------------------------------------------------------------------
SELECT 
    df.fund_name,
    ROUND(SUM(CASE WHEN ft.transaction_type IN ('SIP', 'Lumpsum') THEN ft.amount ELSE 0 END), 2) AS total_inflows,
    ROUND(SUM(CASE WHEN ft.transaction_type = 'Redemption' THEN ft.amount ELSE 0 END), 2) AS total_outflows,
    ROUND(SUM(CASE WHEN ft.transaction_type IN ('SIP', 'Lumpsum') THEN ft.amount ELSE -ft.amount END), 2) AS net_flow,
    ROUND((SUM(CASE WHEN ft.transaction_type = 'Redemption' THEN ft.amount ELSE 0 END) / 
           SUM(CASE WHEN ft.transaction_type IN ('SIP', 'Lumpsum') THEN ft.amount ELSE 0.0001 END)) * 100.0, 2) AS redemption_rate_pct
FROM fact_transactions ft
JOIN dim_fund df ON ft.scheme_code = df.scheme_code
GROUP BY df.fund_name
ORDER BY net_flow DESC;
