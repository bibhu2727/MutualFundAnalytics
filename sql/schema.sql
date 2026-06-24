-- SQLite Star Schema Definition for Mutual Fund Analytics
-- Designed for fintech analytics and data warehousing.

-- Drop tables in order of dependencies to avoid foreign key constraint check errors
DROP TABLE IF EXISTS fact_nav;
DROP TABLE IF EXISTS fact_transactions;
DROP TABLE IF EXISTS fact_performance;
DROP TABLE IF EXISTS fact_aum;
DROP TABLE IF EXISTS dim_fund;
DROP TABLE IF EXISTS dim_date;

-- 1. dim_fund: Mutual Fund Scheme dimension containing metadata
CREATE TABLE dim_fund (
    scheme_code INTEGER PRIMARY KEY,
    fund_name TEXT NOT NULL,
    amc TEXT NOT NULL,
    category TEXT NOT NULL,
    benchmark TEXT NOT NULL
);

-- 2. dim_date: Date dimension to facilitate robust date-intelligence queries
CREATE TABLE dim_date (
    date TEXT PRIMARY KEY, -- Format: YYYY-MM-DD
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend INTEGER NOT NULL -- 1 for True, 0 for False
);

-- 3. fact_nav: Fact table containing daily NAV records (historical)
CREATE TABLE fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER NOT NULL,
    date TEXT NOT NULL,
    nav REAL NOT NULL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund (scheme_code),
    FOREIGN KEY (date) REFERENCES dim_date (date)
);

-- 4. fact_transactions: Fact table recording investor buy/sell events
CREATE TABLE fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    scheme_code INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL, -- SIP, Lumpsum, Redemption
    amount REAL NOT NULL,
    units REAL NOT NULL,
    investor_name TEXT NOT NULL,
    kyc_status TEXT NOT NULL,       -- Verified, Pending, Failed
    state TEXT NOT NULL,            -- Investor geographic state
    FOREIGN KEY (scheme_code) REFERENCES dim_fund (scheme_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date (date)
);

-- 5. fact_performance: Fact table tracking returns and cost ratios
CREATE TABLE fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER NOT NULL,
    returns_1y REAL,
    returns_3y REAL,
    returns_5y REAL,
    expense_ratio REAL NOT NULL,    -- Expressed as numeric percentage (e.g. 1.25 for 1.25%)
    sharpe_ratio REAL,
    sortino_ratio REAL,
    FOREIGN KEY (scheme_code) REFERENCES dim_fund (scheme_code)
);

-- 6. fact_aum: Fact table for historical or snapshot AUM
CREATE TABLE fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER NOT NULL,
    date TEXT NOT NULL,             -- Date of snapshot (YYYY-MM-DD)
    aum_cr REAL NOT NULL,           -- AUM in Crores
    FOREIGN KEY (scheme_code) REFERENCES dim_fund (scheme_code),
    FOREIGN KEY (date) REFERENCES dim_date (date)
);
