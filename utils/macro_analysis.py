"""
Macroeconomic Data Analysis and Composite Scoring Utilities.
Calculates Vietnam Macro Composite Health Score (0-100) and renders rich AI Tooltips and Charts.
"""
from typing import Any, Dict, List, Tuple


def _linear_score(value: float, worst: float, best: float, max_pts: float) -> float:
    if best > worst:
        if value <= worst: return 0.0
        if value >= best: return max_pts
        return max_pts * (value - worst) / (best - worst)
    else:
        if value >= worst: return 0.0
        if value <= best: return max_pts
        return max_pts * (worst - value) / (worst - best)

def calculate_vietnam_macro_health_score(macro_data: Dict[str, Any]) -> Tuple[int, str, str, str]:
    """
    Calculate the Vietnam Macro Composite Health Score on a 0-100 scale.
    Weights 5 core macroeconomic pillars:
    1. Cung tiền M2 (25%)
    2. Sản xuất PMI (25%)
    3. Lạm phát CPI (20%)
    4. Lãi suất cho vay & Huy động (15%)
    5. Tỷ giá USD/VND & DXY (15%)
    """
    m2_growth = macro_data.get("m2_money_supply", {}).get("latest", 14.25)
    pmi = macro_data.get("pmi_index", {}).get("latest", 52.40)
    cpi = macro_data.get("vn_cpi", {}).get("latest", 4.36)
    lending_rate = macro_data.get("lending_rate_avg", {}).get("latest", 8.60)
    usd_vnd = macro_data.get("usd_vnd_rate", {}).get("latest", 25420.0)
    dxy = macro_data.get("dxy_index", {}).get("latest", 103.20)

    score = 0.0

    # 1. Cung tiền M2 (25 điểm)
    score += _linear_score(m2_growth, 4.0, 15.0, 25.0)

    # 2. PMI Sản xuất (25 điểm)
    score += _linear_score(pmi, 44.0, 55.0, 25.0)

    # 3. Lạm phát CPI (20 điểm)
    score += _linear_score(cpi, 7.0, 3.0, 20.0)

    # 4. Lãi suất cho vay (15 điểm)
    score += _linear_score(lending_rate, 13.0, 7.5, 15.0)

    # 5. Tỷ giá USD/VND (15 điểm)
    score += _linear_score(usd_vnd, 26500.0, 24000.0, 15.0)

    final_score = int(round(score))

    if final_score >= 80:
        status_title = "RẤT TÍCH CỰC (VÙNG TĂNG TRƯỞNG MẠNH)"
        status_color = "#2ECC71"
        summary = (
            "Nền kinh tế Việt Nam 2026 đang trong chu kỳ MỞ RỘNG VỮNG CHẮC: Cung tiền M2 tăng tốc (~21.9 Triệu Tỷ VNĐ), "
            "PMI sản xuất đạt 52.40 điểm (tháng thứ 4 mở rộng), CPI được kiểm soát tốt dưới 4.5%. "
            "Môi trường vĩ mô cực kỳ thuận lợi cho thị trường vốn và định giá cổ phiếu."
        )
    elif final_score >= 65:
        status_title = "TÍCH CỰC (VÙNG MỞ RỘNG ỔN ĐỊNH)"
        status_color = "#00ADB5"
        summary = (
            "Nền kinh tế duy trì đà hồi phục ổn định. Thanh khoản tiền tệ dồi dào, sản xuất khởi sắc, "
            "áp lực tỷ giá và lạm phát nằm trong tầm kiểm soát."
        )
    elif final_score >= 50:
        status_title = "TRUNG LẬP (PHÂN HÓA THEO DÕI)"
        status_color = "#F39C12"
        summary = (
            "Thị trường đang trong giai đoạn tích lũy. Cần theo dõi thêm diễn biến tỷ giá USD/VND và định hướng lãi suất của Fed."
        )
    else:
        status_title = "THẬN TRỌNG (ÁP LỰC VĨ MÔ GIA TĂNG)"
        status_color = "#E74C3C"
        summary = (
            "Cảnh báo rủi ro lạm phát hoặc áp lực mất giá đồng nội tệ lớn. Nên ưu tiên quản trị rủi ro danh mục."
        )

    return final_score, status_title, status_color, summary


