import os
import re
import base64
from typing import List, Tuple

from groq import Groq
import pandas as pd
import streamlit as st
from dotenv import load_dotenv


load_dotenv()


def _load_bg_base64(image_path: str) -> str:
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


def apply_centered_container_theme() -> None:
    bg_path = os.path.join(os.path.dirname(__file__), "AF54B2E8-69F2-428B-B.jpeg")
    bg_b64 = _load_bg_base64(bg_path)
    bg_css = (
        f"background-image: url('data:image/jpeg;base64,{bg_b64}');"
        if bg_b64
        else "background: linear-gradient(135deg, #172a45 0%, #355c7d 55%, #f8b195 100%);"
    )

    st.markdown(
        f"""
        <style>
        .stApp {{
            {bg_css}
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        [data-testid="stAppViewContainer"] {{
            background: rgba(7, 15, 30, 0.30);
        }}

        [data-testid="stAppViewContainer"] > .main {{
            display: flex;
            justify-content: center;
            padding: 36px 26px;
        }}

        [data-testid="stAppViewContainer"] > .main > div {{
            width: min(820px, 92%);
            background: rgba(8, 22, 44, 0.72);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.45);
            border-radius: 22px;
            box-shadow: 0 20px 55px rgba(0, 0, 0, 0.30);
            padding: 24px 28px 28px 28px;
        }}

        [data-testid="stAppViewContainer"] > .main > div,
        [data-testid="stAppViewContainer"] > .main > div * {{
            color: #ffffff !important;
        }}

        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stFileUploader > div,
        .stButton > button {{
            color: #ffffff !important;
        }}

        .stTextInput > div > div > input,
        .stSelectbox [data-baseweb="select"] > div,
        .stFileUploader [data-testid="stFileUploaderDropzone"] {{
            background: rgba(9, 24, 50, 0.52) !important;
            border-color: rgba(255, 255, 255, 0.35) !important;
        }}

        [data-testid="stDataFrame"] {{
            border-radius: 14px;
            overflow: hidden;
            background: rgba(9, 24, 50, 0.42);
        }}

        @media (max-width: 768px) {{
            [data-testid="stAppViewContainer"] > .main {{
                padding: 14px 10px;
            }}
            [data-testid="stAppViewContainer"] > .main > div {{
                border-radius: 14px;
                padding: 14px 12px 16px 12px;
                width: min(820px, 100%);
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Cluster Summary", layout="centered")
apply_centered_container_theme()
st.title("Tom Tat Theo Cluster")
st.caption("Tai file Excel, he thong doc toan bo content trong moi cluster va sinh 1 tom tat duy nhat.")


def normalize_text(x: object) -> str:
    s = "" if x is None else str(x)
    s = s.strip()
    return re.sub(r"\s+", " ", s)


def pick_columns(df: pd.DataFrame) -> Tuple[str, str]:
    lower_map = {str(c).strip().lower(): c for c in df.columns}

    cluster_candidates = ["cluster", "nhom", "group"]
    content_candidates = ["content", "noi_dung", "noidung", "response", "text"]

    cluster_col = None
    content_col = None

    for name in cluster_candidates:
        if name in lower_map:
            cluster_col = lower_map[name]
            break

    for name in content_candidates:
        if name in lower_map:
            content_col = lower_map[name]
            break

    if cluster_col is None and len(df.columns) >= 1:
        cluster_col = df.columns[0]
    if content_col is None and len(df.columns) >= 2:
        content_col = df.columns[1]

    if cluster_col is None or content_col is None:
        raise ValueError("Khong tim duoc cot cluster/content trong file.")

    return str(cluster_col), str(content_col)


def cluster_sort_key(value: str) -> Tuple[int, str]:
    s = str(value).strip()
    m = re.search(r"(\d+)", s)
    if m:
        return int(m.group(1)), s.lower()
    return 10**9, s.lower()


def enforce_summary_length(text: str, max_words: int = 40) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    # Keep only the first sentence to enforce single-sentence output.
    first_sentence = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)[0]
    words = first_sentence.split()
    if len(words) > max_words:
        first_sentence = " ".join(words[:max_words]).rstrip(".,;:!?") + "."
    if not first_sentence:
        return ""
    if first_sentence[-1] not in ".!?":
        first_sentence += "."
    return first_sentence


def summarize_cluster(client: Groq, model: str, cluster_id: str, texts: List[str]) -> str:
    all_contents = "\n".join([f"- {t}" for t in texts])
    prompt = (
        "Ban la chuyen gia phan tich survey. "
        "Duoi day la toan bo cau tra loi cua cung 1 cluster.\n\n"
        f"Cluster: {cluster_id}\n"
        f"So luong response: {len(texts)}\n"
        "Danh sach content:\n"
        f"{all_contents}\n\n"
        "Hay viet duy nhat 1 cau tom tat tong hop y chinh cua tat ca content trong cluster nay, bang tieng Viet, lien mach, ro nghia, do dai xap xi 40 tu. "
        "Khong qua 40 tu, khong liet ke, khong tach cum tu bang dau phay, khong dung gach dau dong."
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=90,
        messages=[
            {"role": "system", "content": "Ban la chuyen gia phan tich survey bang tieng Viet."},
            {"role": "user", "content": prompt},
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    return enforce_summary_length(text, max_words=40)


def fallback_summary(cluster_id: str, texts: List[str]) -> str:
    fallback = (
        f"Cluster {cluster_id} gom {len(texts)} phan hoi tuong doi dong nhat, nhung he thong AI dang bi gioi han nen tam thoi can kiem tra thu cong de tom tat chinh xac."
    )
    return enforce_summary_length(fallback, max_words=40)


uploaded = st.file_uploader("Tai file Excel (.xlsx)", type=["xlsx"])
run_btn = st.button("Tom tat", type="primary")

if run_btn:
    if uploaded is None:
        st.error("Ban can tai file Excel truoc khi tom tat.")
        st.stop()

    try:
        xls = pd.ExcelFile(uploaded)
        df = xls.parse(xls.sheet_names[0]).copy()
    except Exception as ex:
        st.error(f"Khong doc duoc file Excel: {ex}")
        st.stop()

    if df.empty:
        st.error("File khong co du lieu.")
        st.stop()

    try:
        cluster_col, content_col = pick_columns(df)
    except Exception as ex:
        st.error(str(ex))
        st.stop()

    work = df[[cluster_col, content_col]].copy()
    work[cluster_col] = work[cluster_col].map(normalize_text)
    work[content_col] = work[content_col].map(normalize_text)
    work = work[(work[cluster_col] != "") & (work[content_col] != "")]

    if work.empty:
        st.error("Khong co dong hop le sau khi lam sach du lieu.")
        st.stop()

    grouped = work.groupby(cluster_col)[content_col].apply(list).reset_index(name="all_contents")
    grouped["_sort_key"] = grouped[cluster_col].map(cluster_sort_key)
    grouped = grouped.sort_values(by="_sort_key", ascending=True).drop(columns=["_sort_key"])

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        st.error("Thieu GROQ_API_KEY. Hay dat bien moi truong roi chay lai app.")
        st.stop()

    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()
    client = Groq(api_key=api_key)

    rows = []
    progress = st.progress(0.0)
    quota_exhausted = False

    for i, row in grouped.reset_index(drop=True).iterrows():
        cluster_id = str(row[cluster_col])
        texts = row["all_contents"]

        if quota_exhausted:
            summary = fallback_summary(cluster_id, texts)
        else:
            try:
                summary = summarize_cluster(client, model_name, cluster_id, texts)
                if not summary:
                    summary = fallback_summary(cluster_id, texts)
            except Exception as ex:
                msg = str(ex).lower()
                if "429" in msg or "quota" in msg or "rate" in msg:
                    quota_exhausted = True
                    st.warning("Groq bi gioi han quota/rate-limit. Cac cluster con lai se dung fallback.")
                summary = fallback_summary(cluster_id, texts)

        rows.append({"cluster": cluster_id, "tom_tat": summary})
        progress.progress((i + 1) / len(grouped))

    result_df = pd.DataFrame(rows)
    st.dataframe(result_df[["cluster", "tom_tat"]], use_container_width=True, hide_index=True)
