# Deployment Guide - Survey Cluster Summarizer

Hướng dẫn deploy project app phân tích survey và tóm tắt cluster theo AI.

---

## 📋 Yêu cầu hệ thống

- **Python**: 3.8+
- **pip** hoặc **conda**: Package manager
- **Git**: Để clone/pull code
- **API Key**: Groq API key (groq.com)

---

## 🚀 Deployment Options

Dự án này có **2 cách chạy**:

### Option 1: Streamlit App (Development/Prototyping)
- Chạy trực tiếp trên localhost:8501
- Giao diện đơn giản, tích hợp UI Streamlit
- Dễ phát triển

### Option 2: Flask Web + HTML/CSS/JS (Production)
- Backend Flask trên localhost:8502
- Frontend HTML/CSS/JS tích hợp template
- Phù hợp triển khai lên hosting

---

## 💻 Local Development Setup

### 1. Clone repository

```bash
git clone https://github.com/DIOquang/khdl.git
cd khdl
```

### 2. Tạo virtual environment

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Sau đó chỉnh sửa `.env` theo API key của bạn:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
```

Lấy GROQ_API_KEY:
1. Đăng ký tại [groq.com](https://groq.com)
2. Vào trang API Console
3. Tạo API Key mới
4. Copy key vào file `.env`

### 5. Chuẩn bị dữ liệu

- File Excel `ResultTestDataOilSurveyVN.xlsx` phải có trong thư mục root
- App sẽ tự detect cột "Cluster" và cột nội dung câu trả lời

---

## ▶️ Chạy Locally

### Streamlit App (Port 8501)

```bash
streamlit run app.py
```

Hoặc với các tùy chọn:

```bash
streamlit run app.py --server.port 8501 --server.headless false
```

**Truy cập**: http://localhost:8501

### Flask Web Integration (Port 8502)

```bash
cd "024 - Website Header with Forms copy/Final"
python server.py
```

**Truy cập**: http://localhost:8502

Hoặc chạy trực tiếp từ root:

```bash
python "024 - Website Header with Forms copy/Final/server.py"
```

---

## ☁️ Deploy Lên Cloud

### A. Streamlit Cloud (Recommended for Streamlit app)

1. **Push code lên GitHub** (đã hoàn thành)

2. **Deploy trên Streamlit Cloud**:
   - Truy cập [streamlit.io/cloud](https://share.streamlit.io)
   - Đăng nhập bằng GitHub account
   - Click "New app"
   - Chọn repository: `DIOquang/khdl`
   - Chọn branch: `main`
   - Chọn file: `app.py`
   - Click "Deploy"

3. **Cấu hình secrets**:
   - Trong Streamlit Cloud dashboard, đi tới "Advanced settings"
   - Thêm secrets:
     ```
     GROQ_API_KEY = "your_api_key"
     GROQ_MODEL = "llama-3.1-8b-instant"
     ```

### B. Heroku (Flask App + Server)

1. **Cài đặt Heroku CLI**:
   ```bash
   brew install heroku/brew/heroku  # macOS
   # hoặc download từ heroku.com
   ```

2. **Đăng nhập**:
   ```bash
   heroku login
   ```

3. **Tạo app**:
   ```bash
   heroku create your-app-name
   ```

4. **Cấu hình environment variables**:
   ```bash
   heroku config:set GROQ_API_KEY=your_key
   heroku config:set GROQ_MODEL=llama-3.1-8b-instant
   ```

5. **Tạo Procfile** (nếu chưa có) trong root folder:
   ```
   web: cd "024 - Website Header with Forms copy/Final" && python server.py
   ```

6. **Push lên Heroku**:
   ```bash
   git push heroku main
   ```

**Truy cập**: `https://your-app-name.herokuapp.com`

### C. Railway (Đơn giản hơn Heroku)

1. **Đăng ký** tại [railway.app](https://railway.app)

2. **Login và tạo project mới**

3. **Connect GitHub repository** `DIOquang/khdl`

4. **Cấu hình**:
   - Root directory: `024 - Website Header with Forms copy/Final` (nếu deploy Flask)
   - Start command: `python server.py`
   - Environment variables:
     ```
     GROQ_API_KEY=your_key
     GROQ_MODEL=llama-3.1-8b-instant
     ```

5. **Deploy** - Railway tự động deploy khi push lên main

### D. PythonAnywhere (Hosting Python đơn giản)

1. **Upload code**:
   - Đăng nhập vào [pythonanywhere.com](https://www.pythonanywhere.com)
   - Upload script hoặc clone từ GitHub

2. **Tạo virtual environment**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 khdl
   pip install -r requirements.txt
   ```

3. **Cấu hình Flask App**:
   - Tạo WSGI file
   - Set environment variables trong dashboard
   - Add domain

### E. Google Cloud Run (Serverless)

1. **Có Dockerfile** (tạo từ `Dockerfile` nếu cần):
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8502
   CMD ["python", "024 - Website Header with Forms copy/Final/server.py"]
   ```

2. **Deploy**:
   ```bash
   gcloud run deploy khdl \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GROQ_API_KEY=your_key,GROQ_MODEL=llama-3.1-8b-instant
   ```

---

## 🔧 Cấu hình Production

### CORS / Security Headers (Flask)

Trong `server.py`, thêm:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS cho all origins
```

### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@limiter.limit("10 per minute")
@app.route('/api/summarize', methods=['POST'])
def summarize():
    # ...
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

---

## 🔐 Best Practices

### 1. Environment Variables
- **Không bao giờ commit** `.env` file
- Luôn dùng `.env.example` để document biến cần thiết
- Sử dụng Secret Management của cloud provider

### 2. API Keys
- Rotate keys định kỳ
- Dùng keys riêng cho dev, staging, production
- Monitor usage trên Groq Console

### 3. File Uploads
- Validate file size (max 50MB)
- Kiểm tra file type (chỉ .xlsx)
- Lưu upload vào temp folder, xóa sau khi xử lý

### 4. Error Handling
- Log errors chi tiết cho debugging
- Return user-friendly messages
- Không expose internal paths/secrets

---

## 📊 Monitoring

### Streamlit Cloud
- Dashboard có sẵn analytics
- View logs từ "Manage app" menu

### Flask + Heroku/Railway
- Sử dụng `heroku logs --tail`
- Integrate với Sentry cho error tracking
- Use DataDog/New Relic cho performance monitoring

---

## 🐛 Troubleshooting

### Port đã bị sử dụng

```bash
# Tìm process đang dùng port
lsof -i :8501  # hoặc :8502

# Kill process
kill -9 <PID>

# macOS
lsof -ti:8501 | xargs kill -9
```

### API Rate Limit / Quota

- Nếu gặp lỗi `429 RESOURCE_EXHAUSTED`
- Kiểm tra API usage trong Groq Console
- Chờ rate limit reset hoặc upgrade plan

### Module không tìm thấy

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Excel file không được detect

- Kiểm tra tên cột: phải có "Cluster" (tên chính xác)
- File phải là `.xlsx` (không `.xls`)
- Kiểm tra encoding: UTF-8

---

## 📞 Support

- **Groq API Issues**: [docs.groq.com](https://docs.groq.com)
- **Streamlit Help**: [docs.streamlit.io](https://docs.streamlit.io)
- **Flask Deployment**: [flask.palletsprojects.com](https://flask.palletsprojects.com)

---

**Last Updated**: March 18, 2026