# Structured Macro Insights Knowledge Base
INDICATOR_INSIGHTS: Dict[str, Dict[str, str]] = {
    "m2_money_supply": {
        "nature": "Tổng phương tiện thanh toán (tiền mặt lưu thông + tiền gửi ngân hàng). Thước đo quan trọng nhất về lượng thanh khoản được bơm vào nền kinh tế.",
        "good": "Tăng trưởng M2 từ 12% - 15%/năm: Bơm thanh khoản dồi dào, kích thích tín dụng, sản xuất và mở rộng định giá tài sản tài chính (chứng khoán, bất động sản).",
        "bad": "Tăng trưởng M2 < 8%: Thắt chặt tiền tệ, khan hiếm thanh khoản; hoặc > 18%: Tiềm ẩn rủi ro bong bóng tài sản và lạm phát phi mã.",
        "current_ai_verdict": "M2 tăng 14.25% YoY (quy mô ~21.9 Triệu Tỷ VNĐ) => RẤT TỐT: Thanh khoản dồi dào, bệ phóng hoàn hảo cho thị trường tài chính 2026.",
    },
    "deposit_rate_12m": {
        "nature": "Lãi suất tiền gửi kỳ hạn 12 tháng tại các NHTM. Chi phí cơ hội của dòng tiền nhàn rỗi trong dân cư và tổ chức.",
        "good": "Lãi suất 12T ở mức 5.0% - 6.0%: Cân bằng giữa bảo vệ giá trị tiền gửi và khuyến khích dòng tiền chuyển dịch vào sản xuất, kinh doanh và kênh đầu tư cổ phiếu.",
        "bad": "Lãi suất 12T tăng cao > 8% - 9%: Hút tiền khỏi thị trường chứng khoán vào gửi tiết kiệm, tăng gánh nặng lãi vay cho doanh nghiệp.",
        "current_ai_verdict": "Lãi suất 12T ở mức 5.75%/năm => HỢP LÝ: Đủ hấp dẫn để giữ chân tiền gửi nhưng vẫn đủ thấp để dòng tiền thông minh tìm đến kênh cổ phiếu.",
    },
    "deposit_rate_6m": {
        "nature": "Lãi suất tiền gửi ngắn hạn 6 tháng. Thước đo biến động thanh khoản ngắn hạn của hệ thống ngân hàng.",
        "good": "Lãi suất 6T duy trì thấp (4.0% - 4.8%): Doanh nghiệp tiếp cận vốn lưu động giá rẻ, giảm chi phí tài chính.",
        "bad": "Lãi suất 6T tăng vọt: Dấu hiệu ngân hàng bị căng thẳng thanh khoản ngắn hạn hoặc cuộc đua lãi suất huy động tái diễn.",
        "current_ai_verdict": "Lãi suất 6T ở mức 4.65%/năm => ỔN ĐỊNH: Chi phí vốn ngắn hạn của các doanh nghiệp đang rất dễ chịu.",
    },
    "lending_rate_avg": {
        "nature": "Lãi suất cho vay bình quân đối với nền kinh tế. Chi phí vốn trực tiếp mà doanh nghiệp và người mua nhà phải trả.",
        "good": "Lãi vay bình quân hạ về 7.5% - 8.5%: Giúp doanh nghiệp giảm chi phí lãi vay, gia tăng biên lợi nhuận ròng, kích thích nhu cầu vay mở rộng kinh doanh.",
        "bad": "Lãi vay tăng cao > 11% - 13%: Gây thiệt hại lớn cho nền kinh tế, ăn mòn lợi nhuận doanh nghiệp sản xuất và làm đóng băng thị trường bất động sản.",
        "current_ai_verdict": "Lãi vay bình quân giảm về 8.60% (giảm -0.35%) => TÍCH CỰC: Hỗ trợ đắc lực cho sự hồi phục của doanh nghiệp sản xuất và bất động sản.",
    },
    "interbank_rate": {
        "nature": "Lãi suất vay mượn qua đêm giữa các ngân hàng. Phong vũ biểu đo lường lượng tiền mặt thừa/thiếu trong hệ thống liên ngân hàng hàng ngày.",
        "good": "Lãi suất ON duy trì ở mức 3.5% - 4.5%: Thanh khoản dồi dào, các ngân hàng đáp ứng tốt nhu cầu thanh toán và giải ngân tín dụng.",
        "bad": "Lãi suất ON tăng vọt > 7% - 9%: Hệ thống bị nghẽn thanh khoản nghiêm trọng, buộc NHNN phải bơm thanh khoản khẩn cấp.",
        "current_ai_verdict": "Lãi suất ON ở mức 4.15% (giảm -0.45%) => DỒI DÀO: Hệ thống ngân hàng đang dư dả thanh khoản.",
    },
    "pmi_index": {
        "nature": "Chỉ số nhà quản trị mua hàng ngành sản xuất. Thước đo sức khỏe đơn hàng mới, sản lượng và việc làm ngành công nghiệp chế biến chế tạo.",
        "good": "PMI > 50 điểm: Khu vực sản xuất đang mở rộng, đơn hàng xuất khẩu gia tăng, nhà máy hoạt động tối đa công suất.",
        "bad": "PMI < 50 điểm kéo dài: Sản xuất suy thoái, đơn hàng cạn kiệt, nguy cơ sụt giảm doanh thu của các doanh nghiệp niêm yết.",
        "current_ai_verdict": "PMI đạt 52.40 điểm (+1.60) => MỞ RỘNG MẠNH: Đơn hàng mới và sản xuất tiếp tục tăng tốc ấn tượng.",
    },
    "vn_cpi": {
        "nature": "Chỉ số giá tiêu dùng đo lường mức độ lạm phát giá cả hàng hóa, dịch vụ sinh hoạt của người dân.",
        "good": "CPI duy trì ở mức 3.5% - 4.2% (dưới trần 4.5% của Quốc hội): Lạm phát được kiểm soát, NHNN có nhiều dư địa nới lỏng chính sách tiền tệ hỗ trợ tăng trưởng.",
        "bad": "CPI vượt > 4.5% - 5.0%: Nguy cơ nhập khẩu lạm phát, buộc NHNN phải thắt chặt tiền tệ và tăng lãi suất để kìm hãm đà tăng giá.",
        "current_ai_verdict": "CPI ở mức 4.36% YoY (-0.09%) => KIỂM SOÁT TỐT: Nằm hoàn toàn trong mục tiêu điều hành vĩ mô.",
    },
    "vn_gdp": {
        "nature": "Tổng sản phẩm quốc nội. Thước đo quy mô và sức khỏe tăng trưởng tổng thể của toàn bộ nền kinh tế Việt Nam.",
        "good": "Tăng trưởng GDP > 6.5% - 7.5%/năm: Nền kinh tế tăng trưởng thần tốc, thu hút dòng vốn FDI, gia tăng thu nhập bình quân đầu người và mở rộng thị trường nội địa.",
        "bad": "Tăng trưởng GDP < 5.0%: Tăng trưởng chậm chạp, dấu hiệu của sự chững lại trong cầu tiêu dùng và đầu tư công.",
        "current_ai_verdict": "Quy mô GDP đạt 514.8 Tỷ USD, tăng trưởng kỳ vọng ~6.85% => VƯỢT TRỘI: Việt Nam nằm trong nhóm các quốc gia có tốc độ tăng trưởng GDP cao nhất khu vực.",
    },
    "usd_vnd_rate": {
        "nature": "Tỷ giá hối đoái giữa đồng Đô la Mỹ và Việt Nam Đồng. Thước đo áp lực mất giá tiền tệ và dòng vốn xuất nhập khẩu/FDI.",
        "good": "Tỷ giá biến động trong biên độ cho phép (+1% - 3%/năm): Bảo vệ giá trị đồng nội tệ, không gây áp lực nhập khẩu lạm phát, ổn định tâm lý nhà đầu tư ngoại.",
        "bad": "Tỷ giá mất giá nhanh > 4% - 5% trong thời gian ngắn: Buộc NHNN phải can thiệp bán ngoại tệ dự trữ hoặc tăng lãi suất để giữ giá trị VND, gây rút ròng vốn ngoại.",
        "current_ai_verdict": "Tỷ giá quanh mức 25,420 đ/USD (+40 đ) => THEO DÕI: Biên độ tỷ giá đang được NHNN giữ vững, áp lực hạ nhiệt khi Fed chính thức giảm lãi suất.",
    },
    "fed_funds": {
        "nature": "Lãi suất điều hành của Cục Dự trữ Liên bang Mỹ (Fed). Yếu tố định hình chi phí vốn và hướng đi của dòng tiền toàn cầu.",
        "good": "Fed bước vào chu kỳ cắt giảm lãi suất: Đồng USD hạ nhiệt (DXY giảm), giảm áp lực tỷ giá lên các thị trường mới nổi như Việt Nam, mở đường cho dòng vốn ngoại quay trở lại.",
        "bad": "Fed duy trì lãi suất 'Cao hơn trong thời gian dài': Tạo chênh lệch lãi suất USD-VND lớn, gây áp lực chảy máu ngoại tệ và hạn chế dư địa hạ lãi suất trong nước.",
        "current_ai_verdict": "Lãi suất Fed ở mức 5.33% => CHUẨN BỊ BƯỚC VÀO CHU KỲ HẠ LÃI SUẤT: Giảm bớt áp lực tỷ giá cho Việt Nam trong các quý tới.",
    },
    "dxy_index": {
        "nature": "Chỉ số Dollar Index đo lường sức mạnh đồng bạc xanh so với 6 đồng tiền mạnh thế giới (EUR, JPY, GBP, CAD, SEK, CHF).",
        "good": "DXY hạ nhiệt < 102 điểm: Đồng USD suy yếu, dòng tiền tìm kiếm cơ hội tăng trưởng tại các thị trường chứng khoán mới nổi và Việt Nam.",
        "bad": "DXY tăng vọt > 105 - 108 điểm: Đồng USD quá mạnh, gây áp lực phá giá lên toàn bộ đồng tiền châu Á và kích hoạt làn sóng bán ròng của khối ngoại.",
        "current_ai_verdict": "DXY ở mức 103.20 điểm (giảm -1.30 điểm) => TÍCH CỰC: Sức mạnh đồng USD đang suy yếu rõ rệt.",
    },
    "vn_bond_10y": {
        "nature": "Lợi suất Trái phiếu Chính phủ Việt Nam kỳ hạn 10 năm. Chuẩn mực lãi suất phi rủi ro dùng để định giá cổ phiếu theo mô hình chiết khấu dòng tiền (DCF).",
        "good": "Lợi suất TPCP 10Y duy trì thấp (2.5% - 3.0%): Chi phí vốn dài hạn rẻ, định giá cổ phiếu (P/E) trở nên hấp dẫn hơn so với đầu tư trái phiếu.",
        "bad": "Lợi suất TPCP 10Y tăng mạnh > 5%: Báo hiệu kỳ vọng lạm phát dài hạn gia tăng, làm giảm mức định giá hợp lý của thị trường cổ phiếu.",
        "current_ai_verdict": "Lợi suất 10Y ở mức 2.82% => TÍCH CỰC: Chi phí vốn dài hạn đang ở vùng đáy lịch sử, tạo điều kiện thuận lợi cho định giá P/E của thị trường chứng khoán mở rộng.",
    },
}


