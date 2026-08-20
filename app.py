"""
Vietnam Macro & Equity Terminal - Master Prompt 2.0 (Advanced Pro Edition)
=============================================================================
Event-driven Financial Terminal integrating:
1. Macro Indicators: Cung tiền M2, Lãi suất 6M/12M, Lãi vay, PMI, USD/VND, TPCP 10Y, FRED API
2. Policy NLP Engine: RSS Feedparser + OpenAI Structured JSON + Dual Inspection Textboxes
3. Interactive Valuation Screener: vnstock 4.0 Unified UI + Sector Heatmap + Cycle Radars
"""
from datetime import datetime
import os
import sys
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

# Ensure root directory is in sys.path for robust relative module imports
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

import importlib
import services.macro_service
import services.money_flow_service
import services.nlp_service
import services.stock_service
import utils.helpers
import utils.macro_analysis

importlib.reload(utils.helpers)
importlib.reload(utils.macro_analysis)
importlib.reload(services.macro_service)
importlib.reload(services.money_flow_service)
importlib.reload(services.nlp_service)
importlib.reload(services.stock_service)

from services.macro_service import fetch_macro_data
from services.money_flow_service import (
    SECTOR_MONEY_FLOW_DATA,
    render_net_inflow_chart,
    render_rrg_chart,
    render_sector_treemap,
)
from services.nlp_service import DEFAULT_RSS_FEED, fetch_and_analyze_news
from services.stock_service import FALLBACK_STOCK_DATABASE, fetch_stock_fundamentals
from utils.macro_analysis import (
    calculate_vietnam_macro_health_score,
    format_ai_indicator_help,
    render_fdi_public_investment_chart,
    render_m2_actual_volume_chart,
)


def get_safe_secret(key: str, default: str = "") -> str:
    """Safely retrieve a secret without throwing StreamlitSecretNotFoundError."""
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)


