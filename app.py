```python
import streamlit as st
import pandas as pd
import re


# =========================
# 1. 載入商品資料
# =========================

df = pd.read_csv(
    "products.csv",
    encoding="utf-8-sig"
)


# =========================
# 2. 整理價格
# =========================

def clean_price(value):
    try:
        text = str(value).replace(",", "").replace("¥", "").strip()

        if text == "" or text.lower() == "nan":
            return 0

        return float(text)

    except:
        return 0


df["price"] = df["price"].apply(clean_price)


# =========================
# 3. 關鍵字分析
# =========================

def get_user_conditions(query):

    conditions = []

    keyword_groups = {
        "雨": ["雨", "雨の日", "レイン"],
        "防水": ["防水", "雨", "レイン"],
        "軽量": ["軽い", "軽量", "持ち運び"],
        "旅行": ["旅行", "観光"],
        "登山": ["登山"],
        "冬": ["冬", "寒い", "防寒"],
        "夏": ["夏", "暑い", "涼しい"],
        "暖かい": ["暖かい", "暖かく", "保温", "防寒"],
        "涼しい": ["涼しい", "暑い", "通気性", "蒸れない"],
        "ストレッチ": ["ストレッチ", "動きやすい"],
        "コンパクト": ["コンパクト", "収納"]
    }

    for condition, keywords in keyword_groups.items():

        if any(
            keyword in query
            for keyword in keywords
        ):
            conditions.append(condition)

    return conditions


# =========================
# 4. 條件一致度
# =========================

def calculate_match_score(user_query, product):

    query = user_query.lower()

    score = 0.0
    total = 0.0

    # 雨／防水
    if any(
        k in query
        for k in ["雨", "雨の日", "防水", "レイン"]
    ):
        total += 3

        if product["waterproof"] == "非常に高い":
            score += 3

        elif product["waterproof"] == "高":
            score += 2.5

        elif product["waterproof"] == "中":
            score += 1.5

        elif product["waterproof"] == "低":
            score += 0.5

    # 輕量
    if any(
        k in query
        for k in ["軽い", "軽量", "持ち運び"]
    ):
        total += 2

        features = str(product["features"])

        if "軽量" in features:
            score += 2

        weight = str(product["weight"])

        matc
```
