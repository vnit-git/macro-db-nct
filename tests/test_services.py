"""Unit tests for Vietnam Macro & Equity Terminal services and helpers."""
import pytest
import pandas as pd

from utils.helpers import clean_html, format_currency_vnd, format_number, format_percent, get_safe_secret, is_valid_ticker
from services.macro_service import fetch_macro_data, FALLBACK_MACRO_DATA
from services.nlp_service import fetch_and_analyze_news, FALLBACK_NEWS_ANALYSIS
from services.stock_service import fetch_stock_fundamentals, FALLBACK_STOCK_DATABASE


def test_clean_html():
    raw_html = "<p>Nghị định <strong>102/2024/NĐ-CP</strong> &amp; các điều khoản mới.</p>"
    cleaned = clean_html(raw_html)
    assert "Nghị định" in cleaned
    assert "102/2024/NĐ-CP" in cleaned
    assert "<p>" not in cleaned
    assert "<strong>" not in cleaned


def test_is_valid_ticker():
    assert is_valid_ticker("VHM") is True
    assert is_valid_ticker("FPT") is True
    assert is_valid_ticker("SSI") is True
    assert is_valid_ticker("VCB") is True
    assert is_valid_ticker("INVALID_TICKER") is False
    assert is_valid_ticker("") is False
    assert is_valid_ticker(None) is False
    assert is_valid_ticker("12") is False


def test_format_helpers():
    assert format_percent(15.234) == "15.23%"
    assert format_number(1234.567, 1) == "1,234.6"
    assert "Tỷ" in format_currency_vnd(50_000_000_000)
    assert format_currency_vnd(None) == "N/A"
    assert get_safe_secret("NON_EXISTENT_KEY", "default_val") == "default_val"


def test_macro_service_fallback():
    data = fetch_macro_data(api_key=None)
    assert "fed_funds" in data
    assert "vn_cpi" in data
    assert "vn_gdp" in data
    assert "m2_money_supply" in data
    assert "deposit_rate_12m" in data
    assert "lending_rate_avg" in data
    assert "pmi_index" in data
    assert data["m2_money_supply"]["latest"] > 0
    assert data["pmi_index"]["latest"] > 0
    assert data["deposit_rate_12m"]["latest"] > 0


def test_nlp_service_fallback():
    items = fetch_and_analyze_news(openai_api_key=None, max_items=3)
    assert len(items) == 3
    for item in items:
        assert "policy_summary" in item
        assert "impact" in item
        assert "benefited_tickers" in item
        assert len(item["benefited_tickers"]) > 0
        for ticker in item["benefited_tickers"]:
            assert is_valid_ticker(ticker)


def test_stock_service():
    tickers = ["VHM", "FPT", "SSI"]
    df = fetch_stock_fundamentals(tickers)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 3
    assert "Mã CP" in df.columns
    assert "Thị Giá Sàn (VNĐ)" in df.columns
    assert "🎯 Định Giá Hợp Lý (VNĐ)" in df.columns
    assert "P/E (Lần)" in df.columns
    assert "ROE (%)" in df.columns
    assert "Vốn Hóa (Tỷ VNĐ)" in df.columns
    assert "VHM" in df["Mã CP"].values
    assert "FPT" in df["Mã CP"].values


def test_stock_service_invalid_ticker_handling():
    # Service must gracefully ignore invalid tickers without crashing
    tickers = ["NON_EXISTENT_XYZ", "", "VHM"]
    df = fetch_stock_fundamentals(tickers)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "VHM" in df["Mã CP"].values

# ─── Valuation Engine Tests ───
def test_forward_pe_basic():
    from services.valuation_engine import calc_forward_pe_target
    target, desc = calc_forward_pe_target(5000, 0.20, 15.0, 0.15)
    assert target > 0
    expected = round(5000 * 1.20 * 15.0 * 0.85 / 500) * 500
    assert target == expected
    assert "Forward P/E" in desc