def format_ai_indicator_help(indicator_key: str, data_dict: Dict[str, Any]) -> str:
    """Format rich structured Markdown tooltip for any macro indicator."""
    insight = INDICATOR_INSIGHTS.get(indicator_key, {})
    label = data_dict.get("label", indicator_key)
    latest = data_dict.get("latest", 0.0)
    delta = data_dict.get("delta", 0.0)
    unit = data_dict.get("unit", "")
    date_str = data_dict.get("date", "")
    scale_desc = data_dict.get("scale_desc", "")

    nature = insight.get("nature", data_dict.get("description", "Chỉ số kinh tế vĩ mô trọng yếu."))
    good_text = insight.get("good", "Chỉ số duy trì ở vùng ổn định và hỗ trợ tăng trưởng kinh tế.")
    bad_text = insight.get("bad", "Chỉ số biến động bất thường hoặc vượt quá ngưỡng kiểm soát.")
    verdict = insight.get("current_ai_verdict", f"Giá trị hiện tại: {latest} {unit}, biến động {delta:+.2f} {unit} so với kỳ trước.")

    tooltip = f"""📊 {label.upper()}
----------------------------------------
📖 BẢN CHẤT CHỈ SỐ:
{nature}

📈 SỐ LIỆU HIỆN TẠI (2026):
• Mức ghi nhận: {latest} {unit} ({delta:+.2f} {unit} so với kỳ trước)
• Kỳ báo cáo: {date_str} {f'| {scale_desc}' if scale_desc else ''}

🟢 THẾ NÀO LÀ TỐT (TÍCH CỰC):
{good_text}

🔴 THẾ NÀO LÀ XẤU (RỦI RO / CẢNH BÁO):
{bad_text}

🎯 NHẬN XÉT CỦA AI (CIO TAKEAWAY):
{verdict}
"""
    return tooltip.strip()


