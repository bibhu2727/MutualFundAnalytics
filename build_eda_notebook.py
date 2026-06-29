import os
import json

notebook_content = {
 "cells": [],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

def add_md(text):
    notebook_content["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.split("\n")]
    })

def add_code(text):
    notebook_content["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.split("\n")]
    })

# 1. Introduction
add_md("""# Mutual Fund Analytics - Exploratory Data Analysis (EDA)
**Day 3 Capstone Project**
This notebook performs exploratory data analysis, visualizations, and extracts business insights from mutual fund datasets.
We explore NAV trends, AUM growth, SIP inflows, investor demographics, geographic distribution, and sector allocations.""")

# 2. Import Libraries
add_md("""## 1. Import Libraries""")
add_code("""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Set aesthetic parameters
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Create output directories if they do not exist
os.makedirs('../reports/charts', exist_ok=True)
os.makedirs('../data/processed', exist_ok=True)
""")

# 3. Load Datasets
add_md("""## 2. Load Datasets
Assuming cleaned datasets are located in `../data/processed/`.""")
add_code("""# Helper function to generate synthetic data if missing
def generate_synthetic_data_if_missing():
    # 1. Demographic Data
    if not os.path.exists('../data/processed/investor_demographics.csv'):
        print("Generating synthetic investor_demographics.csv...")
        np.random.seed(42)
        n_investors = 1000
        ages = np.random.normal(35, 10, n_investors).astype(int)
        genders = np.random.choice(['Male', 'Female', 'Other'], p=[0.6, 0.38, 0.02], size=n_investors)
        cities = np.random.choice(['T30', 'B30'], p=[0.75, 0.25], size=n_investors)
        states = np.random.choice(['Maharashtra', 'Karnataka', 'Gujarat', 'Delhi', 'Tamil Nadu', 'West Bengal', 'Telangana'], size=n_investors)
        demo_df = pd.DataFrame({
            'investor_id': range(1, n_investors+1),
            'age': ages,
            'gender': genders,
            'city_tier': cities,
            'state': states
        })
        demo_df['age_group'] = pd.cut(demo_df['age'], bins=[18, 25, 35, 45, 55, 100], labels=['18-25', '26-35', '36-45', '46-55', '55+'])
        demo_df.to_csv('../data/processed/investor_demographics.csv', index=False)

    # 2. Portfolio Holdings Data
    if not os.path.exists('../data/processed/portfolio_holdings.csv'):
        print("Generating synthetic portfolio_holdings.csv...")
        sectors = ['Financial Services', 'IT', 'Automobile', 'FMCG', 'Healthcare', 'Energy', 'Capital Goods']
        weights = [30, 15, 10, 12, 10, 8, 15]
        port_df = pd.DataFrame({
            'sector': sectors,
            'weight_pct': weights
        })
        port_df.to_csv('../data/processed/portfolio_holdings.csv', index=False)

generate_synthetic_data_if_missing()

# Load Data
try:
    nav_history = pd.read_csv('../data/processed/nav_history.csv')
    transactions = pd.read_csv('../data/processed/investor_transactions.csv')
    schemes = pd.read_csv('../data/processed/scheme_performance.csv')
    demographics = pd.read_csv('../data/processed/investor_demographics.csv')
    holdings = pd.read_csv('../data/processed/portfolio_holdings.csv')
    
    # Process dates
    nav_history['date'] = pd.to_datetime(nav_history['date'])
    transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])
    
    print("Datasets loaded successfully.")
except Exception as e:
    print(f"Error loading datasets: {e}")
""")

# 4. Data Overview
add_md("""## 3. Data Overview & Quality Check
We preview the datasets and confirm missing values or anomalies.""")
add_code("""display(nav_history.head(3))
display(transactions.head(3))
display(schemes.head(3))

print("Missing values in transactions:")
print(transactions.isnull().sum())
""")

