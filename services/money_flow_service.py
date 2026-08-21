"""
Sector Capital Rotation and Money Flow Intelligence Engine.
Calculates Relative Rotation Graph (RRG) coordinates, Net Capital Inflow/Outflow,
and generates AI-powered sector rotation insights.
"""
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

SECTOR_MONEY_FLOW_DATA: List[Dict[str, Any]] = [
    {
        "sector_id": "bds",
        "name": "Bất Động Sản",
        "rs_ratio": 104.5,
        "rs_momentum": 103.8,
        "prev_ratio": 102.1,
        "prev_momentum": 101.2,
        "quadrant": "Leading",
        "net_inflow_bil": 1420,
        "liquidity_pct": 24.5,
        "price_change_pct": 2.15,
        "recommendation": "🚀 TĂNG TỶ TRỌNG",
        "status_color": "#2ECC71",
        "top_stocks": ["VHM", "KDH", "NLG", "DXG", "PDR"],
        "is_live_computed": False,
        "summary": "Dòng tiền lớn đổ vào sau khi các nút thắt pháp lý Luật Đất Đai được tháo gỡ. Sức mạnh giá và xung lực đều vượt trội thị trường.",
    },
    {
        "sector_id": "cntt",
        "name": "Công Nghệ Thông Tin",
        "rs_ratio": 106.2,
        "rs_momentum": 105.1,
        "prev_ratio": 104.8,
        "prev_momentum": 103.0,
        "quadrant": "Leading",
        "net_inflow_bil": 890,
        "liquidity_pct": 12.8,
        "price_change_pct": 2.45,
        "recommendation": "🚀 NẮM GIỮ / MUA GIA TĂNG",
        "status_color": "#2ECC71",
        "top_stocks": ["FPT", "CMG", "CTR", "ELC"],
        "is_live_computed": False,
        "summary": "Được hỗ trợ bởi làn sóng AI, chuyển đổi số toàn cầu và chính sách ưu đãi thuế bán dẫn. Thu hút mạnh vốn tổ chức và khối ngoại.",
    },
    {
        "sector_id": "ck",
        "name": "Chứng Khoán",
        "rs_ratio": 101.8,
        "rs_momentum": 102.5,
        "prev_ratio": 100.1,
        "prev_momentum": 98.2,
        "quadrant": "Leading",
        "net_inflow_bil": 650,
        "liquidity_pct": 18.2,
        "price_change_pct": 1.53,
        "recommendation": "🚀 NẮM GIỮ",
        "status_color": "#2ECC71",
        "top_stocks": ["SSI", "VCI", "HCM", "VND", "MBS"],
        "is_live_computed": False,
        "summary": "Hưởng lợi trực tiếp từ thanh khoản thị trường tăng cao và kỳ vọng nâng hạng thị trường chứng khoán FTSE.",
    },
    {
        "sector_id": "hatang",
        "name": "Đầu Tư Công & Hạ Tầng",
        "rs_ratio": 98.5,
        "rs_momentum": 103.2,
        "prev_ratio": 97.1,
        "prev_momentum": 95.8,
        "quadrant": "Improving",
        "net_inflow_bil": 480,
        "liquidity_pct": 8.5,
        "price_change_pct": 1.15,
        "recommendation": "🔄 MUA ĐÓN ĐẦU",
        "status_color": "#00ADB5",
        "top_stocks": ["VCG", "HHV", "C4G", "KSB"],
        "is_live_computed": False,
        "summary": "Xung lực dòng tiền tăng vọt (Momentum > 103) đang kéo chỉ số RS dịch chuyển từ vùng Tụt Hậu sang Dẫn Dắt khi tiến độ giải ngân Q3-Q4 tăng tốc.",
    },
    {
        "sector_id": "dien",
        "name": "Năng Lượng & Điện",
        "rs_ratio": 99.2,
        "rs_momentum": 101.8,
        "prev_ratio": 98.0,
        "prev_momentum": 96.5,
        "quadrant": "Improving",
        "net_inflow_bil": 310,
        "liquidity_pct": 6.2,
        "price_change_pct": 1.40,
        "recommendation": "🔄 MUA TÍCH LŨY",
        "status_color": "#00ADB5",
        "top_stocks": ["PC1", "GEG", "HDG", "REE", "POW"],
        "is_live_computed": False,
        "summary": "Dòng tiền quay trở lại sau khi cơ chế DPPA và Quy hoạch điện VIII được cụ thể hóa, triển vọng doanh nghiệp điện năng lượng tái tạo phục hồi.",
    },
    {
        "sector_id": "nh",
        "name": "Ngân Hàng",
        "rs_ratio": 102.0,
        "rs_momentum": 98.2,
        "prev_ratio": 103.5,
        "prev_momentum": 101.0,
        "quadrant": "Weakening",
        "net_inflow_bil": 220,
        "liquidity_pct": 21.0,
        "price_change_pct": 0.86,
        "recommendation": "⚠️ QUAN SÁT / CHỐT LỜI TỪNG PHẦN",
        "status_color": "#F39C12",
        "top_stocks": ["VCB", "BID", "CTG", "TCB", "MBB", "ACB"],
        "is_live_computed": False,
        "summary": "Giá vẫn ở mức cao nhưng xung lực tiền bắt đầu chậm lại do dòng tiền chốt lời luân chuyển sang các nhóm có beta cao hơn (BĐS, Chứng khoán).",
    },
    {
        "sector_id": "banle",
        "name": "Bán Lẻ & Tiêu Dùng",
        "rs_ratio": 100.8,
        "rs_momentum": 97.5,
        "prev_ratio": 101.9,
        "prev_momentum": 100.5,
        "quadrant": "Weakening",
        "net_inflow_bil": -120,
        "liquidity_pct": 7.4,
        "price_change_pct": 0.65,
        "recommendation": "⚠️ QUAN SÁT",
        "status_color": "#F39C12",
        "top_stocks": ["MWG", "PNJ", "MSN", "VNM"],
        "is_live_computed": False,
        "summary": "Đang trong nhịp tích lũy điều chỉnh, sức cầu tiêu dùng nội địa cần thêm thời gian để tăng trưởng bứt phá.",
    },
    {
        "sector_id": "thep",
        "name": "Thép & Vật Liệu",
        "rs_ratio": 96.5,
        "rs_momentum": 99.1,
        "prev_ratio": 97.2,
        "prev_momentum": 98.0,
        "quadrant": "Lagging",
        "net_inflow_bil": -280,
        "liquidity_pct": 9.1,
        "price_change_pct": -0.45,
        "recommendation": "🛑 THEO DÕI VÙNG ĐÁY",
        "status_color": "#E74C3C",
        "top_stocks": ["HPG", "HSG", "NKG"],
        "is_live_computed": False,
        "summary": "Chịu áp lực từ giá thép thế giới và biên lợi nhuận thu hẹp, dòng tiền tạm thời rút ra để chờ đợi điểm cân bằng giá.",
    },
    {
        "sector_id": "daukhi",
        "name": "Dầu Khí",
        "rs_ratio": 95.2,
        "rs_momentum": 96.8,
        "prev_ratio": 96.0,
        "prev_momentum": 97.5,
        "quadrant": "Lagging",
        "net_inflow_bil": -350,
        "liquidity_pct": 5.5,
        "price_change_pct": -0.80,
        "recommendation": "🛑 HẠ TỶ TRỌNG",
        "status_color": "#E74C3C",
        "top_stocks": ["GAS", "PVD", "PVS", "BSR", "PLX"],
        "is_live_computed": False,
        "summary": "Giá dầu Brent điều chỉnh giảm gây áp lực tâm lý ngắn hạn, thanh khoản suy giảm và dòng tiền ngoại bán ròng nhẹ.",
    },
    {
        "sector_id": "hoachat",
        "name": "Hóa Chất & Phân Bón",
        "rs_ratio": 97.1,
        "rs_momentum": 95.5,
        "prev_ratio": 98.5,
        "prev_momentum": 97.0,
        "quadrant": "Lagging",
        "net_inflow_bil": -180,
        "liquidity_pct": 4.8,
        "price_change_pct": -0.30,
        "recommendation": "🛑 QUAN SÁT",
        "status_color": "#E74C3C",
        "top_stocks": ["DGC", "DCM", "DPM", "CSV"],
        "is_live_computed": False,
        "summary": "Hiệu suất yếu hơn thị trường chung, chờ đợi tín hiệu phục hồi giá hàng hóa hóa chất thế giới.",
    },
]


