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

def calculate_text_score(user_query, product):

    query = user_query.lower()

    text = " ".join([
        str(product.get("product_name", "")),
        str(product.get("category", "")),
        str(product.get("material", "")),
        str(product.get("season", "")),
        str(product.get("use_case", "")),
        str(product.get("features", "")),
        str(product.get("description", ""))
    ]).lower()

    keywords = [
        "夏",
        "冬",
        "春",
        "秋",
        "暑い",
        "寒い",
        "涼しい",
        "暖かい",
        "防寒",
        "保温",
        "軽い",
        "軽量",
        "持ち運び",
        "旅行",
        "観光",
        "雨",
        "防水",
        "レイン",
        "通気性",
        "蒸れない",
        "アウトドア",
        "登山",
        "キャンプ",
        "ハイキング",
        "ジャケット",
        "シャツ",
        "パンツ",
        "バッグ",
        "リュック",
        "シューズ",
        "ウェア"
    ]

    matched_keywords = []

    for keyword in keywords:

        if keyword in query and keyword in text:
            matched_keywords.append(keyword)

    score = len(matched_keywords) * 0.10

    return min(score, 1.0)


# =========================
# 3. 商品屬性評分
# =========================

def calculate_attribute_score(user_query, product):

    query = user_query.lower()

    score = 0.0

    # =========================
    # 季節：冬
    # =========================

    if any(
        keyword in query
        for keyword in [
            "冬",
            "寒い",
            "暖かい",
            "防寒"
        ]
    ):

        if "冬" in str(product["season"]):
            score += 0.20

        if product["warmth"] == "高":
            score += 0.15

        elif product["warmth"] == "中":
            score += 0.08

    # =========================
    # 季節：夏
    # =========================

    if any(
        keyword in query
        for keyword in [
            "夏",
            "暑い",
            "涼しい"
        ]
    ):

        if "夏" in str(product["season"]):
            score += 0.20

        if product["breathability"] == "非常に高い":
            score += 0.15

        elif product["breathability"] == "高":
            score += 0.10

    # =========================
    # 季節：春
    # =========================

    if "春" in query:

        if "春" in str(product["season"]):
            score += 0.20

    # =========================
    # 季節：秋
    # =========================

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

            weight_text = str(
                product["weight"]
            )

            weight = float(
                re.sub(
                    r"[^0-9.]",
                    "",
                    weight_text
                )
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

    return max(
        0.0,
        score
    )


# =========================
# 4. 推薦處理
# =========================

def recommend_products(
    user_query,
    top_n=3
):

    result = df.copy()

    # =========================
    # 文字條件
    # =========================

    result["similarity"] = result.apply(
        lambda product:
        calculate_text_score(
            user_query,
            product
        ),
        axis=1
    )

    # =========================
    # 商品屬性
    # =========================

    result["attribute_score"] = result.apply(
        lambda product:
        calculate_attribute_score(
            user_query,
            product
        ),
        axis=1
    )

    # =========================
    # 基本最終分數
    # =========================

    result["final_score"] = (
        result["similarity"] * 0.60
        + result["attribute_score"] * 0.40
    )

    # =========================
    # 重量差異作為細微排序
    # 越輕的商品，分數稍微高一點
    # =========================

    def get_weight_score(weight):

        try:

            weight_text = str(weight)

            weight_value = float(
                re.sub(
                    r"[^0-9.]",
                    "",
                    weight_text
                )
            )

            if weight_value <= 200:
                return 0.010

            elif weight_value <= 300:
                return 0.008

            elif weight_value <= 500:
                return 0.005

            else:
                return 0.002

        except:

            return 0.0

    result["weight_bonus"] = result["weight"].apply(
        get_weight_score
    )

    # =========================
    # 加入重量微調分數
    # =========================

    result["final_score"] = (
        result["final_score"]
        + result["weight_bonus"]
    )

    # =========================
    # 排序
    # =========================

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

            # =========================
            # 左側
            # =========================

            with col1:

                st.write(
                    f"**カテゴリー：** {product['category']}"
                )

                st.write(
                    f"**価格：** ¥{int(float(product['price'])):,}"
                )

                st.write(
                    f"**特徴：** {product['features']}"
                )

                st.write(
                    f"**重量：** {product['weight']}"
                )

            # =========================
            # 右側
            # =========================

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

            # =========================
            # 商品説明
            # =========================

            st.write(
                f"**商品説明：** {product['description']}"
            )

            # =========================
            # 評分
            # =========================

            st.write(
                f"条件一致度：{product['similarity']:.3f}"
            )

            st.write(
                f"属性スコア：{product['attribute_score']:.3f}"
            )

            st.write(
                f"最終スコア：{product['final_score']:.3f}"
            )

            # =========================
            # 官方網站
            # =========================

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
                    "公式サイトの商品ページは現在登録されていません。"
                )

            st.divider()
