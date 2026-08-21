import pandas as pd

def get_sector_sensitivities(industry: str):
    """Return (rate_sensitivity, fx_sensitivity)"""
    # Rate Sensitivity: negative for Real Estate, Securities, High Debt. 
    # FX Sensitivity: negative for high foreign debt/import, positive for exporters (DGC, GMD, HPG).
    sensitivities = {
        "Bất động sản": (-0.8, -0.2),
        "BĐS Khu công nghiệp": (-0.4, 0.3),
        "Chứng khoán": (-0.9, 0.0),
        "Ngân hàng": (0.2, -0.1),
        "Thép & Vật Liệu": (-0.3, 0.4), # Exporters benefit from FX
        "Hóa chất cơ bản": (-0.2, 0.5), # DGC
        "Cảng biển & Logistics": (-0.2, 0.4), # GMD
        "Công nghệ thông tin": (-0.1, 0.3),
        "Bán lẻ & Tiêu dùng": (-0.5, -0.3), # Importers hurt
        "Xây dựng & Hạ tầng": (-0.6, -0.2),
        "Năng lượng & Điện": (-0.3, -0.4), # Foreign debt hurt
        "Thực phẩm & Đồ uống": (-0.2, 0.1),
        "Dầu khí": (-0.1, 0.2)
    }
    return sensitivities.get(industry, (-0.2, 0.0))

def simulate_macro_stress(df_stocks: pd.DataFrame, fx_shock_pct: float = 0.0, rate_shock_bps: float = 0.0, erp_shock_pct: float = 0.0) -> pd.DataFrame:
    """
    Simulate macro stress tests on stock valuations.
    """
    if df_stocks.empty:
        return df_stocks
        
    df = df_stocks.copy()
    
    re_rated_targets = []
    re_rated_upsides = []
    valuation_impacts = []
    
    for idx, row in df.iterrows():
        industry = row.get("Ngành") or row.get("Nhóm Ngành", "")
        beta = row.get("Beta") or row.get("beta", 1.0)
        target_price = row.get("🎯 Định Giá Hợp Lý (VNĐ)") or row.get("Giá Mục Tiêu") or row.get("target_price", 0)
        market_price = row.get("Thị Giá Sàn (VNĐ)") or row.get("Thị Giá") or row.get("official_price", 0)
        
        if pd.isna(target_price) or target_price <= 0 or pd.isna(market_price) or market_price <= 0:
            re_rated_targets.append(target_price)
            re_rated_upsides.append(row.get("🚀 Dư Địa Tăng (%)") or row.get("Upside (%)", 0.0))
            valuation_impacts.append(0.0)
            continue
            
        rate_sens, fx_sens = get_sector_sensitivities(industry)
        
        re_rated_target = target_price * (1.0 + rate_sens * (rate_shock_bps / 1000.0) + fx_sens * (fx_shock_pct / 100.0) - beta * (erp_shock_pct / 100.0))
        re_rated_target = max(re_rated_target, 0.5 * market_price)
        
        re_rated_upside = ((re_rated_target - market_price) / market_price) * 100.0
        val_impact = ((re_rated_target - target_price) / target_price) * 100.0
        
        re_rated_targets.append(int(round(re_rated_target / 100.0) * 100))
        re_rated_upsides.append(round(re_rated_upside, 1))
        valuation_impacts.append(round(val_impact, 1))
        
    df["Định Giá Sau Sốc (VNĐ)"] = re_rated_targets
    df["Tác Động Định Giá (%)"] = valuation_impacts
    df["Dư Địa Sau Sốc (%)"] = re_rated_upsides
    
    return df
