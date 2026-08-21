from typing import Dict, Any, List

def detect_market_regime(macro_data: Dict, vnindex_change_pct: float = 1.5) -> Dict[str, Any]:
    """
    Detect the market regime based on macro indicators and VN-Index momentum.
    
    macro_data expects keys:
      - m2_growth (float)
      - pmi (float)
      - cpi (float)
      - tpcp_10y (float)
      - interbank_on (float)
      - usd_vnd (float)
    """
    def _get_val(key_flat, key_nested, default_val):
        if key_flat in macro_data:
            val = macro_data[key_flat]
            if isinstance(val, (int, float)): return float(val)
        if key_nested in macro_data:
            nested = macro_data[key_nested]
            if isinstance(nested, dict):
                return float(nested.get("latest", default_val))
            elif isinstance(nested, (int, float)):
                return float(nested)
        return float(default_val)

    m2_growth = _get_val('m2_growth', 'm2_money_supply', 14.25)
    pmi = _get_val('pmi', 'pmi_index', 52.40)
    cpi = _get_val('cpi', 'vn_cpi', 4.36)
    tpcp_10y = _get_val('tpcp_10y', 'vn_bond_10y', 2.82)
    interbank_on = _get_val('interbank_on', 'interbank_rate', 4.15)
    usd_vnd = _get_val('usd_vnd', 'usd_vnd_rate', 25420.0)
    
    yield_spread = tpcp_10y - interbank_on
    
    score = 50
    
    if m2_growth > 12.0:
        score += 10
    elif m2_growth < 10.0:
        score -= 10
        
    if pmi > 50.0:
        score += 10
    elif pmi < 50.0:
        score -= 10
        
    if cpi < 3.5:
        score += 10
    elif cpi > 4.5:
        score -= 15
        
    if yield_spread > 1.5:
        score += 10
    elif yield_spread < 0.0:
        score -= 10
        
    if usd_vnd < 25000:
        score += 10
    elif usd_vnd > 25500:
        score -= 15
        
    if vnindex_change_pct > 2.0:
        score += 10
    elif vnindex_change_pct < -2.0:
        score -= 10
        
    score = max(0, min(100, score))
    
    if score >= 65:
        regime = "🟢 RISK-ON (MỞ RỘNG TĂNG TỐC)"
        regime_code = "RISK_ON"
        equity_rec = "70% - 90% Cổ phiếu"
        cash_rec = "10% - 30% Tiền mặt"
        mos_adj = -0.05
        leading = ["Chứng khoán", "Bất động sản", "Thép & Vật Liệu", "Bán lẻ & Tiêu dùng"]
        defensive = ["Tiện ích", "Dược phẩm"]
        summary = "Kinh tế mở rộng, dòng tiền dồi dào, ưu tiên tài sản rủi ro."
    elif score <= 35:
        regime = "🔴 RISK-OFF (PHÒNG THỦ THẬN TRỌNG)"
        regime_code = "RISK_OFF"
        equity_rec = "20% - 40% Cổ phiếu"
        cash_rec = "60% - 80% Tiền mặt"
        mos_adj = 0.05
        leading = ["Thực phẩm & Đồ uống", "Năng lượng & Điện", "Cảng biển & Logistics"]
        defensive = ["Chứng khoán", "Bất động sản"]
        summary = "Rủi ro vĩ mô tăng, áp lực tỷ giá/lạm phát, ưu tiên phòng thủ."
    else:
        regime = "🟡 TRANSITION (TÍCH LŨY PHÂN HÓA)"
        regime_code = "TRANSITION"
        equity_rec = "50% - 60% Cổ phiếu"
        cash_rec = "40% - 50% Tiền mặt"
        mos_adj = 0.0
        leading = ["Ngân hàng", "BĐS Khu công nghiệp", "Công nghệ thông tin"]
        defensive = []
        summary = "Giao đoạn chuyển giao, thị trường phân hóa, tập trung cổ phiếu có nền tảng tốt."
        
    return {
        "regime": regime,
        "regime_code": regime_code,
        "macro_score": score,
        "equity_allocation_rec": equity_rec,
        "cash_allocation_rec": cash_rec,
        "mos_adjustment": mos_adj,
        "leading_sectors": leading,
        "defensive_sectors": defensive,
        "summary": summary
    }
