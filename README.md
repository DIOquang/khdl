# Survey Cluster Summarizer

App phân tích survey và tóm tắt ý nghĩa chủ đề chính của các cluster câu trả lời, dùng AI (Groq API).

---

## 🎯 2 Cách Chạy App

Project này có **2 giao diện khác nhau**:

### 🔵 Cách 1: Streamlit App (Port 8501) - Development

Giao diện đơn giản, tích hợp trong Streamlit. Phù hợp phát triển, test nhanh.

```bash
streamlit run app.py
```

**Truy cập**: http://localhost:8501

### 🔴 Cách 2: Flask Web (Port 8502) - Production

Giao diện web đẹp, HTML/CSS/JS từ folder `024 - Website Header with Forms copy/Final`. Phù hợp demo, triển khai.

```bash
cd "024 - Website Header with Forms copy/Final"
python server.py
```

**Truy cập**: http://localhost:8502

---

## ⚙️ Cài Đặt (Chỉ Làm 1 Lần)

### 1. Clone Repository

```bash
git clone https://github.com/DIOquang/khdl.git
cd khdl
```

### 2. Tạo Virtual Environment

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Cài Dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu Hình API Key (BẮT BUỘC)

**Bước này rất quan trọng!** Nếu không làm, app sẽ báo lỗi "Thiếu GROQ_API_KEY".

#### Cách A: Tạo file `.env`

```bash
cp .env.example .env
```

Sau đó mở file `.env` và sửa:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Lấy API key:
1. Đăng ký tại https://groq.com
2. Vào API Console
3. Tạo API Key
4. Copy vào `.env`

#### Cách B: Set biến môi trường trực tiếp (Temporary)

```bash
# macOS/Linux
export GROQ_API_KEY="your_actual_groq_api_key_here"

# Windows PowerShell
$env:GROQ_API_KEY = "your_actual_groq_api_key_here"
```

---

## ▶️ Chạy App

### Cách 1: Streamlit (Port 8501)

```bash
streamlit run app.py
```

Giao diện:
- Upload file Excel
- Chọn cột Cluster
- Click "Phân tích và tóm tắt"
- Xem kết quả trong bảng

### Cách 2: Flask Web (Port 8502)

```bash
cd "024 - Website Header with Forms copy/Final"
python server.py
```

Hoặc từ thư mục root:

```bash
python "024 - Website Header with Forms copy/Final/server.py"
```

Giao diện:
- Upload file Excel (.xlsx)
- Chọn model AI từ dropdown
- Click "Tóm tắt"
- Xem bảng kết quả (2 cột: Cluster, Tóm tắt)

---

## 📊 Định Dạng Input

**File Excel** cần có:
- **Cột "Cluster"**: Tên cluster (Cluster 1, Cluster 2, ...)
- **Cột nội dung**: Câu trả lời survey (bất kỳ tên cột nào cũng được, app sẽ tự detect)

**Ví dụ**:
| Cluster    | Content                           |
|------------|-----------------------------------|
| Cluster 1  | Sản phẩm chất lượng, giá tốt      |
| Cluster 1  | Dịch vụ khách hàng nhanh chóng    |
| Cluster 2  | Giao hàng chậm                    |
| Cluster 2  | Packaging không tốt                |

---

## 📤 Output

**Streamlit**: Tải file CSV kết quả từ app

**Flask**: Bảng hiển thị 2 cột:
- **cluster**: Tên cluster
- **tom_tat**: Tóm tắt 1 câu, tối đa 40 từ

**Ví dụ output**:
| cluster    | tom_tat                                                           |
|------------|-------------------------------------------------------------------|
| Cluster 1  | Khách hàng đánh giá cao chất lượng sản phẩm và dịch vụ nhanh.    |
| Cluster 2  | Nhu cầu cải thiện tốc độ giao hàng và chất lượng bao bì.        |

---

## 🔗 Chi Tiết Thêm

- **Deployment Guide**: Xem [DEPLOYMENT.md](DEPLOYMENT.md) để deploy lên cloud (Streamlit Cloud, Heroku, Railway, v.v.)
- **Repository**: https://github.com/DIOquang/khdl
- **API Provider**: Groq (llama-3.1-8b-instant)
- `stt`: so thu tu dung theo dong trong file goc.
- `cluster_goc`: gia tri cluster ban dau trong file.
- `content_goc`: noi dung cau tra loi goc.
- `ket_qua_tom_tat_gemini`: noi dung tom tat cua cluster do Gemini sinh.

## Ghi chu

- Neu khong nhap API key, app van chay va tao tom tat fallback (khong goi API).
- Model mac dinh: `gemini-2.5-flash` (Gemini) va `gpt-4.1-mini` (OpenAI).
