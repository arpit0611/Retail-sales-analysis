import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def display(df):
    print(df.to_string(index=False))

pd.set_option('display.max_columns', 20)
Path('charts').mkdir(exist_ok=True)
plt.rcParams['figure.figsize'] = (9, 5)

df = pd.read_csv('retail_sales.csv')
print('Rows and columns (raw):', df.shape)
display(df.head())

print('Column types:')
print(df.dtypes)
print(); print('Missing values per column:')
print(df.isna().sum())
print(); print('Duplicate rows:', df.duplicated().sum())

before = len(df)
df = df.drop_duplicates().copy()
df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
df['City'] = df['City'].fillna('Unknown')
df['Discount_Pct'] = pd.to_numeric(df['Discount_Pct'], errors='coerce').fillna(0)
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
df['Unit_Price_INR'] = pd.to_numeric(df['Unit_Price_INR'], errors='coerce')
df = df.dropna(subset=['Order_Date', 'Quantity', 'Unit_Price_INR'])
df = df[
    (df['Quantity'] > 0) &
    (df['Unit_Price_INR'] > 0) &
    df['Discount_Pct'].between(0, 100)
].copy()
print('Removed rows:', before - len(df))
print('Clean orders:', len(df))
print('Missing values after cleaning:', df.isna().sum().sum())

df['Revenue_INR'] = (
    df['Quantity'] * df['Unit_Price_INR'] * (1 - df['Discount_Pct'] / 100)
).round(2)
df['Month'] = df['Order_Date'].dt.to_period('M').astype(str)
display(df[['Order_ID', 'Quantity', 'Unit_Price_INR', 'Discount_Pct', 'Revenue_INR', 'Month']].head())

total_revenue = df['Revenue_INR'].sum()
order_count = df['Order_ID'].nunique()
units_sold = df['Quantity'].sum()
aov = total_revenue / order_count
print(f'Total revenue: ₹{total_revenue:,.2f}')
print(f'Unique orders: {order_count:,}')
print(f'Units sold: {units_sold:,}')
print(f'Average order value: ₹{aov:,.2f}')

category_sales = df.groupby('Category')['Revenue_INR'].sum().sort_values(ascending=False)
print(category_sales.round(2).to_string())
ax = category_sales.plot(kind='bar', color='#3973b9')
ax.set(title='Revenue by Category', xlabel='Category', ylabel='Revenue (INR)')
plt.xticks(rotation=25, ha='right')
plt.tight_layout()
plt.savefig('charts/01_category_revenue.png', dpi=150)
plt.show()

monthly_sales = df.groupby('Month')['Revenue_INR'].sum().sort_index()
print(monthly_sales.round(2).to_string())
ax = monthly_sales.plot(kind='line', marker='o', linewidth=2, color='#3973b9')
ax.set(title='Monthly Revenue (2025)', xlabel='Month', ylabel='Revenue (INR)')
plt.xticks(rotation=45, ha='right')
plt.grid(alpha=.25)
plt.tight_layout()
plt.savefig('charts/02_monthly_revenue.png', dpi=150)
plt.show()

city_sales = df.groupby('City')['Revenue_INR'].sum().sort_values(ascending=False)
print(city_sales.round(2).to_string())
ax = city_sales.sort_values().plot(kind='barh', color='#299e88')
ax.set(title='Revenue by City', xlabel='Revenue (INR)', ylabel='City')
plt.tight_layout()
plt.savefig('charts/03_city_revenue.png', dpi=150)
plt.show()

product_sales = df.groupby('Product')['Revenue_INR'].sum().nlargest(7)
print(product_sales.round(2).to_string())
ax = product_sales.sort_values().plot(kind='barh', color='#9862ae')
ax.set(title='Top 7 Products by Revenue', xlabel='Revenue (INR)', ylabel='Product')
plt.tight_layout()
plt.savefig('charts/04_top_products.png', dpi=150)
plt.show()

payment_counts = df['Payment_Method'].value_counts()
print(payment_counts.to_string())
ax = payment_counts.plot(kind='bar', color='#dd8a3e')
ax.set(title='Orders by Payment Method', xlabel='Payment Method', ylabel='Number of Orders')
plt.xticks(rotation=20, ha='right')
plt.tight_layout()
plt.savefig('charts/05_payment_methods.png', dpi=150)
plt.show()

peak_month = monthly_sales.idxmax()
top_category = category_sales.idxmax()
top_city = city_sales.drop(labels='Unknown', errors='ignore').idxmax()
top_product = product_sales.idxmax()
top_payment = payment_counts.idxmax()

findings = f"""# Retail Sales Analysis — Findings

**Dataset:** Synthetic educational data, calendar year 2025.
**Cleaning:** Removed {before - len(df)} duplicate/invalid rows, labelled missing cities Unknown, and assumed a 0% discount where missing.

## Key metrics
- Total revenue: ₹{total_revenue:,.2f}
- Unique orders: {order_count:,}
- Units sold: {units_sold:,}
- Average order value: ₹{aov:,.2f}

## Main findings
1. **Top category:** {top_category} (₹{category_sales.iloc[0]:,.2f}).
2. **Peak month:** {peak_month} (₹{monthly_sales.max():,.2f}).
3. **Top known city:** {top_city} (₹{city_sales[top_city]:,.2f}).
4. **Top product by revenue:** {top_product} (₹{product_sales.iloc[0]:,.2f}).
5. **Most-used payment method:** {top_payment} ({payment_counts.iloc[0]:,} orders).

## Possible business actions (hypotheses, not proven conclusions)
- Review inventory for high-revenue categories and products.
- Investigate what caused the peak month before planning promotions.
- Monitor data-entry quality to reduce Unknown city entries.

## Limitations
- The dataset is artificial and designed for learning. Results are not evidence about a real company.
- There is no profit, customer, return, or marketing-spend data; revenue alone does not indicate profitability.
"""
Path('findings.md').write_text(findings, encoding='utf-8')
print(findings)

