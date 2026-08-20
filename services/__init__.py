"""Services package for Macro Terminal."""
from services.macro_service import fetch_macro_data
from services.nlp_service import fetch_and_analyze_news
from services.stock_service import fetch_stock_fundamentals, STOCK_FUNDAMENTALS_REGISTRY, get_all_registered_stocks

try:
    from services.valuation_engine import compute_valuation
except ImportError:
    pass

__all__ = [
    "fetch_macro_data",
    "fetch_and_analyze_news",
    "fetch_stock_fundamentals",
    "STOCK_FUNDAMENTALS_REGISTRY",
    "get_all_registered_stocks",
]

