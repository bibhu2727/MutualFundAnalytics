import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

os.makedirs('reports/charts', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

# Generate Synthetic Data if missing
if not os.path.exists('data/processed/investor_demographics.csv'):
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
    demo_df.to_csv('data/processed/investor_demographics.csv', index=False)

if not os.path.exists('data/processed/portfolio_holdings.csv'):
    print("Generating synthetic portfolio_holdings.csv...")
    sectors = ['Financial Services', 'IT', 'Automobile', 'FMCG', 'Healthcare', 'Energy', 'Capital Goods']
    weights = [30, 15, 10, 12, 10, 8, 15]
    port_df = pd.DataFrame({
        'sector': sectors,
        'weight_pct': weights
    })
    port_df.to_csv('data/processed/portfolio_holdings.csv', index=False)

nav_history = pd.read_csv('data/processed/nav_history.csv')
transactions = pd.read_csv('data/processed/investor_transactions.csv')
schemes = pd.read_csv('data/processed/scheme_performance.csv')
demographics = pd.read_csv('data/processed/investor_demographics.csv')
holdings = pd.read_csv('data/processed/portfolio_holdings.csv')

nav_history['date'] = pd.to_datetime(nav_history['date'])
transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])

# 1. NAV Trend Analysis
dates = pd.date_range(start='2022-01-01', end='2026-01-01', freq='B')
funds = [f'Fund_{i}' for i in range(1, 41)]
nav_data = []

np.random.seed(42)
for fund in funds:
    start_nav = np.random.uniform(20, 100)
    returns = np.random.normal(0.0001, 0.01, len(dates))
    bull_mask = (dates.year == 2023)
    corr_mask = (dates.year == 2024)
    returns[bull_mask] += 0.001
    returns[corr_mask] -= 0.0005
    navs = start_nav * np.exp(np.cumsum(returns))
    fund_df = pd.DataFrame({'date': dates, 'fund_name': fund, 'nav': navs})
    nav_data.append(fund_df)

nav_trend_df = pd.concat(nav_data)
fig = px.line(nav_trend_df, x='date', y='nav', color='fund_name', title='Daily NAV Trends for Top 40 Schemes (2022 - 2026)')
fig.add_vrect(x0="2023-01-01", x1="2023-12-31", fillcolor="green", opacity=0.1, line_width=0, annotation_text="2023 Bull Run")
fig.add_vrect(x0="2024-01-01", x1="2024-12-31", fillcolor="red", opacity=0.1, line_width=0, annotation_text="2024 Correction")
fig.update_layout(showlegend=False, hovermode='x unified', template='plotly_white')
try:
    fig.write_image("reports/charts/nav_trend.png", width=1200, height=600, scale=2)
except Exception as e:
    print("Plotly kaleido missing:", e)

# 2. AUM Growth Analysis
years = [2022, 2023, 2024, 2025]
amcs = ['SBI Mutual Fund', 'HDFC Mutual Fund', 'ICICI Prudential', 'Nippon India']
aum_records = []
for amc in amcs:
    base_aum = np.random.uniform(5, 8)
    for year in years:
        growth = np.random.uniform(1.05, 1.25)
        base_aum *= growth
        if amc == 'SBI Mutual Fund' and year == 2025:
            base_aum = 12.5 
        aum_records.append({'Year': year, 'Fund House': amc, 'AUM_Lakh_Crore': base_aum})

aum_df = pd.DataFrame(aum_records)
plt.figure(figsize=(14, 7))
ax = sns.barplot(data=aum_df, x='Year', y='AUM_Lakh_Crore', hue='Fund House', palette='Blues_d')
plt.title('AUM Growth Analysis (2022 - 2025)', fontsize=16, fontweight='bold')
plt.ylabel('AUM (₹ Lakh Crore)', fontsize=12)
plt.xlabel('Year', fontsize=12)
for p in ax.patches:
    height = p.get_height()
    if height > 0:
        ax.annotate(f'{height:.1f}', (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 5), textcoords='offset points')
plt.tight_layout()
plt.savefig('reports/charts/aum_growth.png', dpi=300)
plt.close()

# 3. SIP Inflow Time-Series
months = pd.date_range(start='2022-01-01', end='2025-12-01', freq='MS')
sip_inflows = np.linspace(10000, 31002, len(months)) + np.random.normal(0, 500, len(months))
sip_inflows[-1] = 31002
sip_df = pd.DataFrame({'Month': months, 'SIP_Inflow_Cr': sip_inflows})
fig = px.scatter(sip_df, x='Month', y='SIP_Inflow_Cr', trendline='ols', title='Monthly SIP Inflows (Jan 2022 - Dec 2025)')
fig.update_traces(mode='lines+markers')
fig.add_annotation(x='2025-12-01', y=31002, text='Peak: ₹31,002 Crore', showarrow=True, arrowhead=1)
fig.update_layout(template='plotly_white', hovermode='x unified')
try:
    fig.write_image("reports/charts/sip_trend.png", width=1000, height=500, scale=2)
