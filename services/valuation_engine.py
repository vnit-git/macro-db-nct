import math
from typing import Dict, Tuple

DEFAULT_RISK_FREE_RATE = 0.0282
DEFAULT_EQUITY_RISK_PREMIUM = 0.08
DEFAULT_TERMINAL_GROWTH = 0.05
DEFAULT_MARGIN_OF_SAFETY = 0.15

def calc_forward_pe_target(eps_ttm: float, eps_growth_rate: float, target_pe_multiple: float, margin_of_safety: float = DEFAULT_MARGIN_OF_SAFETY) -> Tuple[int, str]:
    """
    Calculate target price using Forward P/E method.
    Target = EPS_TTM * (1 + growth) * target_PE * (1 - MoS)
    """
    if eps_ttm <= 0:
        return 0, "Forward P/E: Invalid EPS (<= 0)"
    if eps_growth_rate < 0:
        return 0, "Forward P/E: Negative growth"
    
    target_price_raw = eps_ttm * (1 + eps_growth_rate) * target_pe_multiple * (1 - margin_of_safety)
    
    if target_price_raw <= 0:
        return 0, "Forward P/E: Invalid target"
        
    target_price = int(round(target_price_raw / 500.0) * 500)
    return target_price, "Forward P/E Method"

def calc_justified_pb_target(bvps: float, roe: float, cost_of_equity: float = None, terminal_growth: float = DEFAULT_TERMINAL_GROWTH, margin_of_safety: float = DEFAULT_MARGIN_OF_SAFETY, risk_free_rate: float = DEFAULT_RISK_FREE_RATE, equity_risk_premium: float = DEFAULT_EQUITY_RISK_PREMIUM, beta: float = 1.0) -> Tuple[int, str]:
    """
    Calculate target price using Justified P/B method.
    Justified P/B = (ROE - g) / (COE - g)
    """
    if bvps <= 0:
        return 0, "Justified P/B: Invalid BVPS"
        
    if cost_of_equity is None:
        cost_of_equity = risk_free_rate + beta * equity_risk_premium
        
    # Handle edge case: COE <= g
    if cost_of_equity <= terminal_growth:
        cost_of_equity = terminal_growth + 0.02
        
    justified_pb_raw = (roe - terminal_growth) / (cost_of_equity - terminal_growth)
    
    # Cap between 0.5 and 6.0
    justified_pb = max(0.5, min(6.0, justified_pb_raw))
    
    target_price_raw = bvps * justified_pb * (1 - margin_of_safety)
    target_price = int(round(target_price_raw / 500.0) * 500)
    return target_price, "Justified P/B Method"

def calc_blended_target(forward_pe_target: int, justified_pb_target: int, weight_pe: float = 0.5, weight_pb: float = 0.5) -> Tuple[int, str]:
    """
    Calculate blended target price from Forward P/E and Justified P/B targets.
    Returns (blended_target_price, description_string).
    """
    if forward_pe_target == 0 and justified_pb_target == 0:
        return 0, "N/A — Không đủ dữ liệu định giá"
    if forward_pe_target == 0:
        return justified_pb_target, f"Justified P/B (100%): {justified_pb_target:,.0f}đ"
    if justified_pb_target == 0:
        return forward_pe_target, f"Forward P/E (100%): {forward_pe_target:,.0f}đ"
        
    # Normalize weights
    total_weight = weight_pe + weight_pb
    norm_weight_pe = weight_pe / total_weight
    norm_weight_pb = weight_pb / total_weight
    
    blended_target_raw = (forward_pe_target * norm_weight_pe) + (justified_pb_target * norm_weight_pb)
    blended_target = int(round(blended_target_raw / 500.0) * 500)
    desc = f"Blended ({norm_weight_pe:.0%} FwdPE + {norm_weight_pb:.0%} JP/B): {blended_target:,.0f}đ"
    return blended_target, desc

def compute_valuation(profile: Dict, live_price: int = 0) -> Dict:
    """
    Master orchestrator to compute valuation based on available profile data.
    """
    # Extract needed fields from profile
    eps_ttm = profile.get("eps_ttm")
    eps_growth = profile.get("eps_growth")
    target_pe = profile.get("target_pe_multiple")
    bvps = profile.get("bvps")
    
    # ROE can be decimal (0.15) or percentage (15.0) or official_roe
    raw_roe = profile.get("roe") if profile.get("roe") is not None else profile.get("official_roe")
    if raw_roe is not None:
        roe = raw_roe / 100.0 if raw_roe > 1.0 else raw_roe
    else:
        roe = None
        
    beta = profile.get("beta", 1.0)
    val_weights = profile.get("valuation_weights", {"pe": 0.5, "pb": 0.5})
    
    pe_target = 0
    pe_desc = ""
    pb_target = 0
    pb_desc = ""
    
    if eps_ttm is not None and eps_growth is not None and target_pe is not None and eps_ttm > 0:
        pe_target, pe_desc = calc_forward_pe_target(
            eps_ttm=eps_ttm,
            eps_growth_rate=eps_growth,
            target_pe_multiple=target_pe
        )
        
    if bvps is not None and roe is not None and bvps > 0:
        pb_target, pb_desc = calc_justified_pb_target(
            bvps=bvps,
            roe=roe,
            beta=beta
        )
        
    blended_target, blended_desc = calc_blended_target(
        pe_target, pb_target, val_weights.get("pe", 0.5), val_weights.get("pb", 0.5)
    )
    
    is_engine_computed = blended_target > 0
    
    if is_engine_computed:
        return {
            "computed_target": blended_target,
            "computed_method_desc": blended_desc,
            "is_engine_computed": True,
            "details": {
                "pe_target": pe_target,
                "pe_desc": pe_desc,
                "pb_target": pb_target,
                "pb_desc": pb_desc,
            }
        }
    else:
        # Fallback
        fallback_target = profile.get("target_price", 0)
        return {
            "computed_target": fallback_target,
            "computed_method_desc": profile.get("valuation_method", "Hardcoded (Data Insufficient)"),
            "is_engine_computed": False,
            "details": {}
        }