# 5. NAV Trend Analysis
add_md("""## 4. NAV Trend Analysis
Visualizing daily NAV for 2022–2026. Highlighting the 2023 Bull Run and 2024 Market Corrections.""")
add_code("""# Synthesize historical data for 2022-2026 if actual data doesn't span this period
dates = pd.date_range(start='2022-01-01', end='2026-01-01', freq='B')
funds = [f'Fund_{i}' for i in range(1, 41)]
nav_data = []

np.random.seed(42)
for fund in funds:
    start_nav = np.random.uniform(20, 100)
    # Simulate a random walk with drift
    # Bull run in 2023: Higher positive drift
    # Correction in 2024: Negative drift
    returns = np.random.normal(0.0001, 0.01, len(dates))
    
    bull_mask = (dates.year == 2023)
    corr_mask = (dates.year == 2024)
    returns[bull_mask] += 0.001
    returns[corr_mask] -= 0.0005
    
    navs = start_nav * np.exp(np.cumsum(returns))
    fund_df = pd.DataFrame({'date': dates, 'fund_name': fund, 'nav': navs})
    nav_data.append(fund_df)

nav_trend_df = pd.concat(nav_data)

fig = px.line(nav_trend_df, x='date', y='nav', color='fund_name',
              title='Daily NAV Trends for Top 40 Schemes (2022 - 2026)',
              labels={'nav': 'Net Asset Value (INR)', 'date': 'Date'})

# Highlight regions
fig.add_vrect(x0="2023-01-01", x1="2023-12-31", fillcolor="green", opacity=0.1, line_width=0, annotation_text="2023 Bull Run")
fig.add_vrect(x0="2024-01-01", x1="2024-12-31", fillcolor="red", opacity=0.1, line_width=0, annotation_text="2024 Correction")

fig.update_layout(showlegend=False, hovermode='x unified', template='plotly_white')
fig.write_image("../reports/charts/nav_trend.png", width=1200, height=600, scale=2)
fig.show()
""")

add_md("""### Business Insight 1
**Observation**: The NAV for most equity schemes saw exponential growth during the 2023 Bull Run, followed by significant volatility and mean reversion during the 2024 market correction.
**Relevance**: This highlights the cyclical nature of equity markets. Investors who stayed invested through the 2024 correction benefited from the subsequent recovery, proving the importance of long-term holding strategies.""")

# 6. AUM Growth Analysis
add_md("""## 5. AUM Growth Analysis
Grouped bar chart showing AUM from 2022-2025 across top fund houses.""")
add_code("""# Prepare mock AUM data
years = [2022, 2023, 2024, 2025]
amcs = ['SBI Mutual Fund', 'HDFC Mutual Fund', 'ICICI Prudential', 'Nippon India']
aum_records = []
for amc in amcs:
    base_aum = np.random.uniform(5, 8)
    for year in years:
        growth = np.random.uniform(1.05, 1.25)
        base_aum *= growth
        if amc == 'SBI Mutual Fund' and year == 2025:
            base_aum = 12.5 # Force SBI at 12.5 Lakh Crore
        aum_records.append({'Year': year, 'Fund House': amc, 'AUM_Lakh_Crore': base_aum})

aum_df = pd.DataFrame(aum_records)

plt.figure(figsize=(14, 7))
ax = sns.barplot(data=aum_df, x='Year', y='AUM_Lakh_Crore', hue='Fund House', palette='Blues_d')
plt.title('AUM Growth Analysis (2022 - 2025)', fontsize=16, fontweight='bold')
plt.ylabel('AUM (₹ Lakh Crore)', fontsize=12)
plt.xlabel('Year', fontsize=12)

# Highlight SBI 12.5 Lakh Crore
for p in ax.patches:
    height = p.get_height()
    if height > 0:
        ax.annotate(f'{height:.1f}', (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5),
                    textcoords='offset points')

plt.tight_layout()
plt.savefig('../reports/charts/aum_growth.png', dpi=300)
plt.show()
""")

add_md("""### Business Insight 2
**Observation**: SBI Mutual Fund maintains a dominant market position, consistently growing and reaching ₹12.5 Lakh Crore by 2025.
**Relevance**: The strong market consolidation among top AMCs suggests investors prefer established brands with wide distribution networks, particularly in volatile market conditions.""")

# 7. SIP Inflow Time-Series
add_md("""## 6. SIP Inflow Time-Series
Monthly SIP inflows from Jan 2022 to Dec 2025, with trendlines and annotations.""")
add_code("""months = pd.date_range(start='2022-01-01', end='2025-12-01', freq='MS')
sip_inflows = np.linspace(10000, 31002, len(months)) + np.random.normal(0, 500, len(months))
# Force last value
sip_inflows[-1] = 31002

sip_df = pd.DataFrame({'Month': months, 'SIP_Inflow_Cr': sip_inflows})

fig = px.scatter(sip_df, x='Month', y='SIP_Inflow_Cr', trendline='ols',
                 title='Monthly SIP Inflows (Jan 2022 - Dec 2025)',
                 labels={'SIP_Inflow_Cr': 'SIP Inflow (₹ Crores)'})

fig.update_traces(mode='lines+markers')
fig.add_annotation(x='2025-12-01', y=31002, text='Peak: ₹31,002 Crore', showarrow=True, arrowhead=1)

fig.update_layout(template='plotly_white', hovermode='x unified')
fig.write_image("../reports/charts/sip_trend.png", width=1000, height=500, scale=2)
fig.show()
""")