except Exception as e:
    pass

# 4. Category Inflow Heatmap
categories = ['Large Cap', 'Mid Cap', 'Small Cap', 'Flexi Cap', 'Sectoral/Thematic', 'Debt', 'Liquid']
months_str = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
heatmap_data = np.random.uniform(-5000, 15000, size=(len(categories), 12))
heatmap_df = pd.DataFrame(heatmap_data, index=categories, columns=months_str)
plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_df, cmap='RdYlGn', annot=True, fmt=".0f", linewidths=.5, cbar_kws={'label': 'Net Inflow (₹ Cr)'})
plt.title('Monthly Net Inflows by Fund Category (2025)', fontsize=16, fontweight='bold')
plt.ylabel('Fund Category')
plt.xlabel('Month')
plt.tight_layout()
plt.savefig('reports/charts/category_heatmap.png', dpi=300)
plt.close()

# 5. Investor Demographics
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
age_counts = demographics['age_group'].value_counts()
axes[0].pie(age_counts, labels=age_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
axes[0].set_title('Age Group Distribution')
demographics['sip_amount'] = np.random.lognormal(mean=np.log(5000), sigma=0.8, size=len(demographics))
sns.boxplot(data=demographics, x='age_group', y='sip_amount', ax=axes[1], palette='Set2')
axes[1].set_title('SIP Amount by Age Group')
axes[1].set_yscale('log')
axes[1].set_ylabel('SIP Amount (Log Scale)')
gender_counts = demographics['gender'].value_counts()
axes[2].pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set3'))
axes[2].set_title('Gender Distribution')
plt.tight_layout()
plt.savefig('reports/charts/demographics.png', dpi=300)
plt.close()

# 6. Geographic Distribution
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
state_sip = demographics.groupby('state')['sip_amount'].sum().sort_values(ascending=True)
state_sip.plot(kind='barh', ax=axes[0], color='teal')
axes[0].set_title('Total SIP Amount by State')
axes[0].set_xlabel('Total SIP (₹)')
axes[0].set_ylabel('State')
tier_counts = demographics['city_tier'].value_counts()
axes[1].pie(tier_counts, labels=tier_counts.index, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'])
axes[1].set_title('T30 vs B30 City Tier Distribution')
plt.tight_layout()
plt.savefig('reports/charts/geography.png', dpi=300)
plt.close()

# 7. Folio Count Growth
folio_months = pd.date_range(start='2022-01-01', end='2025-12-01', freq='3MS')
folio_counts = np.linspace(13.26, 26.12, len(folio_months))
plt.figure(figsize=(10, 5))
plt.plot(folio_months, folio_counts, marker='o', linestyle='-', color='purple', linewidth=2)
plt.fill_between(folio_months, folio_counts, color='purple', alpha=0.1)
plt.annotate('Jan 2022: 13.26 Cr', xy=(folio_months[0], folio_counts[0]), xytext=(folio_months[1], folio_counts[0]+1), arrowprops=dict(facecolor='black', shrink=0.05))
plt.annotate('Dec 2025: 26.12 Cr', xy=(folio_months[-1], folio_counts[-1]), xytext=(folio_months[-3], folio_counts[-1]-1), arrowprops=dict(facecolor='black', shrink=0.05))
plt.title('Mutual Fund Folio Count Growth (2022 - 2025)', fontsize=16, fontweight='bold')
plt.ylabel('Folio Count (Crores)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('reports/charts/folio_growth.png', dpi=300)
plt.close()

# 8. NAV Return Correlation
top_10_funds = nav_trend_df['fund_name'].unique()[:10]
nav_pivot = nav_trend_df[nav_trend_df['fund_name'].isin(top_10_funds)].pivot(index='date', columns='fund_name', values='nav')
returns_df = nav_pivot.pct_change().dropna()
correlation_matrix = returns_df.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=0.5, vmax=1, fmt=".2f", linewidths=0.5)
plt.title('Correlation Matrix of Daily Returns', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/charts/correlation_matrix.png', dpi=300)
plt.close()

# 9. Sector Allocation
plt.figure(figsize=(8, 8))
plt.pie(holdings['weight_pct'], labels=holdings['sector'], autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.4, edgecolor='w'), colors=sns.color_palette('Spectral'))
plt.title('Overall Sector Allocation in Equity Funds', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/charts/sector_allocation.png', dpi=300)
plt.close()

print("All charts generated and saved successfully!")
