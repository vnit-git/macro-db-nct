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
    assert "P/E" in df.columns
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
