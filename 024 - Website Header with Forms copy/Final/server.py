import os
import re
from typing import List, Tuple

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from groq import Groq


load_dotenv()

BASE_DIR = os.path.dirname(__file__)
app = Flask(__name__, static_folder=BASE_DIR)


def normalize_text(x: object) -> str:
    s = "" if x is None else str(x)
    return re.sub(r"\s+", " ", s.strip())


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
        "Hay viet duy nhat 1 cau tom tat tong hop y chinh cua tat ca content trong cluster nay, "
        "bang tieng Viet, lien mach, ro nghia, do dai xap xi 40 tu. "
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
        f"Cluster {cluster_id} gom {len(texts)} phan hoi tuong doi dong nhat, "
        "nhung he thong AI dang bi gioi han nen tam thoi can kiem tra thu cong de tom tat chinh xac."
    )
    return enforce_summary_length(fallback, max_words=40)


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/<path:path>")
def static_files(path: str):
    return send_from_directory(BASE_DIR, path)


@app.post("/api/summarize")
def summarize_api():
    if "file" not in request.files:
        return jsonify({"error": "Thieu file upload."}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".xlsx"):
        return jsonify({"error": "Chi ho tro file .xlsx"}), 400

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        return jsonify({"error": "Thieu GROQ_API_KEY trong moi truong."}), 500

    model_name = (request.form.get("model") or "llama-3.1-8b-instant").strip()

    try:
        xls = pd.ExcelFile(file)
        df = xls.parse(xls.sheet_names[0]).copy()
    except Exception as ex:
        return jsonify({"error": f"Khong doc duoc file Excel: {ex}"}), 400

    if df.empty:
        return jsonify({"error": "File khong co du lieu."}), 400

    try:
        cluster_col, content_col = pick_columns(df)
    except Exception as ex:
        return jsonify({"error": str(ex)}), 400

    work = df[[cluster_col, content_col]].copy()
    work[cluster_col] = work[cluster_col].map(normalize_text)
    work[content_col] = work[content_col].map(normalize_text)
    work = work[(work[cluster_col] != "") & (work[content_col] != "")]

    if work.empty:
        return jsonify({"error": "Khong co dong hop le sau khi lam sach."}), 400

    grouped = work.groupby(cluster_col)[content_col].apply(list).reset_index(name="all_contents")
    grouped["_sort_key"] = grouped[cluster_col].map(cluster_sort_key)
    grouped = grouped.sort_values(by="_sort_key", ascending=True).drop(columns=["_sort_key"])

    client = Groq(api_key=api_key)
    rows = []
    quota_exhausted = False

    for _, row in grouped.iterrows():
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
                summary = fallback_summary(cluster_id, texts)

        rows.append({"cluster": cluster_id, "tom_tat": summary})

    return jsonify({"rows": rows})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8502, debug=True)