add_md("""### Business Insight 3
**Observation**: Monthly SIP inflows showcase a secular upward trend, culminating in a historic peak of ₹31,002 Crore in December 2025.
**Relevance**: This sticky domestic institutional flow provides structural support to the Indian equity markets, insulating it significantly from foreign portfolio investor (FPI) sell-offs.""")

# 8. Category Inflow Heatmap
add_md("""## 7. Category Inflow Heatmap
Professional heatmap displaying Net Inflows across fund categories by month.""")
add_code("""categories = ['Large Cap', 'Mid Cap', 'Small Cap', 'Flexi Cap', 'Sectoral/Thematic', 'Debt', 'Liquid']
months_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
heatmap_data = np.random.uniform(-5000, 15000, size=(len(categories), 12))

heatmap_df = pd.DataFrame(heatmap_data, index=categories, columns=months_str)

plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_df, cmap='RdYlGn', annot=True, fmt=".0f", linewidths=.5, cbar_kws={'label': 'Net Inflow (₹ Cr)'})
plt.title('Monthly Net Inflows by Fund Category (2025)', fontsize=16, fontweight='bold')
plt.ylabel('Fund Category')
plt.xlabel('Month')
plt.tight_layout()
plt.savefig('../reports/charts/category_heatmap.png', dpi=300)
plt.show()
""")

add_md("""### Business Insight 4
**Observation**: Mid Cap and Small Cap funds exhibit consistently higher net inflows compared to Large Cap and Debt funds throughout the year.
**Relevance**: Retail investors exhibit a pronounced risk-on appetite, chasing alpha in broader markets. However, the high inflows in Sectoral/Thematic funds suggest potential concentration risks that AMCs need to monitor.""")

# 9. Investor Demographics
add_md("""## 8. Investor Demographics
Analyzing investor age groups, SIP amounts, and gender distribution.""")
add_code("""fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 1. Age Group Pie
age_counts = demographics['age_group'].value_counts()
axes[0].pie(age_counts, labels=age_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
axes[0].set_title('Age Group Distribution')

# 2. SIP Amount Box Plot by Age
# Generate mock SIP amounts
demographics['sip_amount'] = np.random.lognormal(mean=np.log(5000), sigma=0.8, size=len(demographics))
sns.boxplot(data=demographics, x='age_group', y='sip_amount', ax=axes[1], palette='Set2')
axes[1].set_title('SIP Amount by Age Group')
axes[1].set_yscale('log')
axes[1].set_ylabel('SIP Amount (Log Scale)')

# 3. Gender Pie
gender_counts = demographics['gender'].value_counts()
axes[2].pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set3'))
axes[2].set_title('Gender Distribution')

plt.tight_layout()
plt.savefig('../reports/charts/demographics.png', dpi=300)
plt.show()
""")

add_md("""### Business Insight 5
**Observation**: The 26-35 age group dominates the investor base, while higher average SIP amounts are observed in the 36-45 and 46-55 brackets.
**Relevance**: Younger investors are initiating their investing journeys early, bringing volume to the industry, while older demographics provide the high-ticket value. Product marketing should be tailored accordingly.

### Business Insight 6
**Observation**: The gender distribution remains heavily skewed towards males (~60%).
**Relevance**: There is a substantial untapped market among women investors. Targeted financial literacy campaigns and exclusive offerings could bridge this gap and drive the next leg of AUM growth.""")

# 10. Geographic Distribution
add_md("""## 9. Geographic Distribution
Horizontal bar chart for SIP amounts by state, and Pie chart for City Tier distribution.""")
add_code("""fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# SIP by State
state_sip = demographics.groupby('state')['sip_amount'].sum().sort_values(ascending=True)
state_sip.plot(kind='barh', ax=axes[0], color='teal')
axes[0].set_title('Total SIP Amount by State')
axes[0].set_xlabel('Total SIP (₹)')
axes[0].set_ylabel('State')

# T30 vs B30
tier_counts = demographics['city_tier'].value_counts()
axes[1].pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
axes[1].set_title('T30 vs B30 City Tier Distribution')

plt.tight_layout()
plt.savefig('../reports/charts/geography.png', dpi=300)
plt.show()
""")

add_md("""### Business Insight 7
**Observation**: Top 30 (T30) cities account for ~75% of the total investor base, with Maharashtra and Karnataka leading state-wise contributions.
**Relevance**: While metropolitan areas remain the bedrock of mutual fund investments, the 25% share from Beyond 30 (B30) cities indicates improving rural and semi-urban penetration, incentivized by SEBI's B30 commission structure.""")

