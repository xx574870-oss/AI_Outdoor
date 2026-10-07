import streamlit as st
import pandas as pd
import re

# =========================
# 1. 載入資料
# =========================

df = pd.read_csv(
    "products.csv",
    encoding="utf-8-sig"
)

# =========================
# 2. 文字匹配評分
# =========================

def calculate_attribute_score(user_query, product):

    query = user_query.lower()

    score = 0.0

    # =========================
    # 季節
    # =========================

    if "冬" in query or "寒い" in query or "暖かい" in query or "防寒" in query:

        if "冬" in str(product["season"]):
            score += 0.20

        if product["warmth"] == "高":
            score += 0.15

        elif product["warmth"] == "中":
            score += 0.08

    if "夏" in query or "暑い" in query or "涼しい" in query:

        if "夏" in str(product["season"]):
            score += 0.20

        if product["breathability"] == "非常に高い":
            score += 0.15

        elif product["breathability"] == "高":
            score += 0.10

    if "春" in query:

        if "春" in str(product["season"]):
            score += 0.20

    if "秋" in query:

        if "秋" in str(product["season"]):
            score += 0.20

    # =========================
    # 輕量
    # =========================

    if any(
        keyword in query
        for keyword in [
            "軽い",
            "軽量",
            "持ち運び"
        ]
    ):

        try:
            weight_text = str(product["weight"])
            weight = float(
                weight_text.replace("g", "").strip()
            )

            if weight <= 200:
                score += 0.15

            elif weight <= 300:
                score += 0.12

            elif weight <= 500:
                score += 0.08

            else:
                score += 0.03

        except:
            pass

    # =========================
    # 防水
    # =========================

    if any(
        keyword in query
        for keyword in [
            "防水",
            "雨",
            "レイン"
        ]
    ):

        if product["waterproof"] == "非常に高い":
            score += 0.20

        elif product["waterproof"] == "高":
            score += 0.15

        elif product["waterproof"] == "中":
            score += 0.08

    # =========================
    # 通氣性
    # =========================

    if any(
        keyword in query
        for keyword in [
            "通気性",
            "蒸れない",
            "涼しい",
            "暑い"
        ]
    ):

        if product["breathability"] == "非常に高い":
            score += 0.15

        elif product["breathability"] == "高":
            score += 0.10

        elif product["breathability"] == "中":
            score += 0.05

    # =========================
    # 收納性
    # =========================

    if any(
        keyword in query
        for keyword in [
            "旅行",
            "持ち運び",
            "コンパクト"
        ]
    ):

        if product["packability"] == "非常に高い":
            score += 0.10

        elif product["packability"] == "高い":
            score += 0.08

        elif product["packability"] == "中":
            score += 0.04

    # =========================
    # 保溫性
    # =========================

    if any(
        keyword in query
        for keyword in [
            "暖かい",
            "暖かく",
            "防寒",
            "保温"
        ]
    ):

        if product["warmth"] == "高":
            score += 0.15

        elif product["warmth"] == "中":
            score += 0.08

    # =========================
    # 最低 0
    # =========================

    return max(0.0, score)

# =========================
# 3. 商品屬性評分
# =========================

def calculate_attribute_score(user_query, product):

    query = user_query.lower()

    score = 0.0

    season_keywords = {
        "夏": ["夏", "暑い", "涼しい", "暑さ"],
        "冬": ["冬", "寒い", "暖かい", "防寒"],
        "春": ["春"],
        "秋": ["秋"]
    }

    # 季節
    for season, keywords in season_keywords.items():

        if any(keyword in query for keyword in keywords):

            if season in str(product["season"]):
                score += 0.20
            else:
                score -= 0.15

    # 涼しさ・通気性
    if any(
        keyword in query
        for keyword in [
            "涼しい",
            "涼しく",
            "通気性",
            "蒸れない",
            "暑い"
        ]
    ):

        if product["breathability"] in [
            "高",
            "非常に高い"
        ]:
            score += 0.15

        if product["warmth"] == "高":
            score -= 0.10

    # 輕さ
    if any(
        keyword in query
        for keyword in [
            "軽い",
            "軽量",
            "持ち運び"
        ]
    ):

        if "軽量" in str(product["features"]):
            score += 0.10

        if product["packability"] in [
            "高い",
            "非常に高い"
        ]:
            score += 0.05

    # 暖かさ
    if any(
        keyword in query
        for keyword in [
            "暖かい",
            "暖かく",
            "防寒",
            "保温"
        ]
    ):

        if product["warmth"] == "高":
            score += 0.15

    # 防水
    if any(
        keyword in query
        for keyword in [
            "防水",
            "雨",
            "レイン"
        ]
    ):

        if product["waterproof"] in [
            "高",
            "非常に高い"
        ]:
            score += 0.20

        elif product["waterproof"] == "低":
            score -= 0.20

    # 旅行
    if any(
        keyword in query
        for keyword in [
            "旅行",
            "観光"
        ]
    ):

        if "旅行" in str(product["use_case"]):
            score += 0.10

    return max(0.0, score)


# =========================
# 4. 推薦處理
# =========================

def recommend_products(user_query, top_n=3):

    result = df.copy()

    result["similarity"] = result.apply(
        lambda product: calculate_text_score(
            user_query,
            product
        ),
        axis=1
    )

    result["attribute_score"] = result.apply(
        lambda product: calculate_attribute_score(
            user_query,
            product
        ),
        axis=1
    )

    result["final_score"] = (
        result["similarity"] * 0.70
        + result["attribute_score"] * 0.30
    )

    result = result.sort_values(
        "final_score",
        ascending=False
    )

    return result.head(top_n)


# =========================
# 5. Streamlit UI
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
    "条件に合ったアウトドア用品を推薦します。"
)

st.info(
    "例：冬の京都旅行で、軽くて暖かい服が欲しいです。"
)

user_query = st.text_input(
    "欲しい商品の条件を入力してください",
    placeholder="例：雨の日の旅行で使える、防水性が高くて軽い服が欲しいです。"
)


# =========================
# 6. 推薦結果
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
                f"## {rank}位：{product['product_name']}"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**カテゴリー：** {product['category']}"
                )

                if product["price"] != 0:
                    st.write(
                        f"**価格：** ¥{product['price']:,}"
                    )
                else:
                    st.write(
                        "**価格：** 要公式確認"
                    )

                st.write(
                    f"**特徴：** {product['features']}"
                )

                st.write(
                    f"**重量：** {product['weight']}"
                )

            with col2:

                st.write(
                    f"**防水性：** {product['waterproof']}"
                )

                st.write(
                    f"**保温性：** {product['warmth']}"
                )

                st.write(
                    f"**通気性：** {product['breathability']}"
                )

                st.write(
                    f"**収納性：** {product['packability']}"
                )

            st.write(
                f"**商品説明：** {product['description']}"
            )

            st.write(
                f"条件一致度：{product['similarity']:.3f}"
            )

            st.write(
                f"属性スコア：{product['attribute_score']:.3f}"
            )

            st.write(
                f"最終スコア：{product['final_score']:.3f}"
            )

            official_url = str(
                product.get("official_url", "")
            ).strip()

            if official_url and official_url.lower() != "nan":

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
                    "公式サイトの商品ページは現在登録されていません。"
                )

            st.divider()
