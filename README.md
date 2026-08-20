# Vietnam Macro & Equity Terminal Pro (v1.2)

> **Hệ Thống Terminal Phân Tích Vĩ Mô & Định Giá Cổ Phiếu Tự Động Hóa**
> Kiến trúc Master Prompt 2.0 tích hợp Quantitative Valuation Engine & 5-Pillar Financial Audit Framework.

---

## 🌟 Tổng Quan Kiến Trúc

Hệ thống được thiết kế dựa trên các nguyên tắc công nghệ tài chính hiện đại nhằm giải quyết bài toán phân tích liên thị trường và lượng hóa tác động chính sách lên nhóm cổ phiếu:

1. **Bộ Chỉ Báo Vĩ Mô (FRED API + Continuous Macro Health Score)**:
   - Tích hợp 12 chỉ báo kinh tế lượng: M2, Lãi suất 6M/12M, Lãi vay, PMI, USD/VND, DXY, TPCP 10Y, Lãi suất Fed (`FEDFUNDS`), Lạm phát CPI Việt Nam (`FPCPITOTLZGVNM`), Quy mô GDP (`MKTGDPVNA646NWDB`).
   - Hệ thống chấm điểm nhiệt kế vĩ mô liên tục (Linear Interpolation) 0-100 điểm.

2. **Động Cơ Định Giá Định Lượng (Quantitative Valuation Engine)**:
   - Tích hợp 3 mô hình định giá chuẩn CFA: **Forward P/E**, **Justified P/B (Gordon Growth Model)**, và **Blended Valuation** với Biên an toàn (Margin of Safety 15%).
   - Tự động hóa tính Vốn hóa thị trường realtime theo giá khớp lệnh sàn giao dịch (SSI iBoard).

3. **Động Cơ Phân Tích Chính Sách Bằng AI (Feedparser + Gemini 3.7 / OpenAI)**:
   - Thu thập luồng RSS công báo chính phủ và tin tức vĩ mô.
   - LLM hoạt động với vai trò Giám Đốc Đầu Tư (CIO) qua Structured JSON output.
   - Trích xuất: Tóm tắt chính sách, Đánh giá tác động chuỗi giá trị, Nhóm mã cổ phiếu hưởng lợi (`benefited_tickers`).

4. **Động Cơ Dòng Tiền Ngành & RRG (Relative Rotation Graph)**:
   - Tính toán RS-Ratio và RS-Momentum chuẩn JdK Research phân loại 4 góc phần tư: Leading, Improving, Weakening, Lagging.

5. **Khả Năng Chống Sụp Đổ Tuyệt Đối (Zero-Crash Tolerance)**:
   - Tất cả các luồng dữ liệu đều được bảo vệ bởi cơ chế Fallback an toàn. Ứng dụng luôn hiển thị mượt mà ngay cả khi mất mạng hoặc chưa cấu hình API Key.

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy Local

### 1. Cài đặt thư viện phụ thuộc:
```bash
py -m pip install -r requirements.txt
```

### 2. Cấu hình API Keys (Tùy chọn):
Chỉnh sửa file `.streamlit/secrets.toml`:
```toml
FRED_API_KEY = "your_fred_api_key_here"
GEMINI_API_KEY = "your_gemini_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
RSS_FEED_URL = "http://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss"
```
*(Bạn cũng có thể nhập trực tiếp API Key trên Sidebar của giao diện Terminal)*.

### 3. Chạy ứng dụng Streamlit:
```bash
py -m streamlit run app.py
```

### 4. Chạy kiểm thử tự động (Pytest Suite - 22/22 Tests):
```bash
py -m pytest tests/test_services.py -v
```

---

## 🌐 Hướng Dẫn Triển Khai Lên Firebase (Không Ảnh Hưởng Đến Link Đang Chạy)

Vì Streamlit là một ứng dụng Python chạy ngầm có kết nối WebSocket thời gian thực (Stateful WebSocket Server), cách triển khai chuẩn mực trên hệ sinh thái Google / Firebase mà **không làm gián đoạn hay ghi đè link web hiện tại** gồm các bước sau:

### Phương Án: Cloud Run + Firebase Multi-Site Hosting (Khuyên Dùng)

#### Bước 1: Deploy backend Streamlit lên Google Cloud Run (Container)
```bash
# Đăng nhập gcloud
gcloud auth login

# Build và Deploy container tự động lên Cloud Run
gcloud run deploy vietnam-macro-terminal \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated
```

#### Bước 2: Tạo Site Hosting mới trên Firebase (Multi-Site)
Tạo thêm 1 site hosting độc lập trong cùng Firebase Project (Ví dụ tên site: `macro-terminal`):
```bash
firebase hosting:sites:create macro-terminal
```

#### Bước 3: Áp target trong `.firebaserc` và Deploy
Liên kết target cho site mới:
```bash
firebase target:apply hosting macro-terminal macro-terminal
```
Sau đó cấu hình trong `firebase.json` (đã tạo sẵn trong dự án) và deploy chỉ riêng site mới:
```bash
firebase deploy --only hosting:macro-terminal
```
> Kết quả: Bạn sẽ có 1 đường link riêng biệt `https://macro-terminal.web.app` hoặc `https://macro-terminal.firebaseapp.com` mà website hiện tại của bạn vẫn hoạt động bình thường 100%!

---

## 📂 Cấu Trúc Dự Án

```
├── .streamlit/
│   ├── config.toml           # Theme Terminal Dark Mode & Server settings
│   ├── secrets.toml          # File cấu hình API Keys
│   └── secrets.toml.example  # Mẫu cấu hình API Keys
├── services/
│   ├── macro_service.py      # Dịch vụ vĩ mô FRED (TTL=86400s)
│   ├── nlp_service.py        # Dịch vụ phân tích RSS + OpenAI (TTL=3600s)
│   └── stock_service.py      # Dịch vụ định giá vnstock 4.0 (TTL=300s)
├── utils/
│   └── helpers.py            # Hàm xử lý HTML, định dạng số, validate ticker, get_safe_secret
├── tests/
│   └── test_services.py      # Bộ kiểm thử tự động
├── Dockerfile                # Docker container cho Cloud Run & Firebase
├── firebase.json             # Cấu hình Firebase Hosting Multi-site
├── app.py                    # Giao diện chính Streamlit Terminal
├── requirements.txt          # Danh sách thư viện
└── README.md                 # Tài liệu dự án
```