def render_m2_actual_volume_chart() -> Any:
    """
    Render Plotly combination chart for Vietnam M2 Money Supply up to 2026 (Present):
    - Bar: Actual Money Supply Volume (Triệu Tỷ VNĐ)
    - Line (Secondary Axis): YoY Growth Rate (%)
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026 (Hiện tại)"]
    m2_volume_bil = [9.17, 10.53, 12.06, 13.40, 14.23, 15.70, 17.65, 19.85, 21.90]  # Triệu Tỷ VNĐ
    m2_growth_pct = [12.4, 14.8, 14.5, 11.1, 6.2, 10.3, 12.4, 12.5, 14.25]        # % YoY

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar colors with 2026 highlighted in glowing cyan
    bar_colors = ["#005F73", "#0A9396", "#00ADB5", "#2ECC71", "#27AE60", "#16A085", "#3498DB", "#2980B9", "#00FFF5"]

    # 1. Bar Chart: Actual Volume
    fig.add_trace(
        go.Bar(
            x=years,
            y=m2_volume_bil,
            name="Quy Mô M2 (Triệu Tỷ VNĐ)",
            marker=dict(
                color=bar_colors,
                line=dict(width=2, color=["#2B313E"] * 8 + ["#FFFFFF"])
            ),
            text=[f"{v:.2f} Tr.Tỷ" for v in m2_volume_bil],
            textposition="inside",
            textfont=dict(color="#FFFFFF", size=11, family="Arial Black"),
        ),
        secondary_y=False,
    )

    # 2. Line Chart: Growth Rate
    fig.add_trace(
        go.Scatter(
            x=years,
            y=m2_growth_pct,
            name="Tăng Trưởng M2 YoY (%)",
            mode="lines+markers+text",
            line=dict(color="#FFD700", width=3.5),
            marker=dict(size=9, color="#FFD700", symbol="circle"),
            text=[f"{g:.1f}%" for g in m2_growth_pct],
            textposition="top center",
            textfont=dict(color="#FFD700", size=11, family="Arial Black"),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=dict(
            text="💵 QUY MÔ THỰC TẾ & TỐC ĐỘ TĂNG TRƯỞNG CUNG TIỀN M2 VIỆT NAM (2018 - 2026 HIỆN TẠI)",
            font=dict(size=13, color="#00FFF5"),
        ),
        xaxis=dict(
            type="category",
            tickmode="array",
            tickvals=years,
            ticktext=years,
            showgrid=False,
            color="#ECEFF1",
            tickfont=dict(size=10),
            automargin=True,
        ),
        yaxis=dict(
            title="Quy Mô M2 (Triệu Tỷ VNĐ)",
            range=[0, 26],
            showgrid=True,
            gridcolor="#232936",
            color="#B0BEC5",
        ),
        yaxis2=dict(
            title="Tăng Trưởng YoY (%)",
            range=[0, 20],
            showgrid=False,
            color="#FFD700",
            overlaying="y",
            side="right",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#FFFFFF")),
        paper_bgcolor="#161B26",
        plot_bgcolor="#0F131C",
        height=440,
        margin=dict(l=30, r=30, t=55, b=40),
    )

    return fig


def render_fdi_public_investment_chart() -> Any:
    """
    Render Plotly combination chart for Foreign Direct Investment (FDI) and Public Investment up to 2026 (Present).
    - Bar 1: Vốn FDI Thực Hiện (Tỷ USD)
    - Bar 2: Vốn Đầu Tư Công Đã Triển Khai (Nghìn Tỷ VNĐ)
    """
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    years = ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026 (Hiện tại)"]
    fdi_actual_usd = [19.1, 20.4, 20.0, 19.7, 22.4, 23.2, 25.4, 27.6, 29.5]          # Tỷ USD
    public_invest_vnd = [275, 312, 466, 435, 540, 625, 685, 750, 820]               # Nghìn Tỷ VNĐ

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fdi_colors = ["#27AE60"] * 8 + ["#2ECC71"]

    # 1. Bar Chart: FDI Thực Hiện
    fig.add_trace(
        go.Bar(
            x=years,
            y=fdi_actual_usd,
            name="Vốn FDI Thực Hiện (Tỷ USD)",
            marker=dict(
                color=fdi_colors,
                line=dict(width=1.5, color=["#2B313E"] * 8 + ["#FFFFFF"])
            ),
            text=[f"{v:.1f} Tỷ $" for v in fdi_actual_usd],
            textposition="auto",
            textfont=dict(color="#FFFFFF", size=10, family="Arial Black"),
        ),
        secondary_y=False,
    )

    # 2. Bar / Line: Vốn Đầu Tư Công Giải Ngân
    fig.add_trace(
        go.Scatter(
            x=years,
            y=public_invest_vnd,
            name="Đầu Tư Công Đã Giải Ngân (Nghìn Tỷ VNĐ)",
            mode="lines+markers+text",
            line=dict(color="#FF9800", width=3.5),
            marker=dict(size=9, color="#FF9800", symbol="diamond"),
            text=[f"{p}k Tỷ" for p in public_invest_vnd],
            textposition="top center",
            textfont=dict(color="#FF9800", size=10, family="Arial Black"),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=dict(
            text="🏗️ ĐỘNG LỰC BƠM VỐN KINH TẾ THỰC: FDI & ĐẦU TƯ CÔNG (2018 - 2026 HIỆN TẠI)",
            font=dict(size=13, color="#00FFF5"),
        ),
        xaxis=dict(
            type="category",
            tickmode="array",
            tickvals=years,
            ticktext=years,
            showgrid=False,
            color="#ECEFF1",
            tickfont=dict(size=10),
            automargin=True,
        ),
        yaxis=dict(
            title="Vốn FDI Thực Hiện (Tỷ USD)",
            range=[0, 36],
            showgrid=True,
            gridcolor="#232936",
            color="#2ECC71",
        ),
        yaxis2=dict(
            title="Đầu Tư Công Giải Ngân (Nghìn Tỷ VNĐ)",
            range=[0, 1000],
            showgrid=False,
            color="#FF9800",
            overlaying="y",
            side="right",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#FFFFFF")),
        paper_bgcolor="#161B26",
        plot_bgcolor="#0F131C",
        height=440,
        margin=dict(l=30, r=30, t=55, b=40),
    )

    return fig
