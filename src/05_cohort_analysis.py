from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
from sqlalchemy import create_engine
import seaborn as sns

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = PROJECT_ROOT / "sql" / "cohort_analysis.sql"
CHART_DIR = PROJECT_ROOT / "charts"
CHART_PATH = CHART_DIR / "cohort_retention.png"

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


df['order_month'] = pd.to_datetime(df['order_month'])
# ----------- 计算每个用户的首购月份 -----------
df['cohort_month'] = df.groupby('CustomerID')['order_month'].transform('min')

# ----------- 计算距首购的月份数 -----------
df['period'] = (
    (df['order_month'].dt.year - df['cohort_month'].dt.year) * 12 +
    (df['order_month'].dt.month - df['cohort_month'].dt.month)
)

# ----------- 构建同期群矩阵 -----------
cohort_data = (
    df.groupby(['cohort_month', 'period'])['CustomerID']
    .nunique()
    .reset_index()
)

cohort_pivot = cohort_data.pivot_table(
    index='cohort_month',
    columns='period',
    values='CustomerID'
)

# 转为留存率（每行除以第0期的用户数）
cohort_size = cohort_pivot[0]
retention = cohort_pivot.divide(cohort_size, axis=0).round(3)

# 格式化index为年月字符串
retention.index = retention.index.strftime('%Y-%m')

# ---------- 画图 ----------
# 第一步：搭建画布
fig, ax =plt.subplots(figsize=(10,6))

# 第二步：画图，选择heatmap热力图
sns.heatmap(
    retention,
    annot=True,
    fmt='0.1%',
    cmap='YlOrRd',
    vmin=0, vmax=0.5,
    linewidths=0.4,
    ax=ax,
    cbar_kws={'label':'留存率(%)'},
    annot_kws={'size':8},
)

# 第三步：绘制标题与xy坐标轴
ax.set_title('用户同期群留存率分析（Cohort Retention）',
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('距首次购买月份',fontsize=12)
ax.set_ylabel('收购月份(同期群)',fontsize=12)

# 第四步：完善保存与显示图片
plt.tight_layout()
CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_PATH,dpi=150,bbox_inches='tight')
plt.show()

print(f"Chart saved to: {CHART_PATH}")