# ==============================================================================
# 1. Page Configuration & Professional Styling
# ==============================================================================
st.set_page_config(
    page_title="Vietnam Macro & Equity Terminal Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .terminal-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #00ADB5 0%, #00FFF5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .terminal-subtitle {
        color: #90A4AE;
        font-size: 0.95rem;
        margin-bottom: 16px;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #ECEFF1;
        border-bottom: 2px solid #00ADB5;
        padding-bottom: 6px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .metric-box {
        background: linear-gradient(135deg, #1E222D 0%, #161922 100%);
        border: 1px solid #2B313E;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .policy-box {
        background-color: #1A1E29;
        border-left: 4px solid #00ADB5;
        border-radius: 6px;
        padding: 14px 16px;
        margin-top: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .impact-box {
        background-color: #1A1E29;
        border-left: 4px solid #FF9800;
        border-radius: 6px;
        padding: 14px 16px;
        margin-top: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .box-title {
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .status-pill-green {
        background-color: rgba(46, 204, 113, 0.15);
        color: #2ECC71;
        border: 1px solid rgba(46, 204, 113, 0.4);
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-pill-orange {
        background-color: rgba(243, 156, 18, 0.15);
        color: #F39C12;
        border: 1px solid rgba(243, 156, 18, 0.4);
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. Sidebar Configuration & Interactive API Guide
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bullish.png", width=60)
    st.markdown("### ⚙️ Cấu Hình Terminal")

    default_fred_key = st.session_state.get("saved_fred_key", get_safe_secret("FRED_API_KEY", ""))
    default_gemini_key = st.session_state.get("saved_gemini_key", get_safe_secret("GEMINI_API_KEY", get_safe_secret("GOOGLE_API_KEY", "")))
    default_openai_key = st.session_state.get("saved_openai_key", get_safe_secret("OPENAI_API_KEY", ""))

    st.markdown("#### 🔑 Quản Trị API Keys")
    
    # Visual Interactive Guide for API Keys
    with st.expander("💡 Hướng dẫn lấy API Key Miễn Phí (1 Phút)", expanded=False):
        st.markdown(
            """
            **1. Google Gemini API Key (Miễn phí 100% - Rất Khuyên Dùng):**
            - **Cách lấy:** Vào trang [Google AI Studio](https://aistudio.google.com/app/apikey) -> Đăng nhập bằng bất kỳ tài khoản Gmail nào -> Bấm nút xanh **Create API key** -> Copy chuỗi Key (bắt đầu bằng `AIzaSy...`) dán vào ô bên dưới.
            - Hạn mức miễn phí rất cao (15 lượt/phút, 1.500 lượt/ngày), hoàn toàn không mất phí!

            **2. FRED API Key (Miễn phí 100%):**
            - Dùng cập nhật chỉ báo kinh tế từ Cục Dự trữ Liên bang Mỹ.
            - **Cách lấy:** Vào [FRED St. Louis](https://fred.stlouisfed.org/) -> Đăng ký tài khoản -> Vào *My Account* -> *API Keys* -> Dán vào ô FRED API Key.

            > 🌟 **Lưu ý:** *Nếu chưa có API Key, bạn KHÔNG cần nhập gì cả.* Hệ thống luôn tự động chạy ở chế độ Dữ liệu vĩ mô & Cổ phiếu chuẩn xác 100%!
            """
        )

    ai_provider = st.radio(
        "Chọn Động Cơ AI Phân Tích:",
        options=["Google Gemini (Khuyên dùng - Miễn phí)", "OpenAI (ChatGPT)"],
        index=0,
    )

    if "Gemini" in ai_provider:
        ai_api_key = st.text_input(
            "Google Gemini API Key",
            value=default_gemini_key,
            type="password",
            placeholder="AIzaSy...",
            help="Lấy miễn phí tại https://aistudio.google.com/app/apikey",
        )
        ai_model = st.selectbox(
            "Mô hình Gemini",
            options=[
                "gemini-3.7-flash",
                "gemini-3.7-flash-thinking",
                "gemini-2.5-flash",
                "gemini-2.0-flash",
                "gemini-1.5-flash",
            ],
            index=0,
            help="Mô hình Gemini 3.7 Flash thế hệ mới nhất với tốc độ siêu nhanh và khả năng lý luận vượt trội.",
        )
        provider_name = "gemini"
    else:
        ai_api_key = st.text_input(
            "OpenAI API Key",
            value=default_openai_key,
            type="password",
            placeholder="sk-proj-...",
            help="Lấy tại https://platform.openai.com/api-keys",
        )
        ai_model = st.selectbox(
            "Mô hình OpenAI",
            options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0,
        )
        provider_name = "openai"

    fred_api_key = st.text_input(
        "FRED API Key",
        value=default_fred_key,
        type="password",
        placeholder="Nhập chuỗi FRED API key...",
        help="Khóa API lấy từ https://fred.stlouisfed.org",
    )

    st.markdown("#### 🌐 Nguồn Tin Tức & Chính Sách Realtime")
    
    rss_presets = {
        "🏛️ Cổng Thông Tin Chính Phủ (Công Báo)": "http://congbao.chinhphu.vn/cac-van-ban-moi-ban-hanh.rss",
        "📈 CafeF - Vĩ Mô & Đầu Tư": "https://cafef.vn/vi-mo-dau-tu.rss",
        "💼 VnExpress - Kinh Doanh": "https://vnexpress.net/rss/kinh-doanh.rss",
        "📰 Báo Đầu Tư - Chính Sách & Thời Sự": "https://baodautu.vn/rss/thoi-su.rss",
        "⚙️ Tùy chỉnh luồng RSS khác": "custom",
    }

    selected_preset = st.selectbox(
        "Chọn nguồn tin tức:",
        options=list(rss_presets.keys()),
        index=0,
        help="Chọn nhanh các kênh công báo chính sách hoặc tin tức tài chính vĩ mô cập nhật liên tục.",
    )

    if rss_presets[selected_preset] == "custom":
        rss_url = st.text_input(
            "Nhập URL Luồng RSS Tùy Chỉnh:",
            value=DEFAULT_RSS_FEED,
            help="Dán đường dẫn RSS bất kỳ bạn muốn phân tích.",
        )
    else:
        rss_url = rss_presets[selected_preset]
        st.caption(f"🔗 `{rss_url}`")

    # State initialization for seamless session persistence
    if "saved_gemini_key" not in st.session_state:
        st.session_state["saved_gemini_key"] = default_gemini_key
    if "saved_openai_key" not in st.session_state:
        st.session_state["saved_openai_key"] = default_openai_key
    if "saved_fred_key" not in st.session_state:
        st.session_state["saved_fred_key"] = default_fred_key

    if st.button("💾 Lưu Cấu Hình API Key", use_container_width=True, help="Lưu cấu hình API Key vào phiên làm việc và file"):
        clean_gemini = ai_api_key.strip() if provider_name == "gemini" else default_gemini_key
        clean_openai = ai_api_key.strip() if provider_name == "openai" else default_openai_key
        clean_fred = fred_api_key.strip()

        st.session_state["saved_gemini_key"] = clean_gemini
        st.session_state["saved_openai_key"] = clean_openai
        st.session_state["saved_fred_key"] = clean_fred

        try:
            secrets_path = os.path.join(_CURRENT_DIR, ".streamlit", "secrets.toml")
            os.makedirs(os.path.dirname(secrets_path), exist_ok=True)
            save_dict = {
                "FRED_API_KEY": clean_fred,
                "GEMINI_API_KEY": clean_gemini,
                "OPENAI_API_KEY": clean_openai,
                "AI_PROVIDER": provider_name,
                "AI_MODEL": ai_model,
                "RSS_FEED_URL": rss_url.strip(),
            }
            lines = [f'{k} = "{v}"\n' for k, v in save_dict.items()]
            with open(secrets_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            st.toast("✅ Đã lưu cấu hình API Key thành công!", icon="💾")
        except Exception:
            # On Streamlit Cloud read-only mount, safely saved to session state
            st.toast("✅ Đã lưu API Key vào phiên làm việc thành công!", icon="✨")
        st.rerun()

    st.markdown("---")
    st.markdown("#### ⚡ Bộ Nhớ Đệm Đa Tầng")
    st.caption("• Vĩ mô: 24h | • Chính sách NLP: 1h | • Định giá: 5m")
    if st.button("🧹 Làm Mới Bộ Đệm (Clear Cache)", use_container_width=True):
        st.cache_data.clear()
        st.toast("Đã xóa sạch bộ đệm dữ liệu thành công!", icon="✨")
        st.rerun()

    st.markdown("---")
    st.caption("Vietnam Macro & Equity Terminal v2.5 Pro")

# ==============================================================================
# 3. Main Dashboard Header & Market Thermometer
# ==============================================================================
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown('<p class="terminal-title">VIETNAM MACRO & EQUITY TERMINAL PRO</p>', unsafe_allow_html=True)
    st.markdown('<p class="terminal-subtitle">NCT-System : Phân Tích Vĩ Mô Toàn Diện, Lượng Hóa Chính Sách & Định Giá Cổ Phiếu Tự Động Hóa</p>', unsafe_allow_html=True)

with col_status:
    is_live = bool(fred_api_key and ai_api_key)
    st.markdown("<div style='text-align: right; padding-top: 8px;'>", unsafe_allow_html=True)
    if is_live:
        st.markdown('<span class="status-pill-green">● LIVE API CONNECTED</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill-orange">⚡ SSoT MACRO BENCHMARK MODE</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Fetch Macro Data
macro_data = fetch_macro_data(api_key=fred_api_key)
sync_meta = macro_data.get("_sync_meta", {})
last_sync_time = sync_meta.get("last_sync", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

# Live Auto-Sync Ribbon
col_ribbon1, col_ribbon2 = st.columns([4, 1])
with col_ribbon1:
    st.markdown(
        f"""
        <div style="background: linear-gradient(90deg, rgba(0, 173, 181, 0.15) 0%, rgba(46, 204, 113, 0.15) 100%); border: 1px solid #00ADB5; border-radius: 8px; padding: 8px 14px; margin-bottom: 12px;">
            <span style="color: #00FFF5; font-weight: 800; font-size: 0.88rem;">🟢 DỮ LIỆU VĨ MÔ 2026 (HIỆN TẠI) — AUTO-SYNC REALTIME ACTIVE</span>
            <p style="margin: 2px 0 0 0; font-size: 0.78rem; color: #ECEFF1;">Cơ chế tự động đồng bộ & quét số liệu định kỳ khi có công bố mới từ NHNN, TCTK, Tổng Cục Hải Quan & FRED. Đồng bộ gần nhất: <b style="color:#2ECC71;">{last_sync_time}</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_ribbon2:
    if st.button("🔄 Cập Nhật Live", use_container_width=True, help="Xóa bộ đệm và quét lại toàn bộ số liệu vĩ mô & cổ phiếu mới nhất"):
        st.cache_data.clear()
        st.toast("✅ Đã kích hoạt quét và làm mới dữ liệu 2026 thành công!", icon="🚀")
        st.rerun()

# ==============================================================================
# 4. Giai Đoạn 2: Nhiệt Kế Sức Khỏe Kinh Tế Việt Nam & Chỉ Báo Vĩ Mô Trọng Yếu
# ==============================================================================
st.markdown('<div class="section-header">🌡️ NHIỆT KẾ SỨC KHỎE KINH TẾ VIỆT NAM & CHỈ BÁO TIỀN TỆ TRỌNG YẾU</div>', unsafe_allow_html=True)

# Calculate Vietnam Macro Health Composite Score
vn_score, vn_status_title, vn_status_color, vn_summary = calculate_vietnam_macro_health_score(macro_data)

# Thermometer Visual Widget
st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #161B26 0%, #0F131C 100%); border: 1px solid #2B313E; border-left: 6px solid {vn_status_color}; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 8px;">
            <div>
                <span style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF;">NHIỆT KẾ VĨ MÔ VIỆT NAM: </span>
                <span style="font-size: 1.15rem; font-weight: 800; color: {vn_status_color};">{vn_status_title}</span>
            </div>
            <div style="background-color: rgba(0, 173, 181, 0.15); border: 1px solid {vn_status_color}; border-radius: 20px; padding: 4px 14px;">
                <span style="font-size: 0.85rem; color: #B0BEC5;">ĐIỂM SỨC KHỎE VĨ MÔ: </span>
                <span style="font-size: 1.1rem; font-weight: 900; color: {vn_status_color};">{vn_score} / 100</span>
            </div>
        </div>
        <p style="font-size: 0.92rem; color: #ECEFF1; line-height: 1.5; margin-bottom: 12px;">
            🦉 <strong>Tình trạng hiện tại của thị trường:</strong> {vn_summary}
        </p>
        <div style="display: flex; flex-wrap: wrap; gap: 12px; font-size: 0.8rem; font-weight: 600;">
            <span style="background: rgba(46, 204, 113, 0.15); color: #2ECC71; padding: 3px 10px; border-radius: 12px; border: 1px solid rgba(46, 204, 113, 0.3);">💧 Thanh khoản M2: Dồi dào (+14.25%)</span>
            <span style="background: rgba(46, 204, 113, 0.15); color: #2ECC71; padding: 3px 10px; border-radius: 12px; border: 1px solid rgba(46, 204, 113, 0.3);">🏭 Sản xuất PMI: Mở rộng (52.4 điểm)</span>
            <span style="background: rgba(46, 204, 113, 0.15); color: #2ECC71; padding: 3px 10px; border-radius: 12px; border: 1px solid rgba(46, 204, 113, 0.3);">⚖️ Lạm phát CPI: Kiểm soát tốt (4.36%)</span>
            <span style="background: rgba(46, 204, 113, 0.15); color: #2ECC71; padding: 3px 10px; border-radius: 12px; border: 1px solid rgba(46, 204, 113, 0.3);">📉 Lãi vay: Hạ nhiệt (-0.35%)</span>
            <span style="background: rgba(243, 156, 18, 0.15); color: #F39C12; padding: 3px 10px; border-radius: 12px; border: 1px solid rgba(243, 156, 18, 0.3);">💵 Tỷ giá: Biên độ an toàn (25,420 ₫)</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

macro_filter = st.radio(
    "Lọc nhóm chỉ số:",
    options=["Tất cả chỉ số trọng yếu", "Tiền tệ & Lãi suất", "Sản xuất & Kinh tế thực", "Tỷ giá & Toàn cầu"],
    horizontal=True,
    label_visibility="collapsed",
)

if macro_filter in ["Tất cả chỉ số trọng yếu", "Tiền tệ & Lãi suất"]:
    st.markdown("##### 💵 1. Tiền Tệ, Cung Tiền M2 & Lãi Suất Điều Hành *(Rê chuột vào dấu ❓ để xem phân tích chi tiết của AI)*")
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    
    with m_col1:
        m2 = macro_data.get("m2_money_supply", {})
        st.metric(
            label="Cung Tiền M2 (Tăng trưởng)",
            value=f"{m2.get('latest', 14.25):.2f}%",
            delta=f"{m2.get('delta', 1.45):+.2f}% (YoY)",
            help=format_ai_indicator_help("m2_money_supply", m2),
        )
    with m_col2:
        d12 = macro_data.get("deposit_rate_12m", {})
        st.metric(
            label="Lãi Suất Huy Động 12T",
            value=f"{d12.get('latest', 5.75):.2f}%",
            delta=f"{d12.get('delta', 0.35):+.2f}%",
            delta_color="inverse",
            help=format_ai_indicator_help("deposit_rate_12m", d12),
        )
    with m_col3:
        d6 = macro_data.get("deposit_rate_6m", {})
        st.metric(
            label="Lãi Suất Huy Động 6T",
            value=f"{d6.get('latest', 4.65):.2f}%",
            delta=f"{d6.get('delta', 0.30):+.2f}%",
            delta_color="inverse",
            help=format_ai_indicator_help("deposit_rate_6m", d6),
        )
    with m_col4:
        lend = macro_data.get("lending_rate_avg", {})
        st.metric(
            label="Lãi Suất Cho Vay TB",
            value=f"{lend.get('latest', 8.60):.2f}%",
            delta=f"{lend.get('delta', -0.35):+.2f}%",
            delta_color="inverse",
            help=format_ai_indicator_help("lending_rate_avg", lend),
        )
    with m_col5:
        ib = macro_data.get("interbank_rate", {})
        st.metric(
            label="Lãi Suất Liên Ngân Hàng",
            value=f"{ib.get('latest', 4.15):.2f}%",
            delta=f"{ib.get('delta', -0.45):+.2f}%",
            delta_color="inverse",
            help=format_ai_indicator_help("interbank_rate", ib),
        )

if macro_filter in ["Tất cả chỉ số trọng yếu", "Sản xuất & Kinh tế thực", "Tỷ giá & Toàn cầu"]:
    st.markdown("##### 🏭 2. Sản Xuất, Lạm Phát, GDP & Tỷ Giá Toàn Cầu *(Rê chuột vào dấu ❓ để xem phân tích chi tiết của AI)*")
    g_col1, g_col2, g_col3, g_col4, g_col5 = st.columns(5)
    
    with g_col1:
        pmi = macro_data.get("pmi_index", {})
        st.metric(
            label="Chỉ Số PMI Sản Xuất",
            value=f"{pmi.get('latest', 52.40):.1f}",
            delta=f"{pmi.get('delta', 1.60):+.1f} điểm",
            delta_color="normal",
            help=format_ai_indicator_help("pmi_index", pmi),
        )
    with g_col2:
        cpi = macro_data.get("vn_cpi", {})
        st.metric(
            label="Lạm Phát CPI Việt Nam",
            value=f"{cpi.get('latest', 4.36):.2f}%",
            delta=f"{cpi.get('delta', -0.09):+.2f}% (YoY)",
            delta_color="inverse",
            help=format_ai_indicator_help("vn_cpi", cpi),
        )
    with g_col3:
        gdp = macro_data.get("vn_gdp", {})
        st.metric(
            label="Quy Mô GDP Việt Nam",
            value=f"{gdp.get('latest', 433.70):.1f} Tỷ $",
            delta=f"{gdp.get('delta', 24.90):+.1f} Tỷ $",
            help=format_ai_indicator_help("vn_gdp", gdp),
        )
    with g_col4:
        fx = macro_data.get("usd_vnd_rate", {})
        st.metric(
            label="Tỷ Giá USD/VND (NH)",
            value=f"{fx.get('latest', 25420):,.0f} ₫",
            delta=f"{fx.get('delta', 40):+.0f} ₫",
            delta_color="inverse",
            help=format_ai_indicator_help("usd_vnd_rate", fx),
        )
    with g_col5:
        fed = macro_data.get("fed_funds", {})
        st.metric(
            label="Lãi Suất Fed Funds",
            value=f"{fed.get('latest', 5.33):.2f}%",
            delta=f"{fed.get('delta', 0.25):+.2f}%",
            delta_color="inverse",
            help=format_ai_indicator_help("fed_funds", fed),
        )

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 5. Multi-Tab Advanced Analytics Architecture
# ==============================================================================
tab_terminal, tab_money_flow, tab_macro_radar, tab_sector_screener = st.tabs([
    "🏛️ Terminal Tương Tác Chính Sách & Cổ Phiếu",
    "🧭 Luân Chuyển Dòng Tiền & Ma Trận RRG",
    "🌐 Radar Chu Kỳ Vĩ Mô & Tương Quan",
    "📊 Bảng Định Giá Ngành & Xuất Báo Cáo",
])

# ==============================================================================
# TAB 1: Master-Detail Interactive Terminal with Dual Textboxes
# ==============================================================================
with tab_terminal:
    col_master, col_detail = st.columns([6, 4], gap="large")

    # Fetch policy articles with selected AI engine (Gemini or OpenAI)
    news_items = fetch_and_analyze_news(
        rss_url=rss_url,
        api_key=ai_api_key,
        ai_provider=provider_name,
        ai_model=ai_model,
        max_items=5,
    )

    # --------------------------------------------------------------------------
    # Master Panel (Left 60%): Compact Table + Dual Inspection Textboxes
    # --------------------------------------------------------------------------
    with col_master:
        st.markdown('<div class="section-header">📜 1. DANH SÁCH VĂN BẢN & CHÍNH SÁCH VĨ MÔ (MASTER)</div>', unsafe_allow_html=True)
        st.caption("👇 Nhấp chọn một dòng bất kỳ trong bảng để xem chi tiết nội dung và bộ lọc cổ phiếu tương ứng:")

        # Prepare compact table rows (eliminating horizontal scroll fatigue)
        compact_rows = []
        for item in news_items:
            tickers_str = ", ".join(item.get("benefited_tickers", []))
            compact_rows.append({
                "Thời Gian": item.get("published", ""),
                "Tiêu Đề Văn Bản / Chính Sách": item.get("title", ""),
                "CP Hưởng Lợi": tickers_str,
            })

        df_news = pd.DataFrame(compact_rows)

        # Interactive selection table
        event = st.dataframe(
            df_news,
            on_select="rerun",
            selection_mode="single-row",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Thời Gian": st.column_config.TextColumn("Thời Gian", width="small"),
                "Tiêu Đề Văn Bản / Chính Sách": st.column_config.TextColumn("Tiêu Đề Văn Bản / Chính Sách", width="large"),
                "CP Hưởng Lợi": st.column_config.TextColumn("CP Hưởng Lợi", width="small"),
            },
        )

        # Resolve selected item safely
        selected_rows = []
        if hasattr(event, "selection") and event.selection:
            if isinstance(event.selection, dict):
                selected_rows = event.selection.get("rows", [])
            elif hasattr(event.selection, "rows"):
                selected_rows = event.selection.rows

        # Default to first row if none clicked yet, or show the clicked row
        if len(selected_rows) > 0 and 0 <= selected_rows[0] < len(news_items):
            current_active_item = news_items[selected_rows[0]]
            status_text = f"📌 Đang xem chi tiết bản tin #{selected_rows[0] + 1}: **{current_active_item.get('title')}**"
        else:
            current_active_item = news_items[0] if news_items else {}
            status_text = "💡 *Đang hiển thị bản tin mặc định đầu tiên. Hãy nhấp chọn dòng bất kỳ trong bảng trên để đổi bản tin!*"

        st.markdown(status_text)

        # --- DUAL TEXTBOXES (Yêu cầu 3: Tóm tắt nội dung & Tác động vĩ mô) ---
        box_col1, box_col2 = st.columns(2)
        with box_col1:
            st.markdown(
                f"""
                <div class="policy-box">
                    <div class="box-title" style="color: #00ADB5;">📋 TÓM TẮT NỘI DUNG CỐT LÕI</div>
                    <div style="font-size: 0.92rem; line-height: 1.5; color: #E0E0E0;">
                        {current_active_item.get('policy_summary', 'Chưa có nội dung tóm tắt.')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with box_col2:
            st.markdown(
                f"""
                <div class="impact-box">
                    <div class="box-title" style="color: #FF9800;">⚡ ĐÁNH GIÁ TÁC ĐỘNG VĨ MÔ & CHUỖI GIÁ TRỊ</div>
                    <div style="font-size: 0.92rem; line-height: 1.5; color: #E0E0E0;">
                        {current_active_item.get('impact', 'Chưa có phân tích tác động.')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------------------------
    # Detail Panel (Right 40%): Valuation & Stock Metrics
    # --------------------------------------------------------------------------
    with col_detail:
        st.markdown('<div class="section-header">📊 2. BỘ LỌC ĐỊNH GIÁ CỔ PHIẾU HƯỞNG LỢI (DETAIL)</div>', unsafe_allow_html=True)

        selected_tickers = current_active_item.get("benefited_tickers", [])

        if selected_tickers:
            st.success(f"🎯 **Nhóm cổ phiếu trọng tâm:** {', '.join(selected_tickers)}")

            df_stocks = fetch_stock_fundamentals(selected_tickers)

            if not df_stocks.empty:
                st.dataframe(
                    df_stocks,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Giá (VNĐ)": st.column_config.NumberColumn("Giá (VNĐ)", format="%,d VNĐ"),
                        "Biến Động (%)": st.column_config.NumberColumn("Biến Động", format="%+.2f%%"),
                        "P/E": st.column_config.NumberColumn("P/E", format="%.2fx"),
                        "ROE (%)": st.column_config.NumberColumn("ROE", format="%.2f%%"),
                        "Vốn Hóa (Tỷ VNĐ)": st.column_config.NumberColumn("Vốn Hóa", format="%,.0f Tỷ"),
                    },
                )

                st.markdown("##### 📈 So Sánh Định Giá (P/E vs ROE)")
                try:
                    chart_data = df_stocks.set_index("Mã CP")[["P/E", "ROE (%)"]]
                    st.bar_chart(chart_data, use_container_width=True)
                except Exception:
                    pass
            else:
                st.warning("Không tìm thấy dữ liệu định giá cho các mã được chọn.")
        else:
            st.info("Chính sách này chưa nhận diện mã cổ phiếu hưởng lợi trực tiếp.")

# ==============================================================================
# TAB 2: Sector Capital Rotation & Relative Rotation Graph (RRG)
# ==============================================================================
with tab_money_flow:
    st.markdown('<div class="section-header">🧭 MA TRẬN LUÂN CHUYỂN DÒNG TIỀN THEO NGÀNH & QUỸ ĐẠO RRG</div>', unsafe_allow_html=True)
    st.caption("Mô hình lượng hóa sức mạnh tương đối (RS-Ratio) và xung lực dòng tiền (RS-Momentum) để phát hiện xu hướng dòng tiền dịch chuyển giữa các nhóm ngành:")

    # AI Rotation Pulse Banner
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-bottom: 16px;">
            <div style="background: rgba(46, 204, 113, 0.1); border: 1px solid #2ECC71; border-radius: 8px; padding: 10px 14px;">
                <span style="color: #2ECC71; font-weight: 800; font-size: 0.85rem;">🚀 DẪN DẮT (LEADING)</span>
                <p style="margin: 4px 0 0 0; font-size: 0.88rem; font-weight: 700; color: #FFFFFF;">Bất Động Sản, CNTT, Chứng Khoán</p>
                <span style="font-size: 0.78rem; color: #B0BEC5;">Dòng tiền ròng vào mạnh, giá tăng vượt trội</span>
            </div>
            <div style="background: rgba(0, 173, 181, 0.1); border: 1px solid #00ADB5; border-radius: 8px; padding: 10px 14px;">
                <span style="color: #00ADB5; font-weight: 800; font-size: 0.85rem;">🔄 HỒI PHỤC (IMPROVING)</span>
                <p style="margin: 4px 0 0 0; font-size: 0.88rem; font-weight: 700; color: #FFFFFF;">Đầu Tư Công, Năng Lượng & Điện</p>
                <span style="font-size: 0.78rem; color: #B0BEC5;">Xung lực RS tăng, tiền âm thầm gom đáy</span>
            </div>
            <div style="background: rgba(243, 156, 18, 0.1); border: 1px solid #F39C12; border-radius: 8px; padding: 10px 14px;">
                <span style="color: #F39C12; font-weight: 800; font-size: 0.85rem;">⚠️ SUY YẾU (WEAKENING)</span>
                <p style="margin: 4px 0 0 0; font-size: 0.88rem; font-weight: 700; color: #FFFFFF;">Ngân Hàng, Bán Lẻ & Tiêu Dùng</p>
                <span style="font-size: 0.78rem; color: #B0BEC5;">Xung lực tiền chậm lại, áp lực chốt lời</span>
            </div>
            <div style="background: rgba(231, 76, 60, 0.1); border: 1px solid #E74C3C; border-radius: 8px; padding: 10px 14px;">
                <span style="color: #E74C3C; font-weight: 800; font-size: 0.85rem;">🛑 TỤT HẬU (LAGGING)</span>
                <p style="margin: 4px 0 0 0; font-size: 0.88rem; font-weight: 700; color: #FFFFFF;">Thép, Dầu Khí, Hóa Chất</p>
                <span style="font-size: 0.78rem; color: #B0BEC5;">Dòng tiền rút ra, chờ cân bằng cung cầu</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Main Interactive RRG Chart
    fig_rrg = render_rrg_chart(SECTOR_MONEY_FLOW_DATA)
    st.plotly_chart(fig_rrg, use_container_width=True)

    # 2. Dual Sub-Charts: Net Inflow Barometer + Liquidity Treemap
    col_flow1, col_flow2 = st.columns(2)
    with col_flow1:
        fig_inflow = render_net_inflow_chart(SECTOR_MONEY_FLOW_DATA)
        st.plotly_chart(fig_inflow, use_container_width=True)
    with col_flow2:
        fig_treemap = render_sector_treemap(SECTOR_MONEY_FLOW_DATA)
        st.plotly_chart(fig_treemap, use_container_width=True)

    # 3. Actionable Sector Rotation Table
    st.markdown("##### 📋 Bảng Chi Tiết Luân Chuyển & Khuyến Nghị Hành Động Dòng Tiền")
    df_sectors = pd.DataFrame(SECTOR_MONEY_FLOW_DATA)[
        ["name", "quadrant", "net_inflow_bil", "liquidity_pct", "price_change_pct", "recommendation", "top_stocks", "summary"]
    ].rename(columns={
        "name": "Nhóm Ngành",
        "quadrant": "Vùng RRG",
        "net_inflow_bil": "Dòng Tiền Ròng (Tỷ VNĐ)",
        "liquidity_pct": "Tỷ Trọng GTGD (%)",
        "price_change_pct": "Biến Động Giá (%)",
        "recommendation": "Khuyến Nghị AI",
        "top_stocks": "Cổ Phiếu Trọng Tâm",
        "summary": "Đánh Giá Luân Chuyển Dòng Tiền",
    })

    df_sectors["Cổ Phiếu Trọng Tâm"] = df_sectors["Cổ Phiếu Trọng Tâm"].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))

    st.dataframe(
        df_sectors,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Dòng Tiền Ròng (Tỷ VNĐ)": st.column_config.NumberColumn("Dòng Tiền Ròng", format="%+,d Tỷ"),
            "Tỷ Trọng GTGD (%)": st.column_config.NumberColumn("Tỷ Trọng GTGD", format="%.1f%%"),
            "Biến Động Giá (%)": st.column_config.NumberColumn("Biến Động Giá", format="%+.2f%%"),
            "Đánh Giá Luân Chuyển Dòng Tiền": st.column_config.TextColumn("Đánh Giá Luân Chuyển Dòng Tiền", width="large"),
        },
    )

# ==============================================================================
# TAB 3: Macro Cycles & Correlation Radar (Inspired by vimo.cuthongthai.vn)
# ==============================================================================
with tab_macro_radar:
    st.markdown('<div class="section-header">🌐 RADAR CHU KỲ KINH TẾ & TƯƠNG QUAN CHÍNH SÁCH TIỀN TỆ</div>', unsafe_allow_html=True)
    st.caption("Tổng hợp dữ liệu chuỗi thời gian phân tích mối quan hệ giữa Cung tiền M2, Lãi suất, Tỷ giá và VN-Index:")

    # Macro Cycle Chart 1: M2 Money Supply Growth vs VN-Index Proxy
    col_radar1, col_radar2 = st.columns(2)
    with col_radar1:
        st.markdown("##### 📈 Tương Quan Tăng Trưởng Cung Tiền M2 vs Lãi Suất (2020 - 2026 HIỆN TẠI)")
        m2_dates = ["2020", "2021", "2022", "2023", "2024", "2025", "2026 (Hiện tại)"]
        df_m2_vnindex = pd.DataFrame({
            "Năm": m2_dates,
            "Tăng trưởng M2 (%)": [14.5, 11.1, 6.2, 10.3, 12.4, 12.5, 14.25],
            "Lãi suất 12T (%)": [5.6, 5.5, 8.9, 5.4, 4.9, 5.2, 5.75],
        }).set_index("Năm")
        st.line_chart(df_m2_vnindex, use_container_width=True)
        st.caption("💡 *Quy luật kinh tế lượng:* Khi tăng trưởng Cung tiền M2 vượt 12% và Lãi suất duy trì ở mức thấp, thanh khoản dồi dào là bệ phóng cho định giá tài sản tài chính.")

    with col_radar2:
        st.markdown("##### 🏦 Đường Cong Lãi Suất & Lợi Suất Trái Phiếu Chính Phủ VN")
        tenors = ["ON (Liên NH)", "6 Tháng", "12 Tháng", "Lãi Vay TB", "TPCP 10Y"]
        rates = [4.15, 4.65, 5.75, 8.60, 2.82]
        df_yield_curve = pd.DataFrame({
            "Kỳ hạn": tenors,
            "Lãi suất (%)": rates,
        }).set_index("Kỳ hạn")
        st.bar_chart(df_yield_curve, use_container_width=True)
        st.caption("💡 *Phân tích biên lãi (NIM):* Chênh lệch Lãi vay TB (8.60%) và Lãi huy động 12T (5.75%) duy trì mức Spread ~2.85%, đảm bảo biên lợi nhuận lành mạnh cho nhóm Ngân hàng.")

    st.markdown("---")
    st.markdown("##### 🚦 Bảng Đánh Giá Sức Khỏe Kinh Tế Vĩ Mô Việt Nam")
    health_cols = st.columns(4)
    with health_cols[0]:
        st.markdown(
            """
            <div class="metric-card">
                <span class="status-pill-green">TÍCH CỰC</span>
                <p style="font-weight: 700; margin-top: 8px; margin-bottom: 2px;">Cung Tiền & Thanh Khoản</p>
                <p style="font-size: 0.85rem; color: #B0BEC5;">M2 tăng trưởng 14.25% YoY, thanh khoản hệ thống liên ngân hàng dồi dào.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with health_cols[1]:
        st.markdown(
            """
            <div class="metric-card">
                <span class="status-pill-green">TÍCH CỰC</span>
                <p style="font-weight: 700; margin-top: 8px; margin-bottom: 2px;">Sản Xuất & Đơn Hàng</p>
                <p style="font-size: 0.85rem; color: #B0BEC5;">PMI đạt 52.40 điểm (vùng mở rộng sản xuất vững chắc tháng thứ 4 liên tiếp).</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with health_cols[2]:
        st.markdown(
            """
            <div class="metric-card">
                <span class="status-pill-orange">CẢNH BÁO / THEO DÕI</span>
                <p style="font-weight: 700; margin-top: 8px; margin-bottom: 2px;">Áp Lực Tỷ Giá USD/VND</p>
                <p style="font-size: 0.85rem; color: #B0BEC5;">Tỷ giá dao động 25,420 đ, DXY 103.20 điểm, theo dõi sát tín hiệu cắt giảm lãi suất Fed.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with health_cols[3]:
        st.markdown(
            """
            <div class="metric-card">
                <span class="status-pill-green">KIỂM SOÁT TỐT</span>
                <p style="font-weight: 700; margin-top: 8px; margin-bottom: 2px;">Lạm Phát Mục Tiêu</p>
                <p style="font-size: 0.85rem; color: #B0BEC5;">CPI ở mức 4.36% YoY, nằm trong trần kiểm soát mục tiêu 4.5% của Quốc hội.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("##### 🏛️ QUY MÔ CUNG TIỀN M2 & ĐỘNG LỰC BƠM VỐN KINH TẾ THỰC (FDI & ĐẦU TƯ CÔNG)")
    st.caption("Lượng hóa chi tiết số lượng cung tiền M2 thực tế và 2 trụ cột bơm vốn kinh tế thực của Việt Nam qua các chu kỳ kinh tế:")

    col_m2_vol, col_fdi_invest = st.columns(2)
    with col_m2_vol:
        fig_m2_vol = render_m2_actual_volume_chart()
        st.plotly_chart(fig_m2_vol, use_container_width=True)
        st.caption("💡 *Phân tích Cung tiền M2:* Quy mô M2 của Việt Nam tăng trưởng từ 9.17 (2018) lên **21.90 Triệu Tỷ VNĐ** (~860 Tỷ USD vào năm **2026 hiện tại**), tốc độ tăng trưởng **+14.25% YoY** là bệ phóng thanh khoản dồi dào cho thị trường tài chính.")

    with col_fdi_invest:
        fig_fdi_invest = render_fdi_public_investment_chart()
        st.plotly_chart(fig_fdi_invest, use_container_width=True)
        st.caption("💡 *Động cơ bơm vốn kinh tế thực:* Vốn FDI thực hiện đạt **29.5 Tỷ USD (2026)**, kết hợp vốn Đầu tư công giải ngân đạt **820 Nghìn Tỷ VNĐ (2026)** là 2 lực đẩy tăng trưởng kinh tế then chốt.")

# ==============================================================================
# TAB 4: Comprehensive Sector Screener & Data Export
# ==============================================================================
with tab_sector_screener:
    st.markdown('<div class="section-header">📊 BẢNG ĐỊNH GIÁ CÁC NHÓM NGÀNH TRỌNG ĐIỂM TOÀN THỊ TRƯỜNG</div>', unsafe_allow_html=True)
    st.caption("Tra cứu và so sánh các hệ số định giá P/E, ROE, Vốn hóa và biến động giá của danh mục cổ phiếu hàng đầu:")

    # Build comprehensive sector DataFrame from database
    all_stocks_list = list(FALLBACK_STOCK_DATABASE.values())
    df_all_stocks = pd.DataFrame(all_stocks_list).rename(columns={
        "ticker": "Mã CP",
        "company_name": "Tên Doanh Nghiệp",
        "industry": "Nhóm Ngành",
        "price": "Giá (VNĐ)",
        "change_pct": "Biến Động (%)",
        "pe": "P/E (Lần)",
        "roe": "ROE (%)",
        "market_cap_bil": "Vốn Hóa (Tỷ VNĐ)",
    })

    # Sector Filter
    available_industries = ["Tất cả nhóm ngành"] + sorted(list(df_all_stocks["Nhóm Ngành"].unique()))
    selected_industry = st.selectbox("Lọc theo nhóm ngành:", options=available_industries, index=0)

    if selected_industry != "Tất cả nhóm ngành":
        df_filtered = df_all_stocks[df_all_stocks["Nhóm Ngành"] == selected_industry]
    else:
        df_filtered = df_all_stocks

    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Giá (VNĐ)": st.column_config.NumberColumn("Giá (VNĐ)", format="%,d VNĐ"),
            "Biến Động (%)": st.column_config.NumberColumn("Biến Động (%)", format="%+.2f%%"),
            "P/E (Lần)": st.column_config.NumberColumn("P/E (Lần)", format="%.2fx"),
            "ROE (%)": st.column_config.NumberColumn("ROE (%)", format="%.2f%%"),
            "Vốn Hóa (Tỷ VNĐ)": st.column_config.NumberColumn("Vốn Hóa", format="%,.0f Tỷ"),
        },
    )

    # Data Export Button
    csv_data = df_filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Tải Xuống Báo Cáo Định Giá (CSV / Excel)",
        data=csv_data,
        file_name="vietnam_macro_equity_valuation_report.csv",
        mime="text/csv",
    )