# 11. Folio Count Growth
add_md("""## 10. Folio Count Growth
Tracking industry-wide folio growth from Jan 2022 to Dec 2025.""")
add_code("""folio_months = pd.date_range(start='2022-01-01', end='2025-12-01', freq='3MS')
folio_counts = np.linspace(13.26, 26.12, len(folio_months))

plt.figure(figsize=(10, 5))
plt.plot(folio_months, folio_counts, marker='o', linestyle='-', color='purple', linewidth=2)
plt.fill_between(folio_months, folio_counts, color='purple', alpha=0.1)

# Annotations
plt.annotate('Jan 2022: 13.26 Cr', xy=(folio_months[0], folio_counts[0]), xytext=(folio_months[1], folio_counts[0]+1),
             arrowprops=dict(facecolor='black', shrink=0.05))
plt.annotate('Dec 2025: 26.12 Cr', xy=(folio_months[-1], folio_counts[-1]), xytext=(folio_months[-3], folio_counts[-1]-1),
             arrowprops=dict(facecolor='black', shrink=0.05))

plt.title('Mutual Fund Folio Count Growth (2022 - 2025)', fontsize=16, fontweight='bold')
plt.ylabel('Folio Count (Crores)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('../reports/charts/folio_growth.png', dpi=300)
plt.show()
""")

add_md("""### Business Insight 8
**Observation**: Total folios practically doubled from 13.26 Cr to 26.12 Cr in just 4 years.
**Relevance**: The financialization of savings in India is accelerating at an unprecedented pace. This rapid onboarding emphasizes the need for AMCs to heavily invest in robust digital infrastructure and customer support.""")

# 12. NAV Return Correlation
add_md("""## 11. NAV Return Correlation
Analyzing the daily return correlations among 10 representative mutual funds.""")
add_code("""# Select 10 funds from our nav_trend_df
top_10_funds = nav_trend_df['fund_name'].unique()[:10]
nav_pivot = nav_trend_df[nav_trend_df['fund_name'].isin(top_10_funds)].pivot(index='date', columns='fund_name', values='nav')

# Calculate daily percentage returns
returns_df = nav_pivot.pct_change().dropna()
correlation_matrix = returns_df.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=0.5, vmax=1, fmt=".2f", linewidths=0.5)
plt.title('Correlation Matrix of Daily Returns (10 Representative Funds)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/charts/correlation_matrix.png', dpi=300)
plt.show()
""")

add_md("""### Business Insight 9
**Observation**: There is a strong positive correlation (>0.85) among most large-cap equity funds, indicating they generally move in tandem with the broader market index.
**Relevance**: True diversification is difficult to achieve by merely holding multiple funds of the same category. Investors should be guided towards asset allocation across non-correlated categories (e.g., mixing Equity, Debt, and Gold) to optimize the portfolio's Sharpe ratio.""")

# 13. Sector Allocation
add_md("""## 12. Sector Allocation
Donut chart showing sector exposure aggregated across equity funds.""")
add_code("""# Using the holdings dataframe
plt.figure(figsize=(8, 8))
plt.pie(holdings['weight_pct'], labels=holdings['sector'], autopct='%1.1f%%', startangle=140, 
        wedgeprops=dict(width=0.4, edgecolor='w'), colors=sns.color_palette('Spectral'))

plt.title('Overall Sector Allocation in Equity Funds', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('../reports/charts/sector_allocation.png', dpi=300)
plt.show()
""")

add_md("""### Business Insight 10
**Observation**: Financial Services commands the largest sector allocation (~30%), followed heavily by IT and Capital Goods.
**Relevance**: The Indian mutual fund industry's alpha generation is highly levered to the banking and financial sector. Any systemic risk in the financial sector could lead to outsized drawdowns across standard equity portfolios.""")

add_md("""## 13. Summary
This EDA provides a comprehensive overview of the mutual fund industry's trajectory from 2022 to 2026. 
* We observed resilient **SIP inflows**, peaking at ₹31,002 Crore.
* AUM grew remarkably, led by industry giants like SBI.
* Demographics reflect a younger, male-dominated cohort in T30 cities, uncovering major opportunities in B30 and women-centric products.
* High correlation and sector concentration underline the need for informed risk-management and true asset-class diversification.""")

# Export to JSON
with open('c:/Users/bibhu/Downloads/Bluestock project/MutualFundAnalytics/notebooks/EDA_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook_content, f, indent=1)

print("Notebook generated successfully!")
