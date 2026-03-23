import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Phân Tích Dòng Tiền Cà Phê", layout="wide", page_icon="☕")

st.title("☕ Ứng Dụng Quản Trị Đầu Tư Cà Phê (Vốn Tự Có)")
st.markdown("So sánh hiệu quả giữa chiến lược **Bán rải đợt + Gửi tiết kiệm tiền thu được** so với **Giữ nguyên 100% sản lượng chờ bán ở giá cuối vụ**.")

# --- SIDEBAR: GIAO DIỆN NHẬP LIỆU ---
st.sidebar.header("⚙️ Quy Mô & Lãi Suất")

total_coffee = st.sidebar.number_input("Sản lượng hiện có (Tấn)", value=3.0, step=0.1, format="%.2f")
savings_rate = st.sidebar.number_input("Lãi suất gửi tiết kiệm (%/năm)", value=5.0, step=0.1, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.header("⏱️ Chiến Lược Bán Rải Đợt")

st.sidebar.subheader("Đợt bán 1")
col1, col2 = st.sidebar.columns(2)
m1 = col1.number_input("Tháng thứ", value=3, min_value=1, step=1)
r1 = col2.number_input("Tỷ lệ bán (%)", value=30.0, min_value=0.0, max_value=100.0, step=1.0, format="%.1f")
p1 = st.sidebar.number_input("Giá bán đợt 1 (Tr/tấn)", value=110.0, step=1.0, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("Đợt bán 2")
col3, col4 = st.sidebar.columns(2)
m2 = col3.number_input("Tháng thứ ", value=max(7, int(m1)), min_value=int(m1), step=1)
r2_max = float(max(0.0, 100.0 - r1))
r2 = col4.number_input("Tỷ lệ bán  (%)", value=min(40.0, r2_max), min_value=0.0, max_value=r2_max, step=1.0, format="%.1f")
p2 = st.sidebar.number_input("Giá bán đợt 2 (Tr/tấn)", value=125.0, step=1.0, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("Đợt chốt cuối")
r3 = max(0.0, 100.0 - r1 - r2)
st.sidebar.markdown(f"*Tỷ lệ còn lại bán nốt: **{r3:.1f}%***")
col5, col6 = st.sidebar.columns(2)
m3 = col5.number_input("Tháng chốt cuối", value=max(12, int(m2)), min_value=int(m2), step=1)
p3 = col6.number_input("Giá kỳ vọng (Tr/tấn)", value=140.0, step=1.0, format="%.2f")

# --- XỬ LÝ LÕI TOÁN HỌC ---
if total_coffee > 0:
    # 1. Tính toán cho chiến lược Bán Rải Đợt (Staged Strategy)
    q1 = total_coffee * (r1 / 100)
    rev1 = q1 * p1
    time_in_bank_1 = max(0, m3 - m1) / 12
    int1 = rev1 * (savings_rate / 100) * time_in_bank_1

    q2 = total_coffee * (r2 / 100)
    rev2 = q2 * p2
    time_in_bank_2 = max(0, m3 - m2) / 12
    int2 = rev2 * (savings_rate / 100) * time_in_bank_2

    q3 = total_coffee * (r3 / 100)
    rev3 = q3 * p3

    total_revenue_staged = rev1 + rev2 + rev3
    total_interest_earned = int1 + int2
    final_cash_staged = total_revenue_staged + total_interest_earned
    
    # Giá bán trung bình thực tế (bao gồm cả lãi ngân hàng đẻ ra)
    effective_price_staged = final_cash_staged / total_coffee

    # 2. Tính toán cho chiến lược Giữ 100% (Hold Strategy)
    final_cash_hold = total_coffee * p3
    effective_price_hold = p3

    # So sánh
    diff_cash = final_cash_staged - final_cash_hold

    # --- HIỂN THỊ KẾT QUẢ GIAO DIỆN ---
    st.subheader("⚖️ Bàn Cân Chiến Lược (Tại mốc Tháng " + str(m3) + ")")
    
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("### 📈 Chiến Lược Bán Rải Đợt + Gửi NH")
        st.info(f"""
        - **Tổng tiền mặt thu về:** **{final_cash_staged:,.2f} Tr**
        - Từ tiền bán cà phê: {total_revenue_staged:,.2f} Tr
        - Từ tiền lãi ngân hàng: {total_interest_earned:,.2f} Tr
        - **Giá bán thực tế (Gồm lãi): {effective_price_staged:,.2f} Tr/tấn**
        """)

    with colB:
        st.markdown("### 📦 Chiến Lược Giữ 100% Đến Cùng")
        st.warning(f"""
        - **Tổng tiền mặt thu về:** **{final_cash_hold:,.2f} Tr**
        - Từ tiền bán cà phê: {final_cash_hold:,.2f} Tr
        - Từ tiền lãi ngân hàng: 0.00 Tr
        - **Giá bán thực tế: {effective_price_hold:,.2f} Tr/tấn**
        """)

    if diff_cash > 0:
        st.success(f"🔥 Kết luận: **Bán rải đợt** mang lại nhiều tiền hơn **{diff_cash:,.2f} Tr** so với việc giữ 100% chờ giá cuối vụ.")
    elif diff_cash < 0:
        st.error(f"⚠️ Kết luận: **Giữ 100%** đến cuối vụ mang lại nhiều tiền hơn **{-diff_cash:,.2f} Tr**. Giá cuối vụ tăng quá mạnh đã đánh bại lãi suất ngân hàng.")
    else:
        st.info("Kết luận: Cả hai chiến lược mang lại hiệu quả tương đương nhau.")

    # Bảng phân tích chi tiết dòng tiền
    st.markdown("### 📊 Phân tích Chi tiết Chiến lược Bán rải đợt")
    df_staged = pd.DataFrame({
        "Giai đoạn": [f"Đợt 1 (T{m1})", f"Đợt 2 (T{m2})", f"Đợt cuối (T{m3})"],
        "Sản lượng bán (Tấn)": [round(q1, 2), round(q2, 2), round(q3, 2)],
        "Giá bán (Tr/tấn)": [p1, p2, p3],
        "Thu tiền mặt (Tr)": [round(rev1, 2), round(rev2, 2), round(rev3, 2)],
        "Kỳ hạn gửi NH (Tháng)": [m3 - m1, m3 - m2, 0],
        "Lãi tiết kiệm sinh ra (Tr)": [round(int1, 2), round(int2, 2), 0.0]
    })
    st.table(df_staged)

    # --- XUẤT EXCEL ---
    st.markdown("### 📥 Lưu trữ kịch bản")
    
    excel_data_summary = {
        "Chỉ số": ["Sản lượng (Tấn)", "Lãi ngân hàng %", "Tổng thu rải đợt (Tr)", "Tổng thu giữ 100% (Tr)", "Giá thực tế rải đợt", "Giá thực tế giữ 100%"],
        "Giá trị": [total_coffee, savings_rate, round(final_cash_staged, 2), round(final_cash_hold, 2), round(effective_price_staged, 2), round(effective_price_hold, 2)]
    }
    df_excel_summary = pd.DataFrame(excel_data_summary)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_excel_summary.to_excel(writer, sheet_name='So_Sanh_Chien_Luoc', index=False)
        df_staged.to_excel(writer, sheet_name='Chi_Tiet_Ban_Rai_Dot', index=False)
    
    excel_file = output.getvalue()

    st.download_button(
        label="Tải Báo Cáo Excel Cà Phê",
        data=excel_file,
        file_name="Bao_Cao_Dau_Tu_Ca_Phe.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
