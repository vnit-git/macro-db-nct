# Vietnam Macro & Equity Terminal (v2.0)

> **Hệ Thống Terminal Phân Tích Vĩ Mô & Định Giá Cổ Phiếu Tự Động Hóa**
> Kiến trúc Master Prompt 2.0 với Unified UI 4.0 & Event Selection Reactive Layout.

---

## 🌟 Tổng Quan Kiến Trúc

Hệ thống được thiết kế dựa trên các nguyên tắc công nghệ tài chính hiện đại nhằm giải quyết bài toán phân tích liên thị trường và lượng hóa tác động chính sách lên nhóm cổ phiếu:

1. **Bộ Chỉ Báo Vĩ Mô (FRED API)**:
   - Tích hợp 3 chuỗi dữ liệu kinh tế lượng: Lãi suất Fed (`FEDFUNDS`), Lạm phát CPI Việt Nam (`FPCPITOTLZGVNM`), Quy mô GDP (`MKTGDPVNA646NWDB`).
   - Bộ nhớ đệm cấp 1: `@st.cache_data(ttl=86400)` (24 giờ).

2. **Động Cơ Phân Tích Chính Sách Bằng AI (Feedparser + OpenAI JSON Mode)**:
   - Thu thập luồng RSS công báo chính phủ và tin tức vĩ mô.
   - LLM hoạt động với vai trò Giám Đốc Đầu Tư (CIO) qua `response_format={"type": "json_object"}` để sinh kết quả tất định.
   - Trích xuất: Tóm tắt chính sách, Đánh giá tác động chuỗi giá trị, Nhóm mã cổ phiếu hưởng lợi (`benefited_tickers`).
   - Bộ nhớ đệm cấp 2: `@st.cache_data(ttl=3600)` (1 giờ).

3. **Bộ Lọc Định Giá & Phản Ứng Sự Kiện (vnstock Unified UI 4.0 + Streamlit Event Selection)**:
   - Bố cục **Master - Detail (60% / 40%)**: Bảng Master bên trái bắt sự kiện `on_select="rerun"`, điều khiển bảng Detail bên phải hiển thị P/E, ROE, Vốn hóa, Biến động giá trực tiếp.
   - Tương tác 3 lớp vnstock 4.0: `Reference`, `Market`, `Fundamental`.
   - Bộ nhớ đệm cấp 3: `@st.cache_data(ttl=300)` (5 phút).

4. **Khả Năng Chống Sụp Đổ Tuyệt Đối (Zero-Crash Tolerance)**:
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
OPENAI_API_KEY = "your_openai_api_key_here"
OPENAI_MODEL = "gpt-4o-mini"
RSS_FEED_URL = "http://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss"
```
*(Bạn cũng có thể nhập trực tiếp API Key trên Sidebar của giao diện Terminal)*.

### 3. Chạy ứng dụng Streamlit:
```bash
py -m streamlit run app.py
```

### 4. Chạy kiểm thử tự động (Unit Tests):
```bash
py -c "import tests.test_services as t; t.test_clean_html(); t.test_is_valid_ticker(); t.test_format_helpers(); t.test_macro_service_fallback(); t.test_nlp_service_fallback(); t.test_stock_service(); t.test_stock_service_invalid_ticker_handling(); print('ALL 7 TESTS PASSED!')"
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
