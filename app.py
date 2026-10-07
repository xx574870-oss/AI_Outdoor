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
        "雨": [
            "雨",
            "雨の日",
            "レイン"
        ],

        "防水": [
            "防水",
            "雨",
            "レイン"
        ],

        "軽量": [
            "軽い",
            "軽量",
            "持ち運び"
        ],

        "旅行": [
            "旅行",
            "観光"
        ],

        "登山": [
            "登山"
        ],

        "冬": [
            "冬",
            "寒い",
            "防寒"
        ],

        "夏": [
            "夏",
            "暑い",
            "涼しい"
        ],

        "暖かい": [
            "暖かい",
            "暖かく",
            "保温",
            "防寒"
        ],

        "涼しい": [
            "涼しい",
            "暑い",
            "通気性",
            "蒸れない"
        ],

        "ストレッチ": [
            "ストレッチ",
            "動きやすい"
        ],

        "コンパクト": [
            "コンパクト",
            "収納"
        ]
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

def calculate_match_score(
    user_query,
    product
):

    query = user_query.lower()

    conditions = get_user_conditions(query)

    if not conditions:
        return 0.0

    product_text = " ".join([
        str(product["product_name"]),
        str(product["category"]),
        str(product["season"]),
        str(product["use_case"]),
        str(product["features"]),
        str(product["description"]),
        str(product["target_user"])
    ]).lower()

    matched = 0

    # -------------------------
    # 每個需求條件
    # -------------------------

    for condition in conditions:

        if condition == "雨":

            if (
                "雨" in product_text
                or "レイン" in product_text
                or "防水" in product_text
            ):
                matched += 1

        elif condition == "防水":

            if (
                "防水" in product_text
                or product["waterproof"] in [
                    "高",
                    "非常に高い"
                ]
            ):
                matched += 1

        elif condition == "軽量":

            if (
                "軽量" in product_text
                or "軽量" in str(product["features"])
            ):
                matched += 1

        elif condition == "旅行":

            if "旅行" in product_text:
                matched += 1

        elif condition == "登山":

            if "登山" in product_text:
                matched += 1

        elif condition == "冬":

            if "冬" in str(product["season"]):
                matched += 1

        elif condition == "夏":

            if "夏" in str(product["season"]):
                matched += 1

        elif condition == "暖かい":

            if (
                product["warmth"] == "高"
                or "保温" in product_text
            ):
                matched += 1

        elif condition == "涼しい":

            if (
                product["breathability"] in [
                    "高",
                    "非常に高い"
                ]
                or "涼しい" in product_text
            ):
                matched += 1

        elif condition == "ストレッチ":

            if (
                "ストレッチ" in product_text
                or "動きやすい" in product_text
            ):
                matched += 1

        elif condition == "コンパクト":

            if (
                "コンパクト" in product_text
                or product["packability"] in [
                    "高い",
                    "非常に高い"
                ]
            ):
                matched += 1

    return matched / len(conditions)


# =========================
# 5. 商品屬性分數
# =========================

def calculate_attribute_score(
    user_query,
    product
):

    query = user_query.lower()

    score = 0.0

    # -------------------------
    # 防水
    # -------------------------

    if any(
        keyword in query
        for keyword in [
            "雨",
            "雨の日",
            "防水",
            "レイン"
        ]
    ):

        if product["waterproof"] == "非常に高い":
            score += 0.25

        elif product["waterproof"] == "高":
            score += 0.20

        elif product["waterproof"] == "中":
            score += 0.05

    # -------------------------
    # 輕量
    # -------------------------

    if any(
        keyword in query
        for keyword in [
            "軽い",
            "軽量",
            "持ち運び"
        ]
    ):

        if "軽量" in str(product["features"]):
            score += 0.15

        if product["packability"] in [
            "高い",
            "非常に高い"
        ]:
            score += 0.10

    # -------------------------
    # 暖和
    # -------------------------

    if any(
        keyword in query
        for keyword in [
            "暖かい",
            "暖かく",
            "防寒",
            "保温",
            "寒い"
        ]
    ):

        if product["warmth"] == "高":
            score += 0.25

        elif product["warmth"] == "中":
            score += 0.10

    # -------------------------
    # 涼爽 / 通氣
    # -------------------------

    if any(
        keyword in query
        for keyword in [
            "涼しい",
            "暑い",
            "通気性",
            "蒸れない"
        ]
    ):

        if product["breathability"] == "非常に高い":
            score += 0.25

        elif product["breathability"] == "高":
            score += 0.20

        elif product["breathability"] == "中":
            score += 0.05

    # -------------------------
    # 旅行
    # -------------------------

    if any(
        keyword in query
        for keyword in [
            "旅行",
            "観光"
        ]
    ):

        if "旅行" in str(product["use_case"]):
            score += 0.10

    # -------------------------
    # 登山
    # -------------------------

    if "登山" in query:

        if "登山" in str(product["use_case"]):
            score += 0.10

    # -------------------------
    # ストレッチ
    # -------------------------

    if any(
        keyword in query
        for keyword in [
            "ストレッチ",
            "動きやすい"
        ]
    ):

        if (
            "ストレッチ"
            in str(product["features"])
            or
            "動きやすい"
            in str(product["features"])
        ):
            score += 0.15

    return min(score, 1.0)


