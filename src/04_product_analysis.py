from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = PROJECT_ROOT / "sql" / "product_analysis.sql"
CHART_DIR = PROJECT_ROOT / "charts"
CHART_PATH = CHART_DIR / "product_pareto.png"

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


# ---------- 连接MySQL ----------

mysql_url = os.getenv("MYSQL_URL")
if not mysql_url:
    raise ValueError(
        "MYSQL_URL is not set. Please create a .env file based on .env.example."
    )

engine = create_engine(mysql_url)

sql = SQL_PATH.read_text(encoding="utf-8")
df = pd.read_sql(sql, engine).reset_index(drop=True)

# ---------- 帕累托计算 ----------
df = df.sort_values('total_revenue', ascending=False).reset_index(drop=True)

# 累计销售额占比
df['cumulative_revenue'] = df['total_revenue'].cumsum()
df['cumulative_pct'] = df['cumulative_revenue'] / df['total_revenue'].sum() * 100

# 商品数量占比
df['sku_pct'] = (df.index + 1) / len(df) * 100

# 找到关键节点
pct_80 = df[df['cumulative_pct'] >= 80].iloc[0]
pct_50 = df[df['cumulative_pct'] >= 50].iloc[0]

# ---------- 帕累托图 ----------
fig, ax1 = plt.subplots(figsize=(10, 6))

# 柱状图：各商品销售额
ax1.bar(range(len(df)), df['total_revenue'],
        color='#4C72B0', alpha=0.7, label='单品销售额')
ax1.set_xlabel('商品排名（按销售额降序）', fontsize=12)
ax1.set_ylabel('销售额 (£)', fontsize=12)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f'£{x/1000:.0f}K'))

# 折线图：累计销售额占比
ax2 = ax1.twinx()
ax2.plot(range(len(df)), df['cumulative_pct'],
         color='#DD8452', linewidth=2.5, label='累计销售额占比')
ax2.set_ylabel('累计销售额占比 (%)', fontsize=12)
ax2.set_ylim(0, 105)

# 标注80%分位线
idx_80 = df[df['cumulative_pct'] >= 80].index[0]
ax2.axhline(y=80, color='red', linestyle='--', linewidth=1.2, alpha=0.7)
ax2.axvline(x=idx_80+1, color='red', linestyle='--', linewidth=1.2, alpha=0.7)
ax2.annotate(f'前{idx_80+1}个SKU\n贡献80%销售额\n（占总SKU {pct_80["sku_pct"]:.1f}%）',
             xy=(idx_80+1, 80),
             xytext=(idx_80 + 100, 60),
             fontsize=9, color='red',
             arrowprops=dict(arrowstyle='->', color='red'))

# 图例合并
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right')


plt.title('商品销售额帕累托分析', fontsize=16, fontweight='bold', pad=15)
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_PATH, dpi=150, bbox_inches='tight')
plt.show()

print(f"Chart saved to: {CHART_PATH}")
