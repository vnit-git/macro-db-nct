import pandas as pd
import math

def calc_dynamic_mos(industry: str, beta: float = 1.0, regime_code: str = "TRANSITION") -> float:
    """
    Calculate dynamic Margin of Safety based on sector risk, beta, and market regime.
    """
    base_mos = 0.15
    if industry in ["Ngân hàng", "Công nghệ thông tin", "Bán lẻ & Tiêu dùng"]:
        base_mos = 0.10
    elif industry in ["Thực phẩm & Đồ uống", "Năng lượng & Điện", "Cảng biển & Logistics"]:
        base_mos = 0.12
    elif industry in ["Chứng khoán", "Thép & Vật Liệu", "Hóa chất cơ bản"]:
        base_mos = 0.18
    elif industry in ["Bất động sản", "BĐS Khu công nghiệp", "Xây dựng & Hạ tầng", "Dầu khí"]:
        base_mos = 0.22
        
    beta_adj = max(-0.05, min(0.08, (beta - 1.0) * 0.10))
    
    if regime_code == "RISK_ON":
        regime_adj = -0.03
    elif regime_code == "RISK_OFF":
        regime_adj = 0.05
    else:
        regime_adj = 0.0
        
    final_mos = base_mos + beta_adj + regime_adj
    final_mos = max(0.08, min(0.35, final_mos))
    
    return round(final_mos, 3)

def calc_position_sizing(df_stocks: pd.DataFrame, total_capital_vnd: float = 1_000_000_000, max_single_weight: float = 0.25) -> pd.DataFrame:
    """
    Calculate position sizing using risk parity proxy and upside boosting.
    """
    if df_stocks.empty:
        return df_stocks
        
    df = df_stocks.copy()
    
    raw_weights = []
    
    for idx, row in df.iterrows():
        beta = row.get("Beta") or row.get("beta", 1.0)
        upside = row.get("🚀 Dư Địa Tăng (%)") or row.get("Upside (%)", 0.0)
        if pd.isna(upside):
            upside = 0.0
            
        risk_score = float(beta) * (1.0 + max(0, -float(upside)/100.0))
        if risk_score <= 0:
            risk_score = 0.1
            
        raw_weight = 1.0 / risk_score
        raw_weight = raw_weight * (1.0 + max(0, float(upside)/100.0) * 0.5)
        raw_weights.append(raw_weight)
        
    df['Raw_Weight'] = raw_weights
    total_raw = sum(raw_weights)
    
    if total_raw > 0:
        df['Tỷ Trọng Đề Xuất (%)'] = df['Raw_Weight'] / total_raw
    else:
        df['Tỷ Trọng Đề Xuất (%)'] = 0.0
        
    # Cap single weight
    capped = False
    while True:
        excess = 0.0
        total_uncapped = 0.0
        
        for idx, row in df.iterrows():
            if df.at[idx, 'Tỷ Trọng Đề Xuất (%)'] > max_single_weight:
                excess += df.at[idx, 'Tỷ Trọng Đề Xuất (%)'] - max_single_weight
                df.at[idx, 'Tỷ Trọng Đề Xuất (%)'] = max_single_weight
            elif df.at[idx, 'Tỷ Trọng Đề Xuất (%)'] < max_single_weight:
                total_uncapped += df.at[idx, 'Tỷ Trọng Đề Xuất (%)']
                
        if excess < 1e-5:
            break
            
        if total_uncapped > 0:
            for idx, row in df.iterrows():
                if df.at[idx, 'Tỷ Trọng Đề Xuất (%)'] < max_single_weight:
                    df.at[idx, 'Tỷ Trọng Đề Xuất (%)'] += excess * (df.at[idx, 'Tỷ Trọng Đề Xuất (%)'] / total_uncapped)
        else:
            break
            
    df['Phân Bổ Vốn (Triệu VNĐ)'] = (df['Tỷ Trọng Đề Xuất (%)'] * total_capital_vnd) / 1_000_000
    
    target_volumes = []
    for idx, row in df.iterrows():
        alloc_vnd = row['Tỷ Trọng Đề Xuất (%)'] * total_capital_vnd
        price = row.get("Thị Giá Sàn (VNĐ)") or row.get("Thị Giá", 0)
        if pd.notna(price) and price > 0:
            vol = math.floor(alloc_vnd / float(price))
        else:
            vol = 0
        target_volumes.append(vol)
        
    df['Khối Lượng Mục Tiêu (CP)'] = target_volumes
    df['Tỷ Trọng Đề Xuất (%)'] = (df['Tỷ Trọng Đề Xuất (%)'] * 100).round(2)
    df['Phân Bổ Vốn (Triệu VNĐ)'] = df['Phân Bổ Vốn (Triệu VNĐ)'].round(1)
    
    df = df.drop(columns=['Raw_Weight'])
    return df
