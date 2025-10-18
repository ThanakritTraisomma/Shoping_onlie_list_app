import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ======================
# 🔧 ตั้งค่าเริ่มต้น
# ======================
st.set_page_config(page_title="รายงานภาษีขายรายวัน", page_icon="📑", layout="wide")
st.title("📑 ระบบบันทึกข้อมูลรายงานภาษีขายรายวัน")

DATA_FILE = "sales_daily.xlsx"

# ======================
# 🧱 กำหนดคอลัมน์
# ======================
COLUMNS = [
    "วันที่สั่งซื้อ",
    "เลขที่คำสั่งซื้อ",
    "ชื่อลูกค้า",
    "ยอดรวมสุทธิ",
    "เลขที่ใบโอน",
    "หมายเหตุ"
]

# ======================
# 📦 โหลดไฟล์ (หรือสร้างใหม่)
# ======================
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_excel(DATA_FILE)

        # ตรวจสอบว่าคอลัมน์ครบไหม ถ้าไม่ครบให้เพิ่ม
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[COLUMNS]  # จัดเรียงคอลัมน์ให้ตรงกัน
    except Exception:
        df = pd.DataFrame(columns=COLUMNS)
else:
    df = pd.DataFrame(columns=COLUMNS)

# ======================
# 🧭 ตัวช่วย session
# ======================
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ======================
# 🧾 ฟอร์มกรอกข้อมูล
# ======================
st.subheader("🧾 ฟอร์มกรอกข้อมูล")

with st.form("input_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        order_date = st.date_input("วันที่สั่งซื้อ", datetime.today())
        order_id = st.text_input("เลขที่คำสั่งซื้อ")
        customer_name = st.text_input("ชื่อลูกค้า")
    with col2:
        total_amount = st.number_input("ยอดรวมสุทธิ (บาท)", min_value=0.0, step=0.01)
        transfer_id = st.text_input("เลขที่ใบโอน")
        remark_choice = st.selectbox(
            "หมายเหตุ",
            ["", "รอตรวจสอบ", "ชำระไม่ครบ", "ส่งไม่สำเร็จ", "อื่น ๆ"]
        )

    remark_text = ""
    if remark_choice != "":
        remark_text = st.text_area("รายละเอียดเพิ่มเติม")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

# ======================
# 💾 การบันทึกข้อมูล
# ======================
if submitted:
    new_row = {
        "วันที่สั่งซื้อ": order_date,
        "เลขที่คำสั่งซื้อ": order_id,
        "ชื่อลูกค้า": customer_name,
        "ยอดรวมสุทธิ": total_amount,
        "เลขที่ใบโอน": transfer_id,
        "หมายเหตุ": f"{remark_choice} - {remark_text}" if remark_choice else ""
    }

    if st.session_state.edit_index is not None:
        df.loc[st.session_state.edit_index] = new_row
        st.session_state.edit_index = None
        st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว")
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว")

    df.to_excel(DATA_FILE, index=False)

# ======================
# 📊 แสดงข้อมูลแบบตาราง
# ======================
st.divider()
st.subheader("📋 ข้อมูลทั้งหมด")

if not df.empty:
    df = df.sort_values(by="วันที่สั่งซื้อ", ascending=True).reset_index(drop=True)

    for i, row in df.iterrows():
        cols = st.columns([2, 2, 2, 2, 2, 2, 1])  # เพิ่มคอลัมน์ปุ่ม

        cols[0].write(row["วันที่สั่งซื้อ"])
        cols[1].write(row["เลขที่คำสั่งซื้อ"])
        cols[2].write(row["ชื่อลูกค้า"])
        cols[3].write(f"{row['ยอดรวมสุทธิ']:,}")
        cols[4].write(row["เลขที่ใบโอน"])
        cols[5].write(row.get("หมายเหตุ", ""))

        with cols[6]:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.experimental_rerun()
            if st.button("🗑️", key=f"delete_{i}"):
                df = df.drop(i).reset_index(drop=True)
                df.to_excel(DATA_FILE, index=False)
                st.experimental_rerun()
else:
    st.info("ยังไม่มีข้อมูลในระบบ")