def compute_rrg_from_prices(sector_prices: pd.Series, benchmark_prices: pd.Series, rs_lookback=52, mom_lookback=12) -> Tuple[float, float]:
    """Compute RRG coordinates from price series."""
    if len(sector_prices) < rs_lookback or len(benchmark_prices) < rs_lookback:
        return 100.0, 100.0
        
    rs = sector_prices / benchmark_prices
    rs_sma = rs.rolling(window=rs_lookback).mean()
    rs_ratio = (rs / rs_sma) * 100.0
    
    rs_ratio_sma = rs_ratio.rolling(window=mom_lookback).mean()
    rs_momentum = (rs_ratio / rs_ratio_sma) * 100.0
    
    curr_ratio = float(rs_ratio.iloc[-1])
    curr_mom = float(rs_momentum.iloc[-1])
    
    if pd.isna(curr_ratio) or pd.isna(curr_mom):
        return 100.0, 100.0
        
    return curr_ratio, curr_mom

def classify_rrg_quadrant(rs_ratio: float, rs_momentum: float) -> str:
    """Classify RRG quadrant based on coordinates."""
    if rs_ratio >= 100 and rs_momentum >= 100:
        return "Leading"
    elif rs_ratio < 100 and rs_momentum >= 100:
        return "Improving"
    elif rs_ratio >= 100 and rs_momentum < 100:
        return "Weakening"
    else:
        return "Lagging"