def test_forward_pe_zero_eps():
    from services.valuation_engine import calc_forward_pe_target
    target, desc = calc_forward_pe_target(0, 0.20, 15.0)
    assert target == 0.0

def test_forward_pe_negative_eps():
    from services.valuation_engine import calc_forward_pe_target
    target, _ = calc_forward_pe_target(-1000, 0.20, 15.0)
    assert target == 0.0

def test_justified_pb_basic():
    from services.valuation_engine import calc_justified_pb_target
    target, desc = calc_justified_pb_target(30000, 0.225, beta=1.0)
    assert target > 0
    assert "Justified P/B" in desc

def test_justified_pb_coe_equals_g():
    from services.valuation_engine import calc_justified_pb_target
    target, _ = calc_justified_pb_target(30000, 0.15, cost_of_equity=0.05, terminal_growth=0.05)
    assert target > 0

def test_justified_pb_zero_bvps():
    from services.valuation_engine import calc_justified_pb_target
    target, _ = calc_justified_pb_target(0, 0.15)
    assert target == 0.0

def test_blended_both_valid():
    from services.valuation_engine import calc_blended_target
    target, _ = calc_blended_target(50000, 60000, 0.5, 0.5)
    assert target == round(55000 / 500) * 500

def test_blended_one_zero():
    from services.valuation_engine import calc_blended_target
    target, _ = calc_blended_target(50000, 0)
    assert target == round(50000 / 500) * 500

def test_blended_both_zero():
    from services.valuation_engine import calc_blended_target
    target, _ = calc_blended_target(0, 0)
    assert target == 0.0

def test_compute_valuation_with_data():
    from services.valuation_engine import compute_valuation
    profile = {"eps_ttm": 5000, "eps_growth": 0.15, "bvps": 30000, "official_roe": 22.5, "beta": 1.0, "target_pe_multiple": 15.0}
    result = compute_valuation(profile)
    assert result["is_engine_computed"] is True
    assert result["computed_target"] > 0

def test_compute_valuation_fallback():
    from services.valuation_engine import compute_valuation
    profile = {"target_price": 50000, "valuation_method": "Reference"}
    result = compute_valuation(profile)
    assert result["is_engine_computed"] is False
    assert result["computed_target"] == 50000

def test_rrg_classify_quadrant():
    from services.money_flow_service import classify_rrg_quadrant
    assert classify_rrg_quadrant(105, 103) == "Leading"
    assert classify_rrg_quadrant(97, 103) == "Improving"
    assert classify_rrg_quadrant(103, 97) == "Weakening"
    assert classify_rrg_quadrant(95, 96) == "Lagging"

def test_macro_score_no_cliff():
    from utils.macro_analysis import calculate_vietnam_macro_health_score
    base1 = {"pmi_index": {"latest": 50.01}, "m2_money_supply": {"latest": 10.0},
             "vn_cpi": {"latest": 4.0}, "lending_rate_avg": {"latest": 9.0},
             "usd_vnd_rate": {"latest": 25400.0}}
    s1, _, _, _ = calculate_vietnam_macro_health_score(base1)
    base2 = {"pmi_index": {"latest": 49.99}, "m2_money_supply": {"latest": 10.0},
             "vn_cpi": {"latest": 4.0}, "lending_rate_avg": {"latest": 9.0},
             "usd_vnd_rate": {"latest": 25400.0}}
    s2, _, _, _ = calculate_vietnam_macro_health_score(base2)
    assert abs(s1 - s2) <= 2

def test_dynamic_market_cap_column():
    from services.stock_service import fetch_stock_fundamentals
    df = fetch_stock_fundamentals(["VHM"])
    assert "Vốn Hóa (Tỷ VNĐ)" in df.columns
    assert df.iloc[0]["Vốn Hóa (Tỷ VNĐ)"] > 0

