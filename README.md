import streamlit as st
import pandas as pd
import datetime

# ตั้งค่าหน้าแอป
st.set_page_config(page_title="Perfume Shop System", layout="wide")

st.title("📊 ระบบบัญชีและแดชบอร์ด ร้านน้ำหอมตลาดคลอง ร.5")
st.write("ระบบบันทึกยอดขายและบริหารกระแสเงินสดร่วมกัน")

# ตารางต้นทุนอ้างอิง
COST_DICT = {3: 10.84, 10: 61.18, 30: 102.11}

# ใช้ Session State จำลองฐานข้อมูล (ในอนาคตเชื่อม Google Sheets ได้)
if 'sales_db' not in st.session_state:
    st.session_state.sales_db = pd.DataFrame(columns=["วันที่", "ชื่อน้ำหอม", "ขนาด (ML.)", "ราคาขาย", "จำนวน", "รวมยอดขาย", "รวมต้นทุน", "กำไรขั้นต้น"])
if 'exp_db' not in st.session_state:
    st.session_state.exp_db = pd.DataFrame(columns=["วันที่", "รายการ", "จำนวนเงิน", "หมายเหตุ"])

# รายการข้อมูลตัวอย่างเริ่มต้น (ถ้าฐานข้อมูลยังว่าง)
if st.session_state.sales_db.empty:
    init_sales = [
        [datetime.date(2026, 6, 3), "Apollo", 30, 350, 1, 350, 102.11, 247.89],
        [datetime.date(2026, 6, 3), "Poseidon", 30, 350, 1, 350, 102.11, 247.89],
        [datetime.date(2026, 6, 3), "Mercury", 30, 350, 1, 350, 102.11, 247.89],
        [datetime.date(2026, 6, 3), "Poseidon", 10, 219, 1, 219, 61.18, 157.82],
        [datetime.date(2026, 6, 3), "Demeter", 30, 350, 1, 350, 102.11, 247.89],
    ]
    st.session_state.sales_db = pd.DataFrame(init_sales, columns=st.session_state.sales_db.columns)

if st.session_state.exp_db.empty:
    init_exp = [
        [datetime.date(2026, 6, 3), "ค่าเช่าที่ตลาดคลองร.5 (เหมา 3 วัน)", 500.0, "จ่ายสด"],
        [datetime.date(2026, 6, 3), "ค่าเดินทาง (ไป-กลับ)", 160.0, "วินมอเตอร์ไซค์"],
        [datetime.date(2026, 6, 3), "กรรไกร", 59.0, "ใช้นาน"],
    ]
    st.session_state.exp_db = pd.DataFrame(init_exp, columns=st.session_state.exp_db.columns)

# คำนวณตัวเลขสำหรับ Dashboard
total_sales = st.session_state.sales_db["รวมยอดขาย"].sum()
total_cogs = st.session_state.sales_db["รวมต้นทุน"].sum()
gross_profit = total_sales - total_cogs
total_expenses = st.session_state.exp_db["จำนวนเงิน"].sum()
net_profit = gross_profit - total_expenses

# คำนวณตามสูตรกระแสเงินสดของผู้ใช้
reserve_rate = 0.40
money_to_reserve = net_profit * reserve_rate if net_profit > 0 else 0
total_capital_pool = total_cogs + money_to_reserve
withdrawable_amount = net_profit - money_to_reserve if net_profit > 0 else 0

# --- ส่วนที่ 1: DASHBOARD สรุปยอด ---
st.subheader("📈 สรุปผลประกอบการวันนี้")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("ยอดขายทั้งหมด", f"{total_sales:,.2f} บาท")
col2.metric("ต้นทุนสินค้า (COGS)", f"{total_cogs:,.2f} บาท")
col3.metric("กำไรขั้นต้น", f"{gross_profit:,.2f} บาท")
col4.metric("ค่าใช้จ่ายรวม", f"{total_expenses:,.2f} บาท", delta=f"-{total_expenses}", delta_color="inverse")
col5.metric("กำไรสุทธิ (Net Profit)", f"{net_profit:,.2f} บาท")

