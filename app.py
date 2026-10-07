import streamlit as st
import pandas as pd
import re


# =========================================================
# 1. 基本設定
# =========================================================

st.set_page_config(
    page_title="AI Outdoor Recommendation",
    page_icon="🏕️",
    layout="wide"
)


# =========================================================
# 2. 載入商品資料
# =========================================================

@st.cache_data
def load_products():

    data = pd.read_csv(
        "products.csv",
        encoding="utf-8-sig"
    )

    return data


df = load_products()


# =========================================================
# 3. 價格整理
# =========================================================

def clean_price(value):

    try:

        text = str(value).strip()

        if (
            text == ""
            or text.lower() == "nan"
        ):
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
            return float(
                match.group()
            )

        return 0

    except Exception:
        return 0


df["price"] = df["price"].apply(
    clean_price
)


# =========================================================
# 4. 重量解析
# =========================================================

def get_weight(weight):

    text = str(weight)

    match = re.search(
        r"(\d+)\s*g",
        text
    )

    if match:
        return int(
            match.group(1)
        )

    return None


# =========================================================
# 5. 商品類型判斷
# =========================================================

def calculate_category_score(
    user_query,
    product
):

    query = str(
        user_query
    ).lower()

    product_name = str(
        product["product_name"]
    ).lower()

    category = str(
        product["category"]
    ).lower()

    score = 0.0

    # -----------------------------------------------------
    # レインジャケット
    # -----------------------------------------------------

    if (
        "レインジャケット" in query
        or
        "レイン ジャケット" in query
    ):

        if (
            "ジャケット" in product_name
            and
            "レインウェア" in category
        ):
            score += 0.50

        elif "ジャケット" in product_name:
            score += 0.20

    # -----------------------------------------------------
    # ジャケット
    # -----------------------------------------------------

    elif "ジャケット" in query:

        if "ジャケット" in product_name:
            score += 0.50

    # -----------------------------------------------------
    # レインパンツ
    # -----------------------------------------------------

    if (
        "レインパンツ" in query
        or
        "レイン パンツ" in query
    ):

        if (
            "パンツ" in product_name
            and
            "レインウェア" in category
        ):
            score += 0.50

        elif "パンツ" in product_name:
            score += 0.20

    # -----------------------------------------------------
    # パンツ
    # -----------------------------------------------------

    elif "パンツ" in query:

        if "パンツ" in product_name:
            score += 0.50

    # -----------------------------------------------------
    # パーカー
    # -----------------------------------------------------

    if "パーカー" in query:

        if "パーカー" in product_name:
            score += 0.50

        elif "パーカー" in category:
            score += 0.40

    # -----------------------------------------------------
    # ダウン
    # -----------------------------------------------------

    if "ダウン" in query:

        if "ダウン" in product_name:
            score += 0.50

        elif "ダウン" in category:
            score += 0.40

    # -----------------------------------------------------
    # シャツ
    # -----------------------------------------------------

    if "シャツ" in query:

        if "シャツ" in product_name:
            score += 0.50

        elif "シャツ" in category:
            score += 0.40

    # -----------------------------------------------------
    # レインウェア
    # -----------------------------------------------------

    if (
        "レインウェア" in query
        or
        "雨具" in query
    ):

        if "レインウェア" in category:
            score += 0.25

    # -----------------------------------------------------
    # 「服」
    # -----------------------------------------------------

    if "服" in query:

        if "ジャケット" in product_name:
            score += 0.25

        elif "パーカー" in category:
            score += 0.22

        elif "ダウン" in category:
            score += 0.22

        elif "フリース" in category:
            score += 0.20

        elif "シャツ" in category:
            score += 0.20

        elif "パンツ" in product_name:
            score += 0.05

    return min(
        score,
        1.0
    )


# =========================================================
# 6. 防水スコア
# =========================================================

def get_waterproof_score(
    product
):

    waterproof = str(
        product["waterproof"]
    )

    if waterproof == "非常に高い":
        return 1.00

    if waterproof == "高":
        return 0.80

    if waterproof == "中":
        return 0.40

    if waterproof == "低":
        return 0.10

    return 0.00


