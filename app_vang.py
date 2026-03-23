import streamlit as st
import pandas as pd
import io

# Cấu hình giao diện trang web
st.set_page_config(page_title="Phân Tích Dòng Tiền Vàng", layout="wide", page_icon="📈")

st.title("📈 Ứng Dụng Quản Trị Dòng Tiền Đầu Tư Vàng (3 Giai Đoạn)")
st.markdown("Phần mềm hỗ trợ tính toán hiệu quả sử dụng đòn bẩy tài chính, theo dõi dư nợ giảm dần và quy đổi giá trị tương đương vốn tự có.")

# --- SIDEBAR: GIAO DIỆN NHẬP LIỆU ---
st.sidebar.header("⚙️ Thông Số Đầu Vào")

loan = st.sidebar.number_input("Vốn vay (Triệu VNĐ)", value=661.5, step=10.0, format="%.2f")
buy_price = st.sidebar.number_input("Giá mua vào (Triệu/cây)", value=147.0, step=1.0, format="%.2f")
loan_rate = st.sidebar.number_input("Lãi suất vay (%/năm)", value=8.9, step=0.1, format="%.2f")
savings_rate = st.sidebar.number_input("Lãi tiết kiệm (%/năm)", value=5.0, step=0.1, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("Đợt bán 1")
col1, col2 = st.sidebar.columns(2)
m1 = col1.number_input("Tháng thứ", value=3, min_value=1, step=1)
r1 = col2.number_input("Tỷ lệ bán (%)", value=30.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f")
p1 = st.sidebar.number_input("Giá bán đợt 1 (Tr/cây)", value=180.0, step=1.0, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("Đợt bán 2")
col3, col4 = st.sidebar.columns(2)

# Khắc phục lỗi: Đảm bảo tháng mặc định của đợt 2 luôn lớn hơn hoặc bằng đợt 1
default_m2 = max(7, int(m1))
m2 = col3.number_input("Tháng thứ ", value=default_m2, min_value=int(m1), step=1)

# Khắc phục lỗi tỷ lệ: Nếu đợt 1 bán hết, đợt 2 tối đa chỉ là 0%
r2_max = float(max(0.0, 100.0 - r1))
default_r2 = min(40.0, r2_max)
r2 = col4.number_input("Tỷ lệ bán  (%)", value=default_r2, min_value=0.0, max_value=r2_max, step=1.0, format="%.1f")

p2 = st.sidebar.number_input("Giá bán đợt 2 (Tr/cây)", value=200.0, step=1.0, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("Đợt bán cuối (Tất toán)")
r3 = max(0.0, 100.0 - r1 - r2)
st.sidebar.info(f"Tỷ lệ bán đợt cuối tự động tính: **{r3:.1f}%**")
col5, col6 = st.sidebar.columns(2)

# Khắc phục lỗi: Đảm bảo tháng mặc định của đợt 3 luôn lớn hơn hoặc bằng đợt 2
default_m3 = max(12, int(m2))
m3 = col5.number_input("Tháng chốt", value=default_m3, min_value=int(m2), step=1)
p3 = col6.number_input("Giá (Tr/cây)", value=220.0, step=1.0, format="%.2f")


# --- XỬ LÝ LÕI TOÁN HỌC ---
if buy_price > 0 and loan > 0:
    total_gold = loan / buy_price
    principal = loan
    savings = 0
    prev_month = 0
    
    # Hàm xử lý từng đợt
    def process_stage(m, r, p, current_principal, current_savings, prev_m):
        t = max(0, m - prev_m)
        # Tính lãi vay
        accrued_int = current_principal * (loan_rate / 100) * (t / 12)
        # Lãi tiết kiệm từ kỳ trước
        sav_int = 0
        if current_savings > 0:
            sav_int = current_savings * (savings_rate / 100) * (t / 12)
            current_savings += sav_int
            
        qty_sold = total_gold * (r / 100)
        revenue = qty_sold * p
        cashflow = revenue + current_savings
        
        # Thanh toán lãi
        cashflow -= accrued_int
        
        paydown = 0
        if cashflow > 0:
            paydown = min(cashflow, current_principal)
            current_principal -= paydown
            current_savings = cashflow - paydown
        else:
            current_savings = cashflow # Ghi nhận âm (phải tự bỏ tiền túi trả lãi)
            
        return current_principal, current_savings, qty_sold, revenue, accrued_int, sav_int, paydown

    # Chạy 3 đợt
    prin1, sav1, q1, rev1, int1, sint1, pay1 = process_stage(m1, r1, p1, principal, savings, prev_month)
    prin2, sav2, q2, rev2, int2, sint2, pay2 = process_stage(m2, r2, p2, prin1, sav1, m1)
    prin3, sav3, q3, rev3, int3, sint3, pay3 = process_stage(m3, r3, p3, prin2, sav2, m2)

    net_profit = sav3 - prin3
    equivalent_price = (net_profit + loan) / total_gold
    
    # Nếu chưa bán lượng vàng nào, tránh lỗi chia cho 0
    total_revenue = rev1 + rev2 + rev3
    actual_avg_price = total_revenue / total_gold if total_gold > 0 else 0

    # --- HIỂN THỊ KẾT QUẢ GIAO DIỆN ---
    st.subheader("🎯 Báo Cáo Hiệu Quả Đầu Tư")
    
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Tổng Lợi Nhuận Ròng", f"{net_profit:,.2f} Tr")
    metric2.metric("Giá Bán Trung Bình", f"{actual_avg_price:,.2f} Tr/cây")
    metric3.metric("Giá Quy Đổi (Vốn Tự Có)", f"{equivalent_price:,.2f} Tr/cây", 
                   help="Mức giá bán tương đương nếu bạn dùng 100% tiền túi không đi vay.")

    st.markdown("### 📊 Tiến trình thanh lý & Dập nợ gốc")
    
    # Tạo DataFrame để hiển thị bảng
    df = pd.DataFrame({
        "Giai đoạn": [f"Đợt 1 (Tháng {m1})", f"Đợt 2 (Tháng {m2})", f"Đợt 3 (Tháng {m3})"],
        "Doanh thu (Tr)": [round(rev1, 2), round(rev2, 2), round(rev3, 2)],
        "Lãi vay phát sinh (Tr)": [round(int1, 2), round(int2, 2), round(int3, 2)],
        "Dập nợ gốc (Tr)": [round(pay1, 2), round(pay2, 2), round(prin2, 2)], 
        "Dư nợ còn lại (Tr)": [round(prin1, 2), round(prin2, 2), 0.0]
    })
    
    st.table(df)

    # --- XUẤT EXCEL ---
    st.markdown("### 📥 Xuất Dữ Liệu")
    
    # Tạo dữ liệu chi tiết cho Excel
    excel_data = {
        "Thông số": ["Vốn vay", "Giá mua", "Lãi vay %", "Đợt 1 (Tháng/Tỷ lệ/Giá)", "Đợt 2", "Đợt 3", "Lợi nhuận ròng", "Giá quy đổi"],
        "Giá trị": [loan, buy_price, loan_rate, f"T{m1} / {r1}% / {p1}", f"T{m2} / {r2}% / {p2}", f"T{m3} / {r3}% / {p3}", round(net_profit,2), round(equivalent_price,2)]
    }
    df_excel = pd.DataFrame(excel_data)

    # Chuyển DataFrame thành file Excel trong bộ nhớ
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_excel.to_excel(writer, sheet_name='Tong_Ket', index=False)
        df.to_excel(writer, sheet_name='Chi_Tiet_Dong_Tien', index=False)
    
    excel_file = output.getvalue()

    st.download_button(
        label="Tải Báo Cáo Excel",
        data=excel_file,
        file_name="Bao_Cao_Dau_Tu_Vang.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
