import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# เชื่อมต่อผ่านไฟล์ที่อยู่ใน GitHub ของคุณโดยตรง
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# เปลี่ยนชื่อไฟล์ให้ตรงกับไฟล์ที่คุณสร้างใน GitHub
creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
client = gspread.authorize(creds)

# ลิงก์ตารางของคุณ
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1ZGdB9tBYAibMva6SnEVGrzRf80j5HHjWLj9Hs1gNd4c/edit"
sheet = client.open_by_url(spreadsheet_url)

# ดึงข้อมูล
sales_df = pd.DataFrame(sheet.worksheet("Sales").get_all_records())
exp_df = pd.DataFrame(sheet.worksheet("Expenses").get_all_records())