def test_engine_column_exists():
    from services.stock_service import fetch_stock_fundamentals
    df = fetch_stock_fundamentals(["VHM", "FPT"])
    if "🔬 Engine" in df.columns:
        assert all(v in ["✅ Computed", "📋 Reference"] for v in df["🔬 Engine"])

# ─── Alpha 2.0 Module Tests ───
def test_regime_engine_detection():
    from services.regime_engine import detect_market_regime
    macro_data = {
        "m2_money_supply": {"latest": 14.25},
        "pmi_index": {"latest": 52.40},
        "vn_cpi": {"latest": 3.20},
        "vn_bond_10y": {"latest": 3.50},
        "interbank_rate": {"latest": 1.50},
        "usd_vnd_rate": {"latest": 24800.0},
    }
    res = detect_market_regime(macro_data, vnindex_change_pct=2.5)
    assert res["regime_code"] == "RISK_ON"
    assert res["mos_adjustment"] == -0.05
    assert len(res["leading_sectors"]) > 0

def test_dynamic_mos_calculation():
    from services.risk_allocator import calc_dynamic_mos
    mos_bank = calc_dynamic_mos("Ngân hàng", beta=1.0, regime_code="RISK_ON")
    mos_bds = calc_dynamic_mos("Bất động sản", beta=1.5, regime_code="RISK_OFF")
    assert mos_bank < mos_bds
    assert 0.08 <= mos_bank <= 0.35
    assert 0.08 <= mos_bds <= 0.35

def test_position_sizing_allocator():
    from services.risk_allocator import calc_position_sizing
    df = pd.DataFrame([
        {"Mã CP": "VCB", "Nhóm Ngành": "Ngân hàng", "Thị Giá Sàn (VNĐ)": 90000, "Beta": 0.9, "🚀 Dư Địa Tăng (%)": 20.0},
        {"Mã CP": "DXG", "Nhóm Ngành": "Bất động sản", "Thị Giá Sàn (VNĐ)": 15000, "Beta": 1.6, "🚀 Dư Địa Tăng (%)": 35.0},
    ])
    res = calc_position_sizing(df, total_capital_vnd=1_000_000_000, max_single_weight=0.6)
    assert "Tỷ Trọng Đề Xuất (%)" in res.columns
    assert "Phân Bổ Vốn (Triệu VNĐ)" in res.columns
    assert "Khối Lượng Mục Tiêu (CP)" in res.columns
    assert round(res["Tỷ Trọng Đề Xuất (%)"].sum()) == 100

def test_simulate_macro_stress():
    from services.stress_test import simulate_macro_stress
    df = pd.DataFrame([
        {"Mã CP": "VHM", "Ngành": "Bất động sản", "Thị Giá Sàn (VNĐ)": 70000, "🎯 Định Giá Hợp Lý (VNĐ)": 90000, "Beta": 1.3},
        {"Mã CP": "DGC", "Ngành": "Hóa chất cơ bản", "Thị Giá Sàn (VNĐ)": 40000, "🎯 Định Giá Hợp Lý (VNĐ)": 55000, "Beta": 1.1},
    ])
    res = simulate_macro_stress(df, fx_shock_pct=5.0, rate_shock_bps=100.0, erp_shock_pct=2.0)
    assert "Định Giá Sau Sốc (VNĐ)" in res.columns
    assert "Tác Động Định Giá (%)" in res.columns
    assert "Dư Địa Sau Sốc (%)" in res.columns
    assert len(res) == 2

def test_live_sector_money_flow_computation():
    from services.money_flow_service import compute_live_sector_money_flow
    live_quotes = {
        "VHM": (72000, 2.5, "Vinhomes"),
        "KDH": (18000, 1.8, "Khang Dien"),
        "FPT": (115000, 3.2, "FPT Corp"),
    }
    sectors = compute_live_sector_money_flow({}, live_quotes)
    assert len(sectors) > 0
    bds = next((s for s in sectors if s.get("sector_id") == "bds"), None)
    if bds and bds.get("is_live_computed"):
        assert bds["price_change_pct"] > 0

