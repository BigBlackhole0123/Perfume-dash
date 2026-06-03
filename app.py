import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Perfume Shop System", layout="wide")
st.title("📊 ระบบบัญชีร้านน้ำหอมตลาดคลอง ร.5 (บันทึกถาวร)")

COST_DICT = {3: 10.84, 10: 61.18, 30: 102.11}

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ดึงข้อมูลจาก Sheets
try:
    sales_df = conn.read(worksheet="Sales", ttl=0).dropna(subset=["ชื่อน้ำหอม"])
except Exception:
    sales_df = pd.DataFrame(columns=["วันที่", "ชื่อน้ำหอม", "ขนาด (ML.)", "ราคาขาย", "จำนวน", "รวมยอดขาย", "รวมต้นทุน", "กำไรขั้นต้น"])

try:
    exp_df = conn.read(worksheet="Expenses", ttl=0).dropna(subset=["รายการ"])
except Exception:
    exp_df = pd.DataFrame(columns=["วันที่", "รายการ", "จำนวนเงิน", "หมายเหตุ"])

# --- ส่วนคำนวณแดชบอร์ด ---
total_sales = pd.to_numeric(sales_df["รวมยอดขาย"], errors='coerce').sum() if "รวมยอดขาย" in sales_df.columns else 0
total_cogs = pd.to_numeric(sales_df["รวมต้นทุน"], errors='coerce').sum() if "รวมต้นทุน" in sales_df.columns else 0
gross_profit = total_sales - total_cogs
total_expenses = pd.to_numeric(exp_df["จำนวนเงิน"], errors='coerce').sum() if "จำนวนเงิน" in exp_df.columns else 0

# คำนวณกำไรสุทธิ
net_profit = gross_profit - total_expenses

reserve_rate = 0.40
money_to_reserve = net_profit * reserve_rate if net_profit > 0 else 0
total_capital_pool = total_cogs + money_to_reserve
withdrawable_amount = net_profit - money_to_reserve if net_profit > 0 else 0

st.subheader("📈 สรุปผลประกอบการวันนี้")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("ยอดขายทั้งหมด", f"{total_sales:,.2f} บาท")
col2.metric("ต้นทุนสินค้า (COGS)", f"{total_cogs:,.2f} บาท")
col3.metric("กำไรขั้นต้น", f"{gross_profit:,.2f} บาท")
col4.metric("ค่าใช้จ่ายรวม", f"{total_expenses:,.2f} บาท")
col5.metric("กำไรสุทธิ (Net Profit)", f"{net_profit:,.2f} บาท")

st.markdown("---")
st.subheader("💰 การจัดสรรกระแสเงินสด")
c_pool1, c_pool2 = st.columns(2)
c_pool1.info(f"🏦 **เงินเก็บเข้าทุนสำรอง ({int(reserve_rate*100)}%):** {money_to_reserve:,.2f} บาท\n\n*(ยอดเงินทุนรวมหมุนเวียนคราวหน้า: {total_capital_pool:,.2f} บาท)*")
c_pool2.success(f"💵 **ส่วนที่แฟนและคุณเบิกไปใช้ได้ (60%):** {withdrawable_amount:,.2f} บาท")

st.markdown("---")
tab1, tab2 = st.tabs(["📝 คีย์ยอดขายใหม่", "💸 คีย์รายจ่ายใหม่"])

with tab1:
    with st.form("sales_form", clear_on_submit=True):
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        s_date = col_s1.date_input("วันที่ขาย", datetime.date.today())
        s_name = col_s2.text_input("ชื่อกลิ่นน้ำหอม")
        s_size = col_s3.selectbox("ขนาดขวด (ML.)", [3, 10, 30])
        s_price = col_s4.number_input("ราคาขายต่อขวด (บาท)", min_value=0, value=350 if s_size==30 else (219 if s_size==10 else 50))
        s_qty = st.number_input("จำนวนที่ขายได้ (ขวด)", min_value=1, value=1)
        
        submit_sale = st.form_submit_button("บันทึกออเดอร์ลง Google Sheets")
        if submit_sale and s_name:
            item_cost = COST_DICT.get(s_size, 0)
            total_s_price = s_price * s_qty
            total_s_cost = item_cost * s_qty
            item_gross_profit = total_s_price - total_s_cost
            new_row = pd.DataFrame([[str(s_date), s_name, s_size, s_price, s_qty, total_s_price, total_s_cost, item_gross_profit]], columns=sales_df.columns)
            updated_sales = pd.concat([sales_df, new_row], ignore_index=True)
            conn.update(worksheet="Sales", data=updated_sales)
            st.success("บันทึกข้อมูลเรียบร้อย!")
            st.rerun()

with tab2:
    with st.form("exp_form", clear_on_submit=True):
        col_e1, col_e2, col_e3 = st.columns(3)
        e_date = col_e1.date_input("วันที่จ่าย", datetime.date.today())
        e_title = col_e2.text_input("รายการรายจ่าย")
        e_amount = col_e3.number_input("จำนวนเงิน (บาท)", min_value=0.0, value=0.0)
        e_note = st.text_input("หมายเหตุ")
        
        submit_exp = st.form_submit_button("บันทึกรายจ่ายลง Google Sheets")
        if submit_exp and e_title and e_amount > 0:
            new_row = pd.DataFrame([[str(e_date), e_title, e_amount, e_note]], columns=exp_df.columns)
            updated_exp = pd.concat([exp_df, new_row], ignore_index=True)
            conn.update(worksheet="Expenses", data=updated_exp)
            st.success("บันทึกรายจ่ายเรียบร้อย!")
            st.rerun()

st.subheader("📋 รายการปัจจุบัน")
st.write("**ตารางยอดขาย**")
st.dataframe(sales_df, use_container_width=True)
st.write("**ตารางรายจ่าย**")
st.dataframe(exp_df, use_container_width=True)
