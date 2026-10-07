import streamlit as st
import pandas as pd
import re


# =========================================================
# 1. 載入商品資料
# =========================================================

df = pd.read_csv(
    "products.csv",
    encoding="utf-8-sig"
)


# =========================================================
# 2. 整理價格
# =========================================================

def clean_price(value):

    try:

        text = str(value).strip()

        if text == "" or text.lower() == "nan":
            return 0

        text = (
            text
            .replace(",", "")
            .replace("¥", "")
            .replace("円", "")
        )

        match = re.search(
            r"\d+",
            text
        )

        if match:
            return float(match.group())

        return 0

    except:
        return 0


df["price"] = df["price"].apply(clean_price)


# =========================================================
# 3. 重量解析
# =========================================================

def get_weight(weight):

    text = str(weight)

    match = re.search(
        r"(\d+)\s*g",
        text
    )

    if match:
        return int(match.group(1))

    return None


# =========================================================
# 4. 條件一致度
# =========================================================

def calculate_match_score(
    user_query,
    product
):

    query = user_query.lower()

    score = 0.0
    max_score = 0.0

    # -----------------------------------------------------
    # 防水
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "雨",
            "雨の日",
            "防水",
            "レイン"
        ]
    ):

        max_score += 30

        waterproof = str(
            product["waterproof"]
        )

        if waterproof == "非常に高い":
            score += 30

        elif waterproof == "高":
            score += 24

        elif waterproof == "中":
            score += 12

        elif waterproof == "低":
            score += 4

    # -----------------------------------------------------
    # 輕量
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "軽い",
            "軽量",
            "持ち運び"
        ]
    ):

        max_score += 25

        features = str(
            product["features"]
        )

        # 商品標示輕量
        if "軽量" in features:
            score += 15

        # 實際重量
        grams = get_weight(
            product["weight"]
        )

        if grams is not None:

            if grams <= 200:
                score += 10

            elif grams <= 300:
                score += 8

            elif grams <= 500:
                score += 5

            else:
                score += 2

    # -----------------------------------------------------
    # 旅行
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "旅行",
            "観光"
        ]
    ):

        max_score += 15

        if "旅行" in str(
            product["use_case"]
        ):
            score += 15

    # -----------------------------------------------------
    # 登山
    # -----------------------------------------------------

    if "登山" in query:

        max_score += 15

        if "登山" in str(
            product["use_case"]
        ):
            score += 15

    # -----------------------------------------------------
    # 暖かさ
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "暖かい",
            "暖かく",
            "防寒",
            "保温",
            "寒い"
        ]
    ):

        max_score += 20

        warmth = str(
            product["warmth"]
        )

        if warmth == "高":
            score += 20

        elif warmth == "中":
            score += 10

        elif warmth == "低":
            score += 0

    # -----------------------------------------------------
    # 涼しさ・通氣性
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "涼しい",
            "暑い",
            "通気性",
            "蒸れない"
        ]
    ):

        max_score += 20

        breathability = str(
            product["breathability"]
        )

        if breathability == "非常に高い":
            score += 20

        elif breathability == "高":
            score += 15

        elif breathability == "中":
            score += 8

    # -----------------------------------------------------
    # ストレッチ
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "ストレッチ",
            "動きやすい"
        ]
    ):

        max_score += 10

        features = str(
            product["features"]
        )

        if (
            "ストレッチ" in features
            or
            "動きやすい" in features
        ):
            score += 10

    # -----------------------------------------------------
    # コンパクト
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "コンパクト",
            "収納"
        ]
    ):

        max_score += 10

        packability = str(
            product["packability"]
        )

        if packability == "非常に高い":
            score += 10

        elif packability == "高い":
            score += 8

        elif packability == "中":
            score += 4

    # -----------------------------------------------------
    # 計算
    # -----------------------------------------------------

    if max_score == 0:
        return 0.0

    return score / max_score


# =========================================================
# 5. 商品屬性分數
# =========================================================

def calculate_attribute_score(
    user_query,
    product
):

    query = user_query.lower()

    score = 0.0

    # -----------------------------------------------------
    # 防水
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "雨",
            "雨の日",
            "防水",
            "レイン"
        ]
    ):

        waterproof = str(
            product["waterproof"]
        )

        if waterproof == "非常に高い":
            score += 0.30

        elif waterproof == "高":
            score += 0.24

        elif waterproof == "中":
            score += 0.12

        elif waterproof == "低":
            score += 0.03

    # -----------------------------------------------------
    # 輕量
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "軽い",
            "軽量",
            "持ち運び"
        ]
    ):

        features = str(
            product["features"]
        )

        if "軽量" in features:
            score += 0.15

        grams = get_weight(
            product["weight"]
        )

        if grams is not None:

            if grams <= 200:
                score += 0.10

            elif grams <= 300:
                score += 0.07

            elif grams <= 500:
                score += 0.04

    # -----------------------------------------------------
    # 暖かさ
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
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
            score += 0.12

    # -----------------------------------------------------
    # 通氣性
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
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
            score += 0.10

    # -----------------------------------------------------
    # 旅行
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "旅行",
            "観光"
        ]
    ):

        if "旅行" in str(
            product["use_case"]
        ):
            score += 0.10

    # -----------------------------------------------------
    # 登山
    # -----------------------------------------------------

    if "登山" in query:

        if "登山" in str(
            product["use_case"]
        ):
            score += 0.10

    # -----------------------------------------------------
    # ストレッチ
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "ストレッチ",
            "動きやすい"
        ]
    ):

        features = str(
            product["features"]
        )

        if (
            "ストレッチ" in features
            or
            "動きやすい" in features
        ):
            score += 0.15

    # -----------------------------------------------------
    # コンパクト
    # -----------------------------------------------------

    if any(
        k in query
        for k in [
            "コンパクト",
            "収納"
        ]
    ):

        if product["packability"] == "非常に高い":
            score += 0.10

        elif product["packability"] == "高い":
            score += 0.08

        elif product["packability"] == "中":
            score += 0.04

    return min(
        score,
        1.0
    )


# =========================================================
# 6. 商品推薦
# =========================================================

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

    # 最終分數
    result["final_score"] = (
        result["similarity"] * 0.60
        +
        result["attribute_score"] * 0.40
    )

    # 排序
    result = result.sort_values(
        by=[
            "final_score",
            "similarity",
            "attribute_score"
        ],
        ascending=False
    )

    return result.head(top_n)


# =========================================================
# 7. Streamlit UI
# =========================================================

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


# =========================================================
# 8. 推薦結果
# =========================================================

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

            # -------------------------------------------------
            # 左側
            # -------------------------------------------------

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

            # -------------------------------------------------
            # 右側
            # -------------------------------------------------

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

            # -------------------------------------------------
            # 官方網站
            # -------------------------------------------------

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