st.markdown("---")
st.subheader("💰 การจัดสรรกระแสเงินสด (ตามสูตรของคุณ)")
c_pool1, c_pool2, c_pool3 = st.columns(3)
c_pool1.info(f"🏦 **เงินเก็บเข้าทุนสำรอง ({int(reserve_rate*100)}%):** {money_to_reserve:,.2f} บาท\n\n*(ยอดเงินทุนรวมหมุนเวียนคราวหน้า: {total_capital_pool:,.2f} บาท)*")
c_pool2.success(f"💵 **ส่วนที่เบิกไปใช้ได้ (60%):** {withdrawable_amount:,.2f} บาท")
actual_withdraw = c_pool3.number_input("ใส่จำนวนเงินที่เบิกจริง (บาท)", min_value=0.0, value=0.0, step=50.0)

# คำนvac ยอดคงค้างในบัญชี
remaining_profit = withdrawable_amount - actual_withdraw
final_balance = total_capital_pool + remaining_profit
st.write(f"👉 **ยอดเงินคงเหลือรวมที่ต้องอยู่ในบัญชี/กระเป๋าเงินทั้งหมด:** `{final_balance:,.2f}` บาท")

st.markdown("---")

# --- ส่วนที่ 2: ฟอร์มกรอกข้อมูลคีย์ยอดขายและรายจ่าย ---
tab1, tab2 = st.tabs(["📝 คีย์ยอดขายใหม่", "💸 คีย์รายจ่ายใหม่"])

with tab1:
    with st.form("sales_form", clear_on_submit=True):
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        s_date = col_s1.date_input("วันที่ขาย", datetime.date.today())
        s_name = col_s2.text_input("ชื่อกลิ่นน้ำหอม (เช่น Zeus, Apollo)")
        s_size = col_s3.selectbox("ขนาดขวด (ML.)", [3, 10, 30])
        s_price = col_s4.number_input("ราคาขายต่อขวด (บาท)", min_value=0, value=350 if s_size==30 else (219 if s_size==10 else 50))
        s_qty = st.number_input("จำนวนที่ขายได้ (ขวด)", min_value=1, value=1)
        
        submit_sale = st.form_submit_button("บันทึกออเดอร์")
        if submit_sale and s_name:
            item_cost = COST_DICT.get(s_size, 0)
            total_s_price = s_price * s_qty
            total_s_cost = item_cost * s_qty
            item_gross_profit = total_s_price - total_s_cost
            
            new_sale = [s_date, s_name, s_size, s_price, s_qty, total_s_price, total_s_cost, item_gross_profit]
            st.session_state.sales_db.loc[len(st.session_state.sales_db)] = new_sale
            st.success(f"บันทึกออเดอร์ {s_name} เรียบร้อย!")
            st.rerun()

with tab2:
    with st.form("exp_form", clear_on_submit=True):
        col_e1, col_e2, col_e3 = st.columns(3)
        e_date = col_e1.date_input("วันที่จ่าย", datetime.date.today())
        e_title = col_e2.text_input("รายการรายจ่าย (เช่น ค่าถุง, ค่าที่)")
        e_amount = col_e3.number_input("จำนวนเงิน (บาท)", min_value=0.0, value=0.0)
        e_note = st.text_input("หมายเหตุ")
        
        submit_exp = st.form_submit_button("บันทึกรายจ่าย")
        if submit_exp and e_title and e_amount > 0:
            new_exp = [e_date, e_title, e_amount, e_note]
            st.session_state.exp_db.loc[len(st.session_state.exp_db)] = new_exp
            st.success(f"บันทึกรายจ่าย {e_title} เรียบร้อย!")
            st.rerun()

# --- ส่วนที่ 3: ตารางแสดงข้อมูล ---
st.subheader("📋 รายการบันทึกวันนี้")
col_t1, col_t2 = st.columns([2, 1])
with col_t1:
    st.write("**ตารางยอดขาย**")
    st.dataframe(st.session_state.sales_db, use_container_width=True)
with col_t2:
    st.write("**ตารางรายจ่าย**")
    st.dataframe(st.session_state.exp_db, use_container_width=True)
