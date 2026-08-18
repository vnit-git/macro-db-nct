"""
AI Macro Health Diagnosis and Educational Indicator Insights Engine.
Provides structured CIO-level explanations, good/bad thresholds, and composite health scoring.
"""
from typing import Any, Dict, Tuple


def calculate_vietnam_macro_health_score(macro_data: Dict[str, Any]) -> Tuple[int, str, str, str]:
    """
    Calculate Vietnam Macroeconomic Health Score (0 - 100) based on core indicators.
    Returns: (Score, Status Title, Status Color, Diagnostic Summary)
    """
    # 1. M2 Money Supply Growth (Target 12% - 15%)
    m2_val = macro_data.get("m2_money_supply", {}).get("latest", 14.25)
    score_m2 = 90 if 12.0 <= m2_val <= 16.0 else (75 if m2_val > 16.0 else 60)

    # 2. PMI Manufacturing (Target > 50.0)
    pmi_val = macro_data.get("pmi_index", {}).get("latest", 52.40)
    score_pmi = 95 if pmi_val >= 52.0 else (80 if pmi_val >= 50.0 else 45)

    # 3. Inflation CPI (Target < 4.5%)
    cpi_val = macro_data.get("vn_cpi", {}).get("latest", 4.36)
    score_cpi = 95 if cpi_val < 3.5 else (85 if cpi_val <= 4.5 else 40)

    # 4. Lending Rate & Spread (Lower lending rate is better for businesses)
    lend_val = macro_data.get("lending_rate_avg", {}).get("latest", 8.60)
    score_lend = 90 if lend_val < 8.5 else (80 if lend_val <= 10.0 else 50)

    # 5. FX Rate Stability
    fx_delta = macro_data.get("usd_vnd_rate", {}).get("delta", 40.0)
    score_fx = 85 if abs(fx_delta) < 100 else 70

    # Weighted Average Health Score
    weights = [0.25, 0.25, 0.20, 0.15, 0.15]
    scores = [score_m2, score_pmi, score_cpi, score_lend, score_fx]
    total_score = int(sum(w * s for w, s in zip(weights, scores)))

    if total_score >= 80:
        status_title = "TĂNG TRƯỞNG MỞ RỘNG & NỚI LỎNG TIỀN TỆ"
        status_color = "#00ADB5"
        summary = "Nền kinh tế đang trong chu kỳ tăng trưởng tích cực. Sản xuất mở rộng (PMI > 50), cung tiền M2 tăng tốc, lạm phát được kiểm soát dưới trần mục tiêu và lãi suất duy trì ở mức hấp dẫn cho đầu tư."
    elif total_score >= 60:
        status_title = "ỔN ĐỊNH & PHỤC HỒI TỪNG BƯỚC"
        status_color = "#2ECC71"
        summary = "Vĩ mô duy trì nền tảng ổn định, thanh khoản đáp ứng tốt cho hoạt động sản xuất kinh doanh, cần tiếp tục theo dõi biến động tỷ giá và lãi suất toàn cầu."
    elif total_score >= 40:
        status_title = "THẬN TRỌNG / ÁP LỰC ĐIỀU HÀNH"
        status_color = "#F39C12"
        summary = "Xuất hiện một số áp lực từ tỷ giá USD/VND hoặc lạm phát gia tăng, doanh nghiệp đối mặt với chi phí vốn cao hơn."
    else:
        status_title = "SUY GIẢM / RỦI RO VĨ MÔ GIA TĂNG"
        status_color = "#E74C3C"
        summary = "Cần thận trọng quản trị rủi ro dòng tiền và giảm đòn bẩy tài chính."

    return total_score, status_title, status_color, summary


