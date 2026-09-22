from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_REVENUE_PATH = PROJECT_ROOT / "sql" / "country_revenue.sql"
SQL_AVG_REVENUE_PATH = PROJECT_ROOT / "sql" / "country_avg_revenue.sql"
CHART_DIR = PROJECT_ROOT / "charts"
CHART_REVENUE_PATH = CHART_DIR / "country_01_revenue.png"
CHART_AVG_REVENUE_PATH = CHART_DIR / "country_02_avg_revenue.png"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


# ---------- 连接MySQL ----------

mysql_url = os.getenv("MYSQL_URL")
if not mysql_url:
    raise ValueError(
        "MYSQL_URL is not set. Please create a .env file based on .env.example."
    )

engine = create_engine(mysql_url)

sql_revenue = SQL_REVENUE_PATH.read_text(encoding="utf-8")
df_revenue = pd.read_sql(sql_revenue, engine).reset_index(drop=True)

sql_avg_revenue = SQL_AVG_REVENUE_PATH.read_text(encoding="utf-8")
df_avg_revenue = pd.read_sql(sql_avg_revenue, engine).reset_index(drop=True)



# ---------- 画图 ----------
fig, ax = plt.subplots(figsize=(12, 7))
colors = ['#2ecc71' if c == 'United Kingdom' else '#3498db'
          for c in df_revenue['Country']]

bars = ax.barh(df_revenue['Country'], df_revenue['revenue'],
               color=colors, alpha=0.85)
for bar, val in zip(bars, df_revenue['revenue']):
    ax.text(val + 1000, bar.get_y() + bar.get_height()/2,
            f'£{val/1000:.0f}K', va='center', fontsize=9)
legend = [Patch(color='#2ecc71', label='United Kingdom'),
          Patch(color='#3498db', label='海外市场')]
ax.legend(handles=legend, fontsize=10)
ax.set_title('各国销售额 Top15', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('销售额 (£)', fontsize=12)
ax.set_xlim(0, df_revenue['revenue'].max() * 1.15)
ax.invert_yaxis()
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f'£{x/1000:.0f}K'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_REVENUE_PATH, dpi=150, bbox_inches='tight')
plt.show()
print(f"Chart saved to: {CHART_REVENUE_PATH}")

# ---------- 画图 ----------
fig, ax = plt.subplots(figsize=(12, 7))
colors2 = ['#FA1000' if v > 1000 else '#F2DA49'
           for v in df_avg_revenue['avg_order_value']]
bars2 = ax.barh(df_avg_revenue['Country'], df_avg_revenue['avg_order_value'],
                color=colors2, alpha=0.8)
for bar, val in zip(bars2, df_avg_revenue['avg_order_value']):
    ax.text(val + 10, bar.get_y() + bar.get_height()/2,
            f'£{val:,.0f}', va='center', fontsize=9)
ax.axvline(x=439, color='#2ecc71', linestyle='--',
           linewidth=1.5, label='UK客单价 £439')
ax.legend(fontsize=10)
ax.set_title('海外市场客单价对比（红色>£1000）',
             fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('平均客单价 (£)', fontsize=12)
ax.set_xlim(0, df_avg_revenue['avg_order_value'].max() * 1.2)
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_AVG_REVENUE_PATH, dpi=150, bbox_inches='tight')
plt.show()

print(f"Chart saved to: {CHART_AVG_REVENUE_PATH}")