def get_sector_money_flow_dataframe() -> pd.DataFrame:
    """Return structured sector money flow DataFrame."""
    return pd.DataFrame(SECTOR_MONEY_FLOW_DATA)


def render_rrg_chart(data: List[Dict[str, Any]]) -> go.Figure:
    """
    Render professional Relative Rotation Graph (RRG) using Plotly.
    Divided into 4 quadrants: Leading (Green), Improving (Blue), Weakening (Yellow), Lagging (Red).
    """
    fig = go.Figure()

    # 1. Background Quadrant Shapes
    fig.add_shape(type="rect", x0=100, y0=100, x1=112, y1=110, fillcolor="rgba(46, 204, 113, 0.12)", line=dict(width=0))
    fig.add_shape(type="rect", x0=90, y0=100, x1=100, y1=110, fillcolor="rgba(0, 173, 181, 0.12)", line=dict(width=0))
    fig.add_shape(type="rect", x0=100, y0=90, x1=112, y1=100, fillcolor="rgba(243, 156, 18, 0.12)", line=dict(width=0))
    fig.add_shape(type="rect", x0=90, y0=90, x1=100, y1=100, fillcolor="rgba(231, 76, 60, 0.12)", line=dict(width=0))

    # 2. Quadrant Labels
    fig.add_annotation(x=108, y=108.5, text="🚀 DẪN DẮT (LEADING)<br><span style='font-size:10px;color:#2ECC71;'>Tiền vào mạnh & Tăng giá</span>", showarrow=False, font=dict(size=12, color="#2ECC71", family="Arial Black"))
    fig.add_annotation(x=93.5, y=108.5, text="🔄 HỒI PHỤC (IMPROVING)<br><span style='font-size:10px;color:#00FFF5;'>Xung lực tăng - Mua đón đầu</span>", showarrow=False, font=dict(size=12, color="#00ADB5", family="Arial Black"))
    fig.add_annotation(x=108, y=91.5, text="⚠️ SUY YẾU (WEAKENING)<br><span style='font-size:10px;color:#F39C12;'>Xung lực giảm - Canh chốt</span>", showarrow=False, font=dict(size=12, color="#F39C12", family="Arial Black"))
    fig.add_annotation(x=93.5, y=91.5, text="🛑 TỤT HẬU (LAGGING)<br><span style='font-size:10px;color:#E74C3C;'>Tiền rút ra - Tránh xa</span>", showarrow=False, font=dict(size=12, color="#E74C3C", family="Arial Black"))

    # 3. Add Sector Trajectory Arrows and Scatter Points
    for item in data:
        name = item["name"]
        curr_x, curr_y = item["rs_ratio"], item["rs_momentum"]
        prev_x, prev_y = item["prev_ratio"], item["prev_momentum"]
        inflow = item["net_inflow_bil"]
        stocks_str = ", ".join(item["top_stocks"][:4])
        color = item["status_color"]

        # Trajectory vector arrow
        fig.add_annotation(
            x=curr_x,
            y=curr_y,
            ax=prev_x,
            ay=prev_y,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.2,
            arrowwidth=2,
            arrowcolor=color,
            opacity=0.8,
        )

        # Current Node Bubble
        hover_text = (
            f"<b>🏢 Ngành: {name}</b><br>"
            f"• Trạng thái: {item['recommendation']}<br>"
            f"• RS-Ratio: {curr_x:.1f} | RS-Momentum: {curr_y:.1f}<br>"
            f"• Dòng tiền ròng: {inflow:+,d} Tỷ VNĐ<br>"
            f"• Tỷ trọng thanh khoản: {item['liquidity_pct']}%<br>"
            f"• CP tiêu biểu: {stocks_str}"
        )

        fig.add_trace(
            go.Scatter(
                x=[curr_x],
                y=[curr_y],
                mode="markers+text",
                name=name,
                text=[f"<b>{name}</b>"],
                textposition="top center",
                textfont=dict(size=11, color="#FFFFFF"),
                marker=dict(
                    size=16 + (item["liquidity_pct"] * 0.5),
                    color=color,
                    line=dict(width=2, color="#FFFFFF"),
                    opacity=0.95,
                ),
                hoverinfo="text",
                hovertext=hover_text,
                showlegend=False,
            )
        )

    # Center Baseline Axes (100, 100)
    fig.add_hline(y=100, line=dict(color="#4A5568", width=1.5, dash="dash"))
    fig.add_vline(x=100, line=dict(color="#4A5568", width=1.5, dash="dash"))

    fig.update_layout(
        title=dict(
            text="🧭 MA TRẬN LUÂN CHUYỂN DÒNG TIỀN THEO NGÀNH - RRG (RELATIVE ROTATION GRAPH)",
            font=dict(size=14, color="#00FFF5"),
        ),
        xaxis=dict(
            title="Sức Mạnh Tương Đối (RS-Ratio vs VN-Index Benchmark)",
            range=[91, 110],
            showgrid=True,
            gridcolor="#232936",
            zeroline=False,
            color="#B0BEC5",
        ),
        yaxis=dict(
            title="Xung Lực Dòng Tiền (RS-Momentum Rate of Change)",
            range=[91, 110],
            showgrid=True,
            gridcolor="#232936",
            zeroline=False,
            color="#B0BEC5",
        ),
        paper_bgcolor="#161B26",
        plot_bgcolor="#0F131C",
        height=520,
        margin=dict(t=0, l=0, r=0, b=0),
    )

    return fig