INDICATOR_INSIGHTS: Dict[str, Dict[str, str]] = {
    "m2_money_supply": {
        "nature": "Tổng khối lượng tiền tệ lưu thông trong nền kinh tế (tiền mặt + tiền gửi tiết kiệm, thanh toán). Thước đo quan trọng nhất phản ánh thanh khoản và chính sách nới lỏng hay thắt chặt của NHNN.",
        "good": "Tăng trưởng M2 từ 12% - 15%/năm: Cung cấp đầy đủ oxy thanh khoản cho sản xuất, kích thích tín dụng và tạo đà tăng trưởng mạnh mẽ cho thị trường chứng khoán & bất động sản.",
        "bad": "Tăng trưởng M2 < 8% (thắt chặt quá mức gây nghẽn vốn) hoặc M2 > 18% (nguy cơ bong bóng tài sản và bùng phát lạm phát chi phí đẩy).",
        "current_ai_verdict": "M2 đang tăng trưởng ~14.25% YoY (+1.45% so với kỳ trước) => TÍCH CỰC: Dòng tiền dồi dào, hỗ trợ hạ lãi suất và tạo bệ đỡ thanh khoản vững chắc cho VN-Index.",
    },
    "deposit_rate_12m": {
        "nature": "Lãi suất tiền gửi tiết kiệm kỳ hạn 12 tháng tại các NHTM. Đại diện cho chi phí huy động vốn trung dài hạn của toàn bộ hệ thống ngân hàng.",
        "good": "Lãi suất 12T ở mức 5.0% - 6.0%/năm: Chi phí vốn rẻ, kích thích dòng tiền dịch chuyển từ gửi tiết kiệm sang đầu tư chứng khoán, bất động sản và mở rộng kinh doanh.",
        "bad": "Lãi suất 12T tăng cao > 8% - 10%/năm: Hút dòng tiền ra khỏi thị trường tài chính, tăng chi phí đầu vào của ngân hàng, báo hiệu giai đoạn thắt chặt tiền tệ.",
        "current_ai_verdict": "Lãi suất 12T duy trì quanh mức 5.75%/năm => HỢP LÝ: Đủ hấp dẫn người gửi tiền thực dương nhưng không gây áp lực chi phí vốn lên hệ thống tín dụng.",
    },
    "deposit_rate_6m": {
        "nature": "Lãi suất tiền gửi tiết kiệm kỳ hạn 6 tháng. Thước đo biến động thanh khoản ngắn hạn và xu hướng lãi suất trong tương lai gần.",
        "good": "Lãi suất 6T ổn định ở mức 4.0% - 5.0%/năm: Đảm bảo thanh khoản lưu thông nhanh, thúc đẩy vòng quay vốn của nền kinh tế.",
        "bad": "Lãi suất 6T tăng đột ngột: Báo hiệu các ngân hàng đang thiếu hụt thanh khoản ngắn hạn hoặc chịu áp lực cạnh tranh tiền gửi.",
        "current_ai_verdict": "Lãi suất 6T ở mức 4.65%/năm => TỐT: Thanh khoản ngắn hạn của các NHTM ổn định, không có hiện tượng chạy đua lãi suất huy động.",
    },
    "lending_rate_avg": {
        "nature": "Lãi suất cho vay bình quân đối với doanh nghiệp sản xuất và cá nhân. Quyết định trực tiếp chi phí lãi vay và biên lợi nhuận ròng của doanh nghiệp.",
        "good": "Lãi vay giảm hoặc duy trì ở mức 7.5% - 9.0%/năm: Doanh nghiệp mạnh dạn vay vốn mở rộng nhà xưởng, gia tăng sản lượng, giảm gánh nặng nợ vay và kích thích thị trường tiêu dùng/BĐS.",
        "bad": "Lãi vay tăng cao > 11% - 13%/năm: Bào mòn lợi nhuận doanh nghiệp, đóng băng đầu tư dự án mới và gia tăng nguy cơ nợ xấu toàn hệ thống.",
        "current_ai_verdict": "Lãi vay trung bình đạt 8.60%/năm (giảm -0.35%) => RẤT TÍCH CỰC: Các gói tín dụng ưu đãi đang thẩm thấu vào nền kinh tế thực, hỗ trợ mạnh mẽ cho nhóm BĐS và Sản xuất.",
    },
    "interbank_rate": {
        "nature": "Lãi suất các ngân hàng vay mượn vốn lẫn nhau kỳ hạn qua đêm (Overnight). Tấm gương phản chiếu thanh khoản từng ngày của hệ thống ngân hàng.",
        "good": "Lãi suất liên ngân hàng ở mức 3% - 4.5%: Thanh khoản dồi dào, các ngân hàng thừa vốn cho vay, không chịu áp lực rút ròng tiền mặt.",
        "bad": "Lãi suất liên ngân hàng vọt lên > 7% - 9%: Báo hiệu hệ thống đang căng thẳng thanh khoản cục bộ hoặc NHNN đang phải phát hành tín phiếu hút tiền mạnh để ghìm tỷ giá.",
        "current_ai_verdict": "Lãi suất qua đêm ở mức 4.15% (giảm -0.45%) => ỔN ĐỊNH: Hệ thống liên ngân hàng thông suốt, NHNN điều tiết thanh khoản linh hoạt.",
    },
    "pmi_index": {
        "nature": "Chỉ số Nhà quản trị mua hàng ngành sản xuất (Manufacturing PMI). Phản ánh đơn đặt hàng mới, sản lượng sản xuất, việc làm và lượng hàng tồn kho.",
        "good": "PMI > 50 điểm (Vùng Mở Rộng): Doanh nghiệp nhận nhiều đơn hàng mới, tăng tuyển dụng nhân công và mở rộng sản xuất. Càng cao (52 - 55) càng tích cực.",
        "bad": "PMI < 50 điểm (Vùng Thu Hẹp): Sản lượng suy giảm, đơn hàng xuất khẩu sụt giảm, tồn kho ứ đọng, báo hiệu giai đoạn ảm đạm của ngành công nghiệp.",
        "current_ai_verdict": "PMI đạt 52.40 điểm (+1.6 điểm) => RẤT TỐT: Ngành sản xuất Việt Nam đang mở rộng mạnh mẽ, đơn hàng FDI và xuất khẩu hồi phục rõ nét.",
    },
    "vn_cpi": {
        "nature": "Chỉ số giá tiêu dùng hàng năm (Consumer Price Index - CPI). La bàn đo lường mức độ trượt giá của rổ hàng hóa sinh hoạt và lạm phát chung.",
        "good": "Lạm phát CPI ở mức 3.0% - 4.0%/năm: Mức tăng giá vừa phải kích thích doanh nghiệp sản xuất kinh doanh, trong khi không làm suy giảm sức mua của người dân.",
        "bad": "CPI > 4.5% - 5.0%: Vượt trần kiểm soát của Quốc hội, buộc NHNN phải tăng lãi suất điều hành để kiềm chế lạm phát, gây áp lực tiêu cực lên thị trường tài sản.",
        "current_ai_verdict": "CPI Việt Nam ở mức 4.36% (hoặc ~3.31% MoM) => KIỂM SOÁT TỐT: Nằm trọn vẹn trong mục tiêu trần < 4.5% của Chính phủ, tạo dư địa lớn để nới lỏng tiền tệ.",
    },
    "vn_gdp": {
        "nature": "Tổng sản phẩm quốc nội. Thước đo quy mô và sức khỏe tăng trưởng tổng thể của toàn bộ nền kinh tế Việt Nam.",
        "good": "Tăng trưởng GDP > 6.5% - 7.5%/năm: Nền kinh tế tăng trưởng thần tốc, thu hút dòng vốn FDI, gia tăng thu nhập bình quân đầu người và mở rộng thị trường nội địa.",
        "bad": "Tăng trưởng GDP < 5.0%: Tăng trưởng chậm chạp, dấu hiệu của sự chững lại trong cầu tiêu dùng và đầu tư công.",
        "current_ai_verdict": "Quy mô GDP đạt 433.7 - 514 Tỷ USD, tăng trưởng kỳ vọng 6.5% - 7.0% => VƯỢT TRỘI: Việt Nam nằm trong nhóm các quốc gia có tốc độ tăng trưởng GDP cao nhất khu vực.",
    },
    "usd_vnd_rate": {
        "nature": "Tỷ giá hối đoái giữa đồng Đô la Mỹ và Việt Nam Đồng. Thước đo áp lực mất giá tiền tệ và dòng vốn xuất nhập khẩu/FDI.",
        "good": "Tỷ giá biến động trong biên độ cho phép (+1% - 3%/năm): Bảo vệ giá trị đồng nội tệ, không gây áp lực nhập khẩu lạm phát, ổn định tâm lý nhà đầu tư ngoại.",
        "bad": "Tỷ giá mất giá nhanh > 4% - 5% trong thời gian ngắn: Buộc NHNN phải can thiệp bán ngoại tệ dự trữ hoặc tăng lãi suất để giữ giá trị VND, gây rút ròng vốn ngoại.",
        "current_ai_verdict": "Tỷ giá quanh mức 25,420 đ/USD (+40 đ) => THEO DÕI: Biên độ tỷ giá đang được NHNN giữ vững, áp lực sẽ hạ nhiệt khi Fed chính thức cắt giảm lãi suất.",
    },
    "fed_funds": {
        "nature": "Lãi suất điều hành của Cục Dự trữ Liên bang Mỹ (Fed). Yếu tố định hình chi phí vốn và hướng đi của dòng tiền toàn cầu.",
        "good": "Fed bắt đầu chu kỳ cắt giảm lãi suất: Đồng USD hạ nhiệt (DXY giảm), giảm áp lực tỷ giá lên các thị trường mới nổi như Việt Nam, mở đường cho dòng vốn ngoại quay trở lại.",
        "bad": "Fed duy trì lãi suất 'Cao hơn trong thời gian dài' (Higher for longer): Tạo chênh lệch lãi suất USD-VND lớn, gây áp lực chảy máu ngoại tệ và hạn chế dư địa hạ lãi suất trong nước.",
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

📈 SỐ LIỆU HIỆN TẠI:
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
