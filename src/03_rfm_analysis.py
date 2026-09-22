from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = PROJECT_ROOT / "sql" / "rfm_analysis.sql"
CHART_DIR = PROJECT_ROOT / "charts"
CHART_PATH1 = CHART_DIR / "rfm_01_distribution.png"
CHART_PATH2 = CHART_DIR / "rfm_02_monetary.png"
CHART_PATH3 = CHART_DIR / "rfm_03_scatter.png"

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


# RFM打分
df['R_score'] = pd.qcut(df['Recency'], q=5, labels=[5,4,3,2,1]).astype(int)
df['F_score'] = pd.qcut(df['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)
df['M_score'] = pd.qcut(df['Monetary'], q=5, labels=[1,2,3,4,5]).astype(int)

def segment_user(row):
    r, f, m = row['R_score'], row['F_score'], row['M_score']
    if r >= 4 and f >= 4 and m>=4:   return '重要价值客户'
    elif r >= 4 and f < 3:  return '新客/潜力客户'
    elif r < 3 and f >= 4:  return '流失高价值客户'
    elif r >= 3 and f >= 3: return '一般价值客户'
    elif r < 3 and f < 3:   return '流失普通客户'
    else:                   return '其他'

df['segment'] = df.apply(segment_user, axis=1)
print(df[df['segment']=='流失高价值客户']['Monetary'].sum())

seg_colors = {
    '重要价值客户':   '#2ecc71',
    '新客/潜力客户':  '#3498db',
    '一般价值客户':   '#f39c12',
    '流失高价值客户': '#e67e22',
    '流失普通客户':   '#e74c3c',
    '其他':          '#95a5a6',
}

# ---------- 图1：用户分层分布饼图 ----------
fig, ax = plt.subplots(figsize=(8, 8))
seg_count = df['segment'].value_counts()
ax.pie(
    seg_count,
    labels=seg_count.index,
    colors=[seg_colors[s] for s in seg_count.index],
    autopct='%1.2f%%',
    startangle=90,
    pctdistance=0.8,
)
ax.set_title('用户分层分布', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_PATH1, dpi=150, bbox_inches='tight')
plt.show()

print(f"Chart saved to: {CHART_PATH1}")

# ---------- 图2：各分层平均消费金额 ----------
fig, ax = plt.subplots(figsize=(10, 6))
Seg_Monetary = df.groupby('segment')['Monetary'].mean().sort_values(ascending=True)
bars = ax.barh(
    Seg_Monetary.index,
    Seg_Monetary.values,
    color=[seg_colors[s] for s in Seg_Monetary.index],
    alpha=1,
)
for bar, val in zip(bars, Seg_Monetary.values):
    ax.text(val + 50, bar.get_y() + bar.get_height() / 2,
            f'£{val:,.0f}', va='center', fontsize=10)
ax.set_title('各分层平均消费金额', fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('平均消费金额 (£)', fontsize=12)
ax.set_xlim(0, Seg_Monetary.max() * 1.25)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_PATH2, dpi=150, bbox_inches='tight')
plt.show()

print(f"Chart saved to: {CHART_PATH2}")


# ---------- 图3：Recency vs Frequency 散点图 ----------
fig, ax = plt.subplots(figsize=(10, 7))
for seg, color in seg_colors.items():
    mask = df['segment'] == seg
    ax.scatter(
        df.loc[mask, 'Recency'],
        df.loc[mask, 'Frequency'],
        c=color, label=seg,
        alpha=0.5, s=25,
    )
ax.set_title('用户活跃度分布（Recency vs Frequency）',
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('距上次购买天数（越小越活跃）', fontsize=12)
ax.set_ylabel('购买频次', fontsize=12)
ax.set_xlim(0, 380)
ax.legend(fontsize=10, loc='upper right',
          framealpha=0.9, edgecolor='#cccccc')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_PATH3, dpi=150, bbox_inches='tight')
plt.show()

print(f"Chart saved to: {CHART_PATH3}")
