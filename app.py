import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Perfume Shop System", layout="wide")

# ตั้งค่าการเชื่อมต่อ
# ดึงค่าจาก st.secrets โดยตรง
creds_dict = st.secrets["gcp"]
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# ดึง URL จาก Secrets
spreadsheet_url = st.secrets["gcp"]["spreadsheet"]
sheet = client.open_by_url(spreadsheet_url)

# ดึงข้อมูล
sales_df = pd.DataFrame(sheet.worksheet("Sales").get_all_records())
exp_df = pd.DataFrame(sheet.worksheet("Expenses").get_all_records())