# =========================
# 6. 重量加分
# =========================

def calculate_weight_bonus(
    user_query,
    weight
):

    query = user_query.lower()

    if not any(
        keyword in query
        for keyword in [
            "軽い",
            "軽量",
            "持ち運び"
        ]
    ):
        return 0.0

    weight_text = str(weight)

    if (
        "要公式確認" in weight_text
        or weight_text.lower() == "nan"
    ):
        return 0.0

    match = re.search(
        r"\d+",
        weight_text
    )

    if not match:
        return 0.0

    weight_value = int(
        match.group()
    )

    if weight_value <= 200:
        return 0.10

    elif weight_value <= 300:
        return 0.07

    elif weight_value <= 500:
        return 0.04

    return 0.01


# =========================
# 7. 商品推薦
# =========================

def recommend_products(
    user_query,
    top_n=3
):

    result = df.copy()

    # 條件一致度
    result["similarity"] = result.apply(
        lambda product:
        calculate_match_score(
            user_query,
            product
        ),
        axis=1
    )

    # 屬性分數
    result["attribute_score"] = result.apply(
        lambda product:
        calculate_attribute_score(
            user_query,
            product
        ),
        axis=1
    )

    # 重量加分
    result["weight_bonus"] = result.apply(
        lambda product:
        calculate_weight_bonus(
            user_query,
            product["weight"]
        ),
        axis=1
    )

    # 最終分數
    result["final_score"] = (
        result["similarity"] * 0.50
        + result["attribute_score"] * 0.40
        + result["weight_bonus"] * 0.10
    )

    # 排序
    result = result.sort_values(
        by=[
            "final_score",
            "similarity",
            "attribute_score",
            "weight_bonus"
        ],
        ascending=False
    )

    return result.head(top_n)


# =========================
# 8. Streamlit UI
# =========================

st.set_page_config(
    page_title="AI Outdoor Recommendation",
    page_icon="🏕️",
    layout="wide"
)

st.title(
    "🏕️ AIを活用したアウトドア用品推薦システム"
)

st.write(
    "あなたの希望を入力すると、"
    "AIが条件に合ったアウトドア用品を推薦します。"
)

st.info(
    "例：冬の京都旅行で、軽くて暖かい服が欲しいです。"
)

user_query = st.text_input(
    "欲しい商品の条件を入力してください",
    placeholder=(
        "例：雨の日の旅行で使える、"
        "防水性が高くて軽い服が欲しいです。"
    )
)


# =========================
# 9. 推薦結果
# =========================

if st.button(
    "🔍 商品を推薦する",
    use_container_width=True
):

    if not user_query.strip():

        st.warning(
            "条件を入力してください。"
        )

    else:

        recommendations = recommend_products(
            user_query,
            top_n=3
        )

        st.subheader(
            "🎯 おすすめ商品"
        )

        for rank, (_, product) in enumerate(
            recommendations.iterrows(),
            start=1
        ):

            st.markdown(
                f"## {rank}位："
                f"{product['product_name']}"
            )

            col1, col2 = st.columns(2)

            # -------------------------
            # 左側
            # -------------------------

            with col1:

                st.write(
                    f"**カテゴリー：** "
                    f"{product['category']}"
                )

                price = product["price"]

                if price > 0:

                    st.write(
                        f"**価格：** "
                        f"¥{int(price):,}"
                    )

                else:

                    st.write(
                        "**価格：** 要公式確認"
                    )

                st.write(
                    f"**特徴：** "
                    f"{product['features']}"
                )

                st.write(
                    f"**重量：** "
                    f"{product['weight']}"
                )

            # -------------------------
            # 右側
            # -------------------------

            with col2:

                st.write(
                    f"**防水性：** "
                    f"{product['waterproof']}"
                )

                st.write(
                    f"**保温性：** "
                    f"{product['warmth']}"
                )

                st.write(
                    f"**通気性：** "
                    f"{product['breathability']}"
                )

                st.write(
                    f"**収納性：** "
                    f"{product['packability']}"
                )

            st.write(
                f"**商品説明：** "
                f"{product['description']}"
            )

            # -------------------------
            # 評分
            # -------------------------

            st.write(
                f"条件一致度："
                f"{product['similarity']:.3f}"
            )

            st.write(
                f"属性スコア："
                f"{product['attribute_score']:.3f}"
            )

            st.write(
                f"最終スコア："
                f"{product['final_score']:.3f}"
            )

            # -------------------------
            # 官方網站
            # -------------------------

            official_url = str(
                product.get(
                    "official_url",
                    ""
                )
            ).strip()

            if (
                official_url
                and official_url.lower() != "nan"
            ):

                st.markdown(
                    "### 🛒 商品公式サイト"
                )

                st.link_button(
                    "🛒 公式サイトで商品を見る",
                    official_url,
                    use_container_width=True
                )

            else:

                st.info(
                    "公式サイトの商品ページは"
                    "現在登録されていません。"
                )

            st.divider()
