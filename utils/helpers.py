"""Utility functions and formatting helpers for Macro Terminal."""
import os
import re
from typing import Any, Optional
import streamlit as st


def get_safe_secret(key: str, default: str = "") -> str:
    """
    Safely retrieve a secret from Streamlit secrets or OS environment variables.
    Never throws StreamlitSecretNotFoundError even if secrets.toml is missing.
    """
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)


def clean_html(raw_html: Optional[str]) -> str:
    """Remove HTML tags and clean whitespace from raw text."""
    if not raw_html or not isinstance(raw_html, str):
        return ""
    # Strip HTML tags
    cleanr = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
    cleantext = re.sub(cleanr, " ", raw_html)
    # Normalize whitespaces
    cleantext = re.sub(r"\s+", " ", cleantext).strip()
    return cleantext


def format_currency_vnd(val: Any) -> str:
    """Format numeric value into Vietnamese Dong currency string (Billions/Tỷ or Millions/Tr)."""
    if val is None or val == "" or str(val) == "nan":
        return "N/A"
    try:
        num = float(val)
        if abs(num) >= 1_000_000_000_000:
            return f"{num / 1_000_000_000_000:,.2f} T nghìn tỷ"
        elif abs(num) >= 1_000_000_000:
            return f"{num / 1_000_000_000:,.2f} Tỷ"
        elif abs(num) >= 1_000_000:
            return f"{num / 1_000_000:,.2f} Tr"
        else:
            return f"{num:,.0f}"
    except (ValueError, TypeError):
        return str(val)


def format_percent(val: Any, decimals: int = 2) -> str:
    """Format numeric value to percentage string."""
    if val is None or val == "" or str(val) == "nan":
        return "N/A"
    try:
        num = float(val)
        return f"{num:.{decimals}f}%"
    except (ValueError, TypeError):
        return str(val)


def format_number(val: Any, decimals: int = 2) -> str:
    """Format standard numeric value with decimal places."""
    if val is None or val == "" or str(val) == "nan":
        return "N/A"
    try:
        num = float(val)
        return f"{num:,.{decimals}f}"
    except (ValueError, TypeError):
        return str(val)


def is_valid_ticker(ticker: str) -> bool:
    """Validate if ticker is a valid Vietnamese stock ticker format (usually 3 uppercase alphanumeric characters)."""
    if not ticker or not isinstance(ticker, str):
        return False
    cleaned = ticker.strip().upper()
    return bool(re.match(r"^[A-Z0-9]{3}$", cleaned))