def compute_live_sector_money_flow():
    return SECTOR_MONEY_FLOW_DATA


def render_net_inflow_chart(data: List[Dict[str, Any]]) -> go.Figure:
    """Render horizontal bar chart for net capital inflow/outflow per sector."""
    df = pd.DataFrame(data).sort_values(by="net_inflow_bil", ascending=True)

    colors = ["#2ECC71" if val > 0 else "#E74C3C" for val in df["net_inflow_bil"]]

    fig = go.Figure(
        go.Bar(
            x=df["net_inflow_bil"],
            y=df["name"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=1, color="#2B313E")),
            text=[f"{val:+,d} Tỷ" for val in df["net_inflow_bil"]],
            textposition="auto",
            textfont=dict(color="#FFFFFF", size=11, family="Arial Black"),
        )
    )

    fig.update_layout(
        title=dict(
            text="🌊 GIÁ TRỊ DÒNG TIỀN RÒNG THEO NHÓM NGÀNH (NET CAPITAL INFLOW/OUTFLOW)",
            font=dict(size=13, color="#00FFF5"),
        ),
        xaxis=dict(
            title="Giá Trị Tiền Ròng (Tỷ VNĐ)",
            showgrid=True,
            gridcolor="#232936",
            color="#B0BEC5",
        ),
        yaxis=dict(
            showgrid=False,
            color="#ECEFF1",
        ),
        paper_bgcolor="#161B26",
        plot_bgcolor="#0F131C",
        height=420,
        margin=dict(l=20, r=20, t=50, b=30),
    )

    return fig


