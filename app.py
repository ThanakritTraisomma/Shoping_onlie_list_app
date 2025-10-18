import streamlit as st
import pandas as pd
import os
from io import BytesIO

# ==========================
# ตั้งค่าหน้าเว็บ
# ==========================
st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")

st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")
st.write("กรอกข้อมูลใหม่, แก้ไข, หรือลบข้อมูลได้จากตารางด้านล่าง")

# ==========================
# ค่าพื้นฐาน
# ==========================
DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน", "หมายเหตุ"
]

# ==========================
# โหลดข้อมูลเดิม
# ==========================
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_excel(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=COLUMNS)
else:
    df = pd.DataFrame(columns=COLUMNS)

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ==========================
# ส่วนฟอร์มกรอก / แก้ไขข้อมูล
# ==========================
st.subheader("🧾 ฟอร์มกรอกข้อมูล")

with st.form("sales_form", clear_on_submit=(st.session_state.edit_index is None)):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ")
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1)
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ")
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent", "อื่นๆ"])
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า")

    with col2:
        st.markdown("### 🛍️ รายละเอียดสินค้า")
        รหัส = st.text_input("รหัส")
        สี = st.text_input("สี")
        Size = st.text_input("Size")

        st.markdown("---")
        st.markdown("### 💰 รายละเอียดการขาย")
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0)
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0)
        สุทธิ = st.number_input("สุทธิ", min_value=0.0)

    with col3:
        st.markdown("### 📦 การชำระเงินและขนส่ง")
        วดป = st.date_input("ว.ด.ป.")
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0)
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0)
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0)
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน")

        st.markdown("---")
        หมายเหตุเลือก = st.selectbox(
            "หมายเหตุ",
            ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"]
        )
        หมายเหตุข้อความ = ""
        if หมายเหตุเลือก:
            หมายเหตุข้อความ = st.text_area("รายละเอียดเพิ่มเติม", placeholder="ระบุรายละเอียด...")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

# ==========================
# เมื่อกดบันทึก
# ==========================
if submitted:
    new_data = pd.DataFrame([[
        วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size,
        ราคาขาย, ส่วนลด, สุทธิ, วดป, จำนวนเงิน,
        ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน, หมายเหตุข้อความ
    ]], columns=COLUMNS)

    if st.session_state.edit_index is not None:
        # อัปเดตข้อมูลแถวที่เลือก
        df.iloc[st.session_state.edit_index] = new_data.iloc[0]
        st.session_state.edit_index = None
        st.success("✏️ แก้ไขข้อมูลเรียบร้อยแล้ว!")
    else:
        # เพิ่มข้อมูลใหม่
        df = pd.concat([df, new_data], ignore_index=True)
        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

    df = df.sort_values(by="วันที่สั่งซื้อ", ascending=True).reset_index(drop=True)
    df.to_excel(DATA_FILE, index=False)
    st.rerun()

# ==========================
# แสดงข้อมูลในรูปแบบตาราง
# ==========================
st.subheader("📋 ข้อมูลทั้งหมด")

if not df.empty:
    for i, row in df.iterrows():
        cols = st.columns([1, 2, 2, 2, 2, 2, 2])
        cols[0].write(f"**{i+1}**")
        cols[1].write(row["วันที่สั่งซื้อ"])
        cols[2].write(row["เลขที่ใบกำกับ"])
        cols[3].write(row["Seller"])
        cols[4].write(row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"])
        cols[5].write(row["หมายเหตุ"])
        edit_col, delete_col = cols[6].columns(2)
        if edit_col.button("✏️", key=f"edit_{i}"):
            st.session_state.edit_index = i
            st.rerun()
        if delete_col.button("🗑️", key=f"delete_{i}"):
            df = df.drop(i).reset_index(drop=True)
            df.to_excel(DATA_FILE, index=False)
            st.rerun()
else:
    st.info("ยังไม่มีข้อมูลในระบบ")

# ==========================
# ปุ่มดาวน์โหลด
# ==========================
st.subheader("⬇️ ดาวน์โหลดไฟล์ Excel")
buffer = BytesIO()
df.to_excel(buffer, index=False)
buffer.seek(0)
st.download_button(
    label="📥 ดาวน์โหลดไฟล์ Excel",
    data=buffer,
    file_name="sales_daily.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
