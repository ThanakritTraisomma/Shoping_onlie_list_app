import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")

st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")
st.write("กรอกข้อมูล, อัปโหลดไฟล์เดิม หรือดาวน์โหลดข้อมูลที่กรอกไว้")

# ------------------------------
# ค่าพื้นฐาน
DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน"
]
# ------------------------------

# โหลดข้อมูลเดิม
# โหลดข้อมูลเดิม (พร้อมกัน error BadZipFile)
try:
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=COLUMNS)
except Exception as e:
    st.warning("⚠️ ไม่สามารถอ่านไฟล์ Excel เดิมได้ (ไฟล์อาจเสียหรือไม่ใช่ .xlsx)")
    df = pd.DataFrame(columns=COLUMNS)


# ===== ส่วนที่ 1: อัปโหลดไฟล์เดิม =====
st.subheader("📤 อัปโหลดไฟล์ Excel เดิม (ถ้ามี)")
uploaded = st.file_uploader("เลือกไฟล์ Excel เพื่อโหลดข้อมูลเก่า", type=["xlsx"])
if uploaded:
    xls = pd.ExcelFile(uploaded)
    
    # ถ้ามีชีตชื่อ "รายงานภาษีขายรายวัน" ให้เลือกอัตโนมัติ
    target_sheet = None
    for name in xls.sheet_names:
        if "รายงานภาษีขายรายวัน" in name:
            target_sheet = name
            break

    if target_sheet:
        df = pd.read_excel(xls, sheet_name=target_sheet)
        st.success(f"✅ โหลดข้อมูลจากชีต '{target_sheet}' เรียบร้อยแล้ว!")
    else:
        sheet_name = st.selectbox("เลือกชีตที่ต้องการดู", xls.sheet_names)
        df = pd.read_excel(xls, sheet_name=sheet_name)
        st.warning("⚠️ ไม่พบชีต 'รายงานภาษีขายรายวัน' ในไฟล์ที่อัปโหลด จึงโหลดชีตที่เลือกแทน")


# ===== ส่วนที่ 2: ฟอร์มกรอกข้อมูลใหม่ =====
st.subheader("🧾 กรอกข้อมูลใหม่")
with st.form("sales_form"):
    col1, col2, col3 = st.columns(3)

    # ----------- คอลัมน์ 1 -----------
    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ")
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1)
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ")
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent"])
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า")

    # ----------- คอลัมน์ 2 -----------
    with col2:
        # หัวข้อใหญ่: รายละเอียดสินค้า
        st.markdown("### 🛍️ รายละเอียดสินค้า")
        รหัส = st.text_input("รหัส")
        สี = st.text_input("สี")
        Size = st.text_input("Size")

        st.markdown("---")  # เส้นคั่น

        # หัวข้อใหญ่: รายละเอียดการขาย
        st.markdown("### 💰 รายละเอียดการขาย")
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0)
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0)
        สุทธิ = st.number_input("สุทธิ", min_value=0.0)

    # ----------- คอลัมน์ 3 -----------
    with col3:
        st.markdown("### 📦 การชำระเงินและขนส่ง")
        วดป = st.date_input("ว.ด.ป.")
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0)
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0)
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0)
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

if submitted:
    new_data = pd.DataFrame([[
        วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size,
        ราคาขาย, ส่วนลด, สุทธิ, วดป, จำนวนเงิน,
        ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน
    ]], columns=COLUMNS)

    df = pd.concat([df, new_data], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)
    st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

# ===== ส่วนที่ 3: แสดงข้อมูล =====
st.subheader("📋 ข้อมูลที่มีอยู่แล้ว")
edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
if st.button("💾 บันทึกการแก้ไขทั้งหมด"):
    edited_df.to_excel(DATA_FILE, index=False)
    st.success("✅ บันทึกการแก้ไขเรียบร้อยแล้ว!")

# ===== ส่วนที่ 4: ดาวน์โหลดข้อมูล =====
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





