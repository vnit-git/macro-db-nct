import math
from typing import Dict, Tuple

DEFAULT_RISK_FREE_RATE = 0.0282
DEFAULT_EQUITY_RISK_PREMIUM = 0.08
DEFAULT_TERMINAL_GROWTH = 0.05
DEFAULT_MARGIN_OF_SAFETY = 0.15

def calc_forward_pe_target(eps_ttm: float, eps_growth_rate: float, target_pe_multiple: float, margin_of_safety: float = 0.0) -> Tuple[int, str]:
    """
    Calculate 12-Month Fair Value Target using Forward P/E method.
    Formula: Fair Value = EPS_TTM * (1 + growth) * target_PE
    """
    if eps_ttm <= 0:
        return 0, "Forward P/E: Invalid EPS (<= 0)"
    if eps_growth_rate < -0.5:
        return 0, "Forward P/E: Negative growth beyond threshold"
    
    # Fair Value (Intrinsic Value)
    target_price_raw = eps_ttm * (1.0 + eps_growth_rate) * target_pe_multiple
    
    if target_price_raw <= 0:
        return 0, "Forward P/E: Invalid target"
        
    target_price = int(round(target_price_raw / 500.0) * 500)
    return target_price, f"Forward P/E ({target_pe_multiple:.1f}x): {target_price:,.0f}đ"

def calc_justified_pb_target(bvps: float, roe: float, cost_of_equity: float = None, terminal_growth: float = DEFAULT_TERMINAL_GROWTH, margin_of_safety: float = 0.0, risk_free_rate: float = DEFAULT_RISK_FREE_RATE, equity_risk_premium: float = DEFAULT_EQUITY_RISK_PREMIUM, beta: float = 1.0, industry: str = "") -> Tuple[int, str]:
    """
    Calculate 12-Month Fair Value Target using Justified P/B & Residual Income method.
    Formula: Fair Value = BVPS * Target_PB_Multiple
    """
    if bvps <= 0:
        return 0, "Justified P/B: Invalid BVPS"
        
    if cost_of_equity is None:
        cost_of_equity = risk_free_rate + beta * equity_risk_premium
        
    # Sector-aware Justified P/B multiple
    coe_floor = max(0.08, cost_of_equity)
    if "Bất động sản" in industry:
        target_pb = 1.6
    elif "Ngân hàng" in industry:
        target_pb = max(1.2, min(2.8, (roe / coe_floor) * 1.3))
    elif "Chứng khoán" in industry:
        target_pb = max(1.4, min(2.5, (roe / coe_floor) * 1.4))
    elif "Công nghệ" in industry:
        target_pb = max(2.5, min(6.0, (roe / coe_floor) * 2.0))
    else:
        target_pb = max(1.2, min(3.5, (roe / coe_floor) * 1.25))
        
    target_price_raw = bvps * target_pb
    target_price = int(round(target_price_raw / 500.0) * 500)
    return target_price, f"Justified P/B ({target_pb:.2f}x): {target_price:,.0f}đ"

def calc_blended_target(forward_pe_target: int, justified_pb_target: int, weight_pe: float = 0.5, weight_pb: float = 0.5) -> Tuple[int, str]:
    """
    Calculate blended target price from Forward P/E and Justified P/B targets.
    """
    if forward_pe_target == 0 and justified_pb_target == 0:
        return 0, "N/A — Không đủ dữ liệu định giá"
    if forward_pe_target == 0:
        return justified_pb_target, f"Justified P/B (100%): {justified_pb_target:,.0f}đ"
    if justified_pb_target == 0:
        return forward_pe_target, f"Forward P/E (100%): {forward_pe_target:,.0f}đ"
        
    total_weight = weight_pe + weight_pb
    norm_weight_pe = weight_pe / total_weight
    norm_weight_pb = weight_pb / total_weight
    
    blended_target_raw = (forward_pe_target * norm_weight_pe) + (justified_pb_target * norm_weight_pb)
    blended_target = int(round(blended_target_raw / 500.0) * 500)
    desc = f"Blended ({norm_weight_pe:.0%} FwdPE + {norm_weight_pb:.0%} JP/B): {blended_target:,.0f}đ"
    return blended_target, desc

def compute_valuation(profile: Dict, live_price: int = 0, regime_code: str = "TRANSITION") -> Dict:
    """
    Institutional valuation engine: computes quantitative model and blends with consensus equity research target.
    """
    from services.risk_allocator import calc_dynamic_mos
    
    eps_ttm = profile.get("eps_ttm")
    eps_growth = profile.get("eps_growth", 0.15)
    target_pe = profile.get("target_pe_multiple")
    bvps = profile.get("bvps")
    
    raw_roe = profile.get("roe") if profile.get("roe") is not None else profile.get("official_roe")
    if raw_roe is not None:
        roe = raw_roe / 100.0 if raw_roe > 1.0 else raw_roe
    else:
        roe = 0.15
        
    beta = profile.get("beta", 1.0)
    industry = profile.get("industry", "")
    target_consensus = profile.get("target_price", 0)
    val_method = profile.get("valuation_method", "Consensus Target")
    val_weights = profile.get("valuation_weights", {"pe": 0.5, "pb": 0.5})
    
    mos = calc_dynamic_mos(industry, beta, regime_code=regime_code)
    
    pe_target = 0
    pe_desc = ""
    pb_target = 0
    pb_desc = ""
    
    if eps_ttm is not None and eps_growth is not None and target_pe is not None and eps_ttm > 0:
        pe_target, pe_desc = calc_forward_pe_target(
            eps_ttm=eps_ttm,
            eps_growth_rate=eps_growth,
            target_pe_multiple=target_pe,
            margin_of_safety=0.0
        )
        
    if bvps is not None and roe is not None and bvps > 0:
        pb_target, pb_desc = calc_justified_pb_target(
            bvps=bvps,
            roe=roe,
            beta=beta,
            industry=industry,
            margin_of_safety=0.0
        )
        
    quant_target, blended_desc = calc_blended_target(
        pe_target, pb_target, val_weights.get("pe", 0.5), val_weights.get("pb", 0.5)
    )
    
    # Synthesize Quantitative Forward Model with Consensus Equity Research Target
    if quant_target > 0 and target_consensus > 0:
        final_target = int(round((quant_target * 0.5 + target_consensus * 0.5) / 500.0) * 500)
        final_desc = f"{val_method} | {blended_desc}"
        is_computed = True
    elif quant_target > 0:
        final_target = quant_target
        final_desc = blended_desc
        is_computed = True
    elif target_consensus > 0:
        final_target = target_consensus
        final_desc = val_method
        is_computed = False
    else:
        final_target = int(round((live_price * 1.20) / 500.0) * 500) if live_price > 0 else 0
        final_desc = "Baseline Intrinsic Multiple (+20%)"
        is_computed = False

    return {
        "computed_target": final_target,
        "computed_method_desc": final_desc,
        "is_engine_computed": is_computed,
        "applied_mos": mos,
        "details": {
            "pe_target": pe_target,
            "pe_desc": pe_desc,
            "pb_target": pb_target,
            "pb_desc": pb_desc,
            "consensus_target": target_consensus,
        }
    }


