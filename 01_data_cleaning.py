import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

# 原始数据路径
raw_data_path = Path("data/raw/data.csv")

# 清洗后数据保存路径
clean_data_path = Path("data/processed/clean_data.csv")

# 读取原始数据
df = pd.read_csv(raw_data_path, encoding="ISO-8859-1")

print(df.head())
print(df.info())
print(df.shape)
print(df.dtypes)
print(df.isnull().sum())
print(df.nunique())

# ---------- 清洗数据 ----------

clean_data = (
    df
    .dropna(subset=["CustomerID"])
    .query("UnitPrice > 0")
    .assign(
        InvoiceDate=lambda x: pd.to_datetime(x["InvoiceDate"], errors="coerce"),
        CustomerID=lambda x: x["CustomerID"].astype(int).astype(str),
        is_return=lambda x: (
            x["InvoiceNo"].astype(str).str.startswith("C") | (x["Quantity"] < 0)
        ),
        UnitPrice=lambda x: x["UnitPrice"].round(2),
        SalesAmount=lambda x: (x["Quantity"] * x["UnitPrice"]).round(2)
    )
    .dropna(subset=["InvoiceDate"])
)

# ---------- 保存清洗后数据 ----------

clean_data_path.parent.mkdir(parents=True, exist_ok=True)
clean_data.to_csv(clean_data_path, index=False, encoding="utf-8-sig")

print("清洗后的数据已保存到：", clean_data_path)


load_dotenv()

mysql_url = os.getenv("MYSQL_URL")
engine = create_engine(mysql_url)

clean_data.to_sql(
    name="cleaned_orders",
    con=engine,
    if_exists="replace",
    index=False
)