# =========================================================
# 7. 重量スコア
# =========================================================

def get_weight_score(
    product
):

    grams = get_weight(
        product["weight"]
    )

    if grams is None:
        return 0.00

    if grams <= 180:
        return 1.00

    if grams <= 250:
        return 0.90

    if grams <= 300:
        return 0.75

    if grams <= 400:
        return 0.50

    if grams <= 500:
        return 0.30

    return 0.10


# =========================================================
# 8. 保暖スコア
# =========================================================

def get_warmth_score(
    product
):

    warmth = str(
        product["warmth"]
    )

    if warmth == "高":
        return 1.00

    if warmth == "中":
        return 0.50

    return 0.00


# =========================================================
# 9. 通氣性スコア
# =========================================================

def get_breathability_score(
    product
):

    breathability = str(
        product["breathability"]
    )

    if breathability == "非常に高い":
        return 1.00

    if breathability == "高":
        return 0.80

    if breathability == "中":
        return 0.50

    return 0.20


# =========================================================
# 10. 収納性スコア
# =========================================================

def get_packability_score(
    product
):

    packability = str(
        product["packability"]
    )

    if packability == "非常に高い":
        return 1.00

    if packability == "高い":
        return 0.80

    if packability == "中":
        return 0.50

    return 0.00


# =========================================================
# 11. 條件一致度
# =========================================================

def calculate_match_score(
    user_query,
    product
):

    query = str(
        user_query
    ).lower()

    score = 0.0
    max_score = 0.0

    # -----------------------------------------------------
    # 防水
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "雨",
            "雨の日",
            "防水",
            "レイン"
        ]
    ):

        max_score += 30

        score += (
            get_waterproof_score(product)
            * 30
        )

    # -----------------------------------------------------
    # 輕量 / 薄い
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "軽い",
            "軽量",
            "薄い",
            "持ち運び"
        ]
    ):

        max_score += 25

        features = str(
            product["features"]
        )

        # 有輕量特徵
        if "軽量" in features:
            score += 10

        # 實際重量
        score += (
            get_weight_score(product)
            * 15
        )

    # -----------------------------------------------------
    # 旅行
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
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
    # 暖かい / 防寒
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "暖かい",
            "暖かく",
            "防寒",
            "保温",
            "寒い"
        ]
    ):

        max_score += 20

        score += (
            get_warmth_score(product)
            * 20
        )

    # -----------------------------------------------------
    # 涼しい / 通氣性
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "涼しい",
            "暑い",
            "通気性",
            "蒸れない"
        ]
    ):

        max_score += 20

        score += (
            get_breathability_score(product)
            * 20
        )

    # -----------------------------------------------------
    # ストレッチ
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
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
        word in query
        for word in [
            "コンパクト",
            "収納"
        ]
    ):

        max_score += 10

        score += (
            get_packability_score(product)
            * 10
        )

    # -----------------------------------------------------
    # 沒有條件
    # -----------------------------------------------------

    if max_score == 0:
        return 0.0

    return min(
        score / max_score,
        1.0
    )


# =========================================================
# 12. 屬性分數
# =========================================================