def render_sector_treemap(data: List[Dict[str, Any]]) -> go.Figure:
    """Render Sector Liquidity & Performance Heatmap (Treemap)."""
    df = pd.DataFrame(data)

    fig = px.treemap(
        df,
        path=["name"],
        values="liquidity_pct",
        color="net_inflow_bil",
        color_continuous_scale=[
            [0.0, "#E74C3C"],
            [0.35, "#C0392B"],
            [0.5, "#2C3E50"],
            [0.65, "#27AE60"],
            [1.0, "#2ECC71"],
        ],
        hover_data=["recommendation", "top_stocks"],
    )

    fig.update_layout(
        title=dict(
            text="🗺️ BẢN ĐỒ NHIỆT THANH KHOẢN & DÒNG TIỀN NGÀNH (TREEMAP)",
            font=dict(size=13, color="#00FFF5"),
        ),
        paper_bgcolor="#161B26",
        height=420,
        margin=dict(l=10, r=10, t=50, b=10),
    )

    return fig

def compute_live_sector_money_flow(stock_registry: Optional[Dict[str, Dict]] = None, live_quotes: Optional[Dict[str, Tuple]] = None) -> List[Dict[str, Any]]:
    import copy
    sectors_base = copy.deepcopy(SECTOR_MONEY_FLOW_DATA)
    
    if live_quotes is None:
        try:
            from services.stock_service import fetch_batch_live_quotes
            all_syms = set()
            for sec in sectors_base:
                for s in sec.get("top_stocks", []):
                    all_syms.add(s)
            live_quotes = fetch_batch_live_quotes(list(all_syms))
        except Exception:
            live_quotes = {}
            
    if not live_quotes:
        return sectors_base
        
    market_chg_sum = 0.0
    market_chg_count = 0
    for sym, (p, c, n) in live_quotes.items():
        if c is not None:
            market_chg_sum += c
            market_chg_count += 1
            
    market_avg_chg = market_chg_sum / market_chg_count if market_chg_count > 0 else 0.0
    
    for sector in sectors_base:
        top_stocks = sector.get("top_stocks", [])
        if not top_stocks:
            continue
            
        total_price_change = 0.0
        valid_count = 0
        
        for sym in top_stocks:
            if sym in live_quotes:
                p, chg, n = live_quotes[sym]
                if chg is not None:
                    total_price_change += chg
                    valid_count += 1
                    
        if valid_count > 0:
            avg_chg = total_price_change / valid_count
            sector["price_change_pct"] = round(avg_chg, 2)
            
            relative_perf = avg_chg - market_avg_chg
            sector["rs_ratio"] = round(sector["prev_ratio"] + relative_perf * 1.5, 1)
            sector["rs_momentum"] = round(sector["prev_momentum"] + relative_perf * 2.0, 1)
            
            sector["net_inflow_bil"] = int(sector["net_inflow_bil"] + avg_chg * 100)
            sector["liquidity_pct"] = round(sector["liquidity_pct"] * (1.0 + abs(avg_chg)/10.0), 1)
            
            sector["quadrant"] = classify_rrg_quadrant(sector["rs_ratio"], sector["rs_momentum"])
            
            if sector["quadrant"] == "Leading":
                sector["status_color"] = "#2ECC71"
                sector["recommendation"] = "🚀 NẮM GIỮ / MUA GIA TĂNG"
            elif sector["quadrant"] == "Improving":
                sector["status_color"] = "#00ADB5"
                sector["recommendation"] = "🔄 MUA ĐÓN ĐẦU"
            elif sector["quadrant"] == "Weakening":
                sector["status_color"] = "#F39C12"
                sector["recommendation"] = "⚠️ QUAN SÁT / CHỐT LỜI TỪNG PHẦN"
            else:
                sector["status_color"] = "#E74C3C"
                sector["recommendation"] = "🛑 THEO DÕI VÙNG ĐÁY"
                
            sector["is_live_computed"] = True
            
    return sectors_base
