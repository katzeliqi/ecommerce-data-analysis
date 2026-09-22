from pathlib import Path
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = PROJECT_ROOT / "sql" / "sales_trend.sql"
CHART_DIR = PROJECT_ROOT / "charts"
CHART_PATH = CHART_DIR / "sales_trend.png"

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


# ---------- 标记不完整月份 ----------

df["is_incomplete"] = df["month"] == "2011-12"
incomplete_idx = int(df[df["is_incomplete"]].index[0]) if df["is_incomplete"].any() else None


# ---------- 画图 ----------

fig, ax1 = plt.subplots(figsize=(14, 6))

# Highlight Sep-Nov as the peak season window.
ax1.axvspan(8, 10, alpha=0.08, color="orange", label="Q4 Peak Season")

colors = ["#d9534f" if inc else "#4C72B0" for inc in df["is_incomplete"]]
ax1.bar(
    range(len(df)),
    df["monthly_revenue"],
    color=colors,
    alpha=0.7,
    label="Monthly Revenue (£)",
)
ax1.set_ylabel("Monthly Revenue (£)", fontsize=12)
ax1.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, _: f"£{x / 1000:.0f}K")
)

ax2 = ax1.twinx()
ax2.plot(
    range(len(df)),
    df["order_count"],
    color="#DD8452",
    linewidth=2.5,
    marker="o",
    markersize=5,
    label="Order Count",
)
ax2.set_ylabel("Order Count", fontsize=12)

ax1.set_xticks(range(len(df)))
ax1.set_xticklabels(df["month"], rotation=45, ha="center")

if incomplete_idx is not None:
    ax1.annotate(
        "Data until Dec 9 only",
        xy=(incomplete_idx, df.loc[incomplete_idx, "monthly_revenue"]),
        xytext=(incomplete_idx - 2.5, df["monthly_revenue"].max() * 0.75),
        fontsize=9,
        color="#d9534f",
        arrowprops=dict(arrowstyle="->", color="#d9534f", lw=1.5),
    )

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.title(
    "Monthly Sales Trend (Dec 2010 - Dec 2011)",
    fontsize=14,
    fontweight="bold",
    pad=10,
)
plt.tight_layout()

CHART_DIR.mkdir(parents=True, exist_ok=True)
plt.savefig(CHART_PATH, dpi=150, bbox_inches="tight")
plt.show()

print(f"Chart saved to: {CHART_PATH}")
