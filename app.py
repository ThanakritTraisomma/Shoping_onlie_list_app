import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")
st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")

DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน", "หมายเหตุ"
]

# โหลดข้อมูล
if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
    df = pd.read_excel(DATA_FILE)
    # ป้องกันไฟล์เก่าไม่มีคอลัมน์ใหม่
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=COLUMNS)


def save_data(df):
    df.to_excel(DATA_FILE, index=False)


def clear_form():
    for key in list(st.session_state.keys()):
        if key not in ["edit_index"]:
            del st.session_state[key]


# ==========================
# 🧾 ฟอร์มกรอก/แก้ไขข้อมูล
# ==========================
st.subheader("🧾 กรอกหรือแก้ไขข้อมูล")

edit_mode = "edit_index" in st.session_state and st.session_state.edit_index is not None
edit_row = df.loc[st.session_state.edit_index] if edit_mode else None

with st.form("sales_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ", value=None if not edit_mode else pd.to_datetime(edit_row["วันที่สั่งซื้อ"], errors="coerce"))
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=1 if not edit_mode else int(edit_row["ลำดับ"]))
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", value="" if not edit_mode else str(edit_row["เลขที่ใบกำกับ"]))
        Seller = st.selectbox(
            "Seller", ["shopee", "lazada", "cent", "อื่นๆ"],
            index=0 if not edit_mode else (
                ["shopee", "lazada", "cent", "อื่นๆ"].index(edit_row["Seller"])
                if edit_row["Seller"] in ["shopee", "lazada", "cent", "อื่นๆ"] else 0
            ),
        )
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", value="" if not edit_mode else str(edit_row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"]))

    with col2:
        รหัส = st.text_input("รหัส", value="" if not edit_mode else str(edit_row["รหัส"]))
        สี = st.text_input("สี", value="" if not edit_mode else str(edit_row["สี"]))
        Size = st.text_input("Size", value="" if not edit_mode else str(edit_row["Size"]))
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["ราคาขาย"]))
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["ส่วนลด"]))
        สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["สุทธิ"]))

    with col3:
        วดป = st.date_input("ว.ด.ป.", value=None if not edit_mode else pd.to_datetime(edit_row["ว.ด.ป."], errors="coerce"))
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["จำนวนเงิน"]))
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["ค่าขนส่ง กทม."]))
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["ค่าขนส่ง ตจว."]))
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", value="" if not edit_mode else str(edit_row["เลขที่ใบโอน"]))
        หมายเหตุ = st.text_input("หมายเหตุ", value="" if not edit_mode else str(edit_row["หมายเหตุ"]))

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

if submitted:
    new_data = pd.DataFrame([[วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size, ราคาขาย, ส่วนลด,
        สุทธิ, วดป, จำนวนเงิน, ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน, หมายเหตุ]],
        columns=COLUMNS)

    if edit_mode:
        df.iloc[st.session_state.edit_index] = new_data.iloc[0]
        st.session_state.edit_index = None
        st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
    else:
        df = pd.concat([df, new_data], ignore_index=True)
        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

    save_data(df)
    clear_form()
    st.rerun()


# ==========================
# 📋 ตารางข้อมูล
# ==========================
st.subheader("📋 ข้อมูลทั้งหมด")

if not df.empty:
    st.write("คลิกปุ่ม ✏️ เพื่อแก้ไข หรือ 🗑️ เพื่อลบ")

    # แสดงตารางเต็มพร้อมปุ่มในแต่ละแถว
    for i, row in df.iterrows():
        cols = st.columns([0.7, 0.7, 1, 1, 1, 1, 1, 0.5])
        with cols[0]:
            st.write(row["เลขที่ใบกำกับ"])
        with cols[1]:
            st.write(row["Seller"])
        with cols[2]:
            st.write(row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"])
        with cols[3]:
            st.write(row["สุทธิ"])
        with cols[4]:
            st.write(row["จำนวนเงิน"])
        with cols[5]:
            st.write(row["เลขที่ใบโอน"])
        with cols[6]:
            st.write(row["หมายเหตุ"])
        with cols[7]:
            edit_btn = st.button("✏️", key=f"edit_{i}")
            delete_btn = st.button("🗑️", key=f"delete_{i}")

        if edit_btn:
            st.session_state.edit_index = i
            st.rerun()
        if delete_btn:
            df = df.drop(i).reset_index(drop=True)
            save_data(df)
            st.warning("🗑️ ลบข้อมูลเรียบร้อยแล้ว!")
            st.rerun()

else:
    st.info("ยังไม่มีข้อมูล กรุณากรอกข้อมูลใหม่")
