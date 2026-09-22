from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_PRODUCT_PATH = PROJECT_ROOT / "sql" / "return_product_top10.sql"
SQL_TREND_PATH = PROJECT_ROOT / "sql" / "return_monthly_trend.sql"
CHART_DIR = PROJECT_ROOT / "charts"
CHART_PRODUCT_PATH = CHART_DIR / "return_01_product.png"
CHART_TREND_PATH = CHART_DIR / "return_02_trend.png"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


# ---------- 连接MySQL ----------

mysql_url = os.getenv("MYSQL_URL")
if not mysql_url:
    raise ValueError(
        "MYSQL_URL is not set. Please create a .env file based on .env.example."
    )

engine = create_engine(mysql_url)

sql_product = SQL_PRODUCT_PATH.read_text(encoding="utf-8")
df_product = pd.read_sql(sql_product, engine).reset_index(drop=True)

sql_trend = SQL_TREND_PATH.read_text(encoding="utf-8")
df_trend = pd.read_sql(sql_trend, engine).reset_index(drop=True)

# ---------- 画图 ----------
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(
    df_product['Description'],
    df_product['total_return_amount'],
    color='#327AC7', alpha=0.8
)
for bar, val in zip(bars, df_product['total_return_amount']):
    ax.text(val + 100, bar.get_y() + bar.get_height()/2,
            f'£{val:,.0f}', va='center', fontsize=9)
ax.set_title('退货损失金额 Top10 商品', fontsize=15, fontweight='bold', pad=15)
ax.set_xlabel('退货损失金额 (£)', fontsize=12)
ax.set_xlim(0, df_product['total_return_amount'].max() * 1.2)
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_PRODUCT_PATH, dpi=150, bbox_inches='tight')
plt.show()
print(f"Chart saved to: {CHART_PRODUCT_PATH}")

# ---------- 画图 ----------
fig, ax1 = plt.subplots(figsize=(12, 6))

# 柱状图：退货损失金额
ax1.bar(range(len(df_trend)), df_trend['total_return_amount'],
        color='#0F64BF', alpha=0.9, label='退货损失金额')
ax1.set_ylabel('退货损失金额 (£)', fontsize=12)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f'£{x/1000:.0f}K'))

# 折线图：退货订单数
ax2 = ax1.twinx()
ax2.plot(range(len(df_trend)), df_trend['return_orders'],
         color='#2c3e50', linewidth=2.5,
         marker='o', markersize=5, label='退货订单数')
ax2.set_ylabel('退货订单数', fontsize=12)

ax1.set_xticks(range(len(df_trend)))
ax1.set_xticklabels(df_trend['month'], rotation=45, ha='right')

# 标注旺季
ax1.axvspan(9, 11, alpha=0.1, color='orange', label='下单旺季')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')


plt.title('月度退货趋势',
          fontsize=15, fontweight='bold', pad=15)
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_TREND_PATH, dpi=150, bbox_inches='tight')
plt.show()
print(f"Chart saved to: {CHART_TREND_PATH}")
