import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Perfume Shop System", layout="wide")

# ตั้งค่าการเชื่อมต่อด้วย gspread
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# ดึงค่าจาก st.secrets
creds_dict = dict(st.secrets["gcp"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
spreadsheet_url = st.secrets["gcp"]["spreadsheet"]
sheet = client.open_by_url(spreadsheet_url)

# ดึงข้อมูล
sales_df = pd.DataFrame(sheet.worksheet("Sales").get_all_records())
exp_df = pd.DataFrame(sheet.worksheet("Expenses").get_all_records())

# ... (ส่วนการคำนวณและแสดงผลคงเดิม) ...

# ส่วนการบันทึกข้อมูล (แก้ใหม่ตรงนี้)
if submit_sale and s_name:
    # ... คำนวณ ...
    new_row = [str(s_date), s_name, s_size, s_price, s_qty, total_s_price, total_s_cost, item_gross_profit]
    sheet.worksheet("Sales").append_row(new_row) # ใช้ gspread เขียนแทน
    st.success("บันทึกข้อมูลแล้ว!")
    st.rerun()

if submit_exp and e_title and e_amount > 0:
    new_row = [str(e_date), e_title, e_amount, e_note]
    sheet.worksheet("Expenses").append_row(new_row) # ใช้ gspread เขียนแทน
    st.success("บันทึกรายจ่ายแล้ว!")
    st.rerun()