def calculate_attribute_score(
    user_query,
    product
):

    query = str(
        user_query
    ).lower()

    score = 0.0
    count = 0

    # -----------------------------------------------------
    # 防水
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "雨",
            "雨の日",
            "防水",
            "レイン"
        ]
    ):

        score += (
            get_waterproof_score(product)
        )

        count += 1

    # -----------------------------------------------------
    # 輕量
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "軽い",
            "軽量",
            "薄い",
            "持ち運び"
        ]
    ):

        score += (
            get_weight_score(product)
        )

        count += 1

    # -----------------------------------------------------
    # 暖かさ
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "暖かい",
            "暖かく",
            "防寒",
            "保温",
            "寒い"
        ]
    ):

        score += (
            get_warmth_score(product)
        )

        count += 1

    # -----------------------------------------------------
    # 通氣性
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "涼しい",
            "暑い",
            "通気性",
            "蒸れない"
        ]
    ):

        score += (
            get_breathability_score(product)
        )

        count += 1

    # -----------------------------------------------------
    # 旅行
    # -----------------------------------------------------

    if any(
        word in query
        for word in [
            "旅行",
            "観光"
        ]
    ):

        if "旅行" in str(
            product["use_case"]
        ):
            score += 1.0
        else:
            score += 0.0

        count += 1

    # -----------------------------------------------------
    # 登山
    # -----------------------------------------------------

    if "登山" in query:

        if "登山" in str(
            product["use_case"]
        ):
            score += 1.0

        count += 1

    # -----------------------------------------------------
    # 結果
    # -----------------------------------------------------

    if count == 0:
        return 0.0

    return min(
        score / count,
        1.0
    )


# =========================================================
# 13. 商品推薦
# =========================================================

def recommend_products(
    user_query,
    top_n=3
):

    result = df.copy()

    # -----------------------------------------------------
    # 條件一致度
    # -----------------------------------------------------

    result["similarity"] = result.apply(
        lambda product:
        calculate_match_score(
            user_query,
            product
        ),
        axis=1
    )

    # -----------------------------------------------------
    # 屬性分數
    # -----------------------------------------------------

    result["attribute_score"] = result.apply(
        lambda product:
        calculate_attribute_score(
            user_query,
            product
        ),
        axis=1
    )

    # -----------------------------------------------------
    # 商品類型
    # -----------------------------------------------------

    result["category_score"] = result.apply(
        lambda product:
        calculate_category_score(
            user_query,
            product
        ),
        axis=1
    )

    # -----------------------------------------------------
    # 最終分數
    # -----------------------------------------------------

    result["final_score"] = (
        result["similarity"] * 0.50
        +
        result["attribute_score"] * 0.30
        +
        result["category_score"] * 0.20
    )

    # -----------------------------------------------------
    # 排序
    # -----------------------------------------------------

    result = result.sort_values(
        by=[
            "final_score",
            "category_score",
            "attribute_score",
            "similarity"
        ],
        ascending=False
    )

    return result.head(
        top_n
    )


# =========================================================
# 14. Streamlit UI
# =========================================================

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


# =========================================================
# 15. 使用者輸入
# =========================================================

user_query = st.text_input(
    "欲しい商品の条件を入力してください",
    placeholder=(
        "例：雨の日の旅行で使える、"
        "防水性が高くて軽い服が欲しいです。"
    )
)


# =========================================================
# 16. 推薦按鈕
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

        # -------------------------------------------------
        # 顯示前三名
        # -------------------------------------------------

        for rank, (_, product) in enumerate(
            recommendations.iterrows(),
            start=1
        ):

            st.markdown(
                f"## {rank}位："
                f"{product['product_name']}"
            )

            col1, col2 = st.columns(2)

            # ---------------------------------------------
            # 左側
            # ---------------------------------------------

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

            # ---------------------------------------------
            # 右側
            # ---------------------------------------------

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

            # ---------------------------------------------
            # 商品説明
            # ---------------------------------------------

            st.write(
                f"**商品説明：** "
                f"{product['description']}"
            )

            # ---------------------------------------------
            # 評分
            # ---------------------------------------------

            st.write(
                f"条件一致度："
                f"{product['similarity']:.3f}"
            )

            st.write(
                f"属性スコア："
                f"{product['attribute_score']:.3f}"
            )

            st.write(
                f"商品タイプスコア："
                f"{product['category_score']:.3f}"
            )

            st.write(
                f"最終スコア："
                f"{product['final_score']:.3f}"
            )

            # ---------------------------------------------
            # 官方網站
            # ---------------------------------------------

            official_url = str(
                product.get(
                    "official_url",
                    ""
                )
            ).strip()

            if (
                official_url
                and
                official_url.lower() != "nan"
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
