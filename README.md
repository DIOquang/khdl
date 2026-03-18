# Survey Cluster Theme Summarizer (Streamlit)

Demo app de tom tat y nghia chu de chinh cua cac cluster cau tra loi survey bang AI model API.

Ho tro 2 nha cung cap AI:
- Google Gemini
- OpenAI

## 1) Cai dat

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Cau hinh API key

```bash
cp .env.example .env
# sua OPENAI_API_KEY trong .env
# hoac them GOOGLE_API_KEY neu dung Gemini
```

Hoac dat truc tiep bien moi truong:

```bash
export OPENAI_API_KEY="..."
```

## 3) Chay app

```bash
streamlit run app.py
```

## 4) Cach dung

1. Upload file Excel survey hoac de mac dinh file `ResultTestDataOilSurveyVN.xlsx`.
2. Chon sheet va cot text (`Content`).
3. Chon 1 trong 2 che do:
   - Dung cluster co san (`Cluster`).
   - Bat `Tu dong phan cum` de app tu gom cum voi KMeans.
4. Chon nha cung cap AI trong sidebar (Google Gemini/OpenAI), nhap API key va model.
5. Bam `Phan tich va tom tat`.
6. Tai ket qua CSV sau khi app sinh `theme_title`, `summary`, `insight` cho tung cluster.

## Dinh dang output chinh

App xuat bang ket qua theo tung dong goc voi 4 cot:
- `stt`: so thu tu dung theo dong trong file goc.
- `cluster_goc`: gia tri cluster ban dau trong file.
- `content_goc`: noi dung cau tra loi goc.
- `ket_qua_tom_tat_gemini`: noi dung tom tat cua cluster do Gemini sinh.

## Ghi chu

- Neu khong nhap API key, app van chay va tao tom tat fallback (khong goi API).
- Model mac dinh: `gemini-2.5-flash` (Gemini) va `gpt-4.1-mini` (OpenAI).
