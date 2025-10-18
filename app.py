import streamlit as st
import pandas as pd
import os
from io import BytesIO

# ==========================
# 🧭 ตั้งค่าหน้าเว็บ
# ==========================
st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")

st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")
st.write("กรอกข้อมูล แล้วดูผลลัพธ์เป็นตารางได้ทันที")

# ==========================
# 🔧 ค่าพื้นฐาน
# ==========================
DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน", "หมายเหตุ"
]

# ==========================
# 📂 โหลดข้อมูลเดิม
# ==========================
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
else:
    df = pd.DataFrame(columns=COLUMNS)

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ==========================
# 🧾 ฟอร์มกรอกข้อมูล
# ==========================
st.subheader("🧾 ฟอร์มกรอกข้อมูล")

if st.session_state.edit_index is not None:
    st.info(f"✏️ กำลังแก้ไขแถวที่ {st.session_state.edit_index + 1}")
    edit_row = df.loc[st.session_state.edit_index]
else:
    edit_row = {col: "" for col in COLUMNS}

with st.form("sales_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ", value=pd.to_datetime(edit_row["วันที่สั่งซื้อ"]) if edit_row["วันที่สั่งซื้อ"] else pd.to_datetime("today"))
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=int(edit_row["ลำดับ"]) if str(edit_row["ลำดับ"]).isdigit() else 1)
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", value=str(edit_row["เลขที่ใบกำกับ"]))
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent", "อื่นๆ"], index=0 if edit_row["Seller"] == "" else ["shopee", "lazada", "cent", "อื่นๆ"].index(edit_row["Seller"]))
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", value=str(edit_row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"]))

    with col2:
        รหัส = st.text_input("รหัส", value=str(edit_row["รหัส"]))
        สี = st.text_input("สี", value=str(edit_row["สี"]))
        Size = st.text_input("Size", value=str(edit_row["Size"]))
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=float(edit_row["ราคาขาย"]) if str(edit_row["ราคาขาย"]).replace('.', '', 1).isdigit() else 0.0)
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=float(edit_row["ส่วนลด"]) if str(edit_row["ส่วนลด"]).replace('.', '', 1).isdigit() else 0.0)
        สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=float(edit_row["สุทธิ"]) if str(edit_row["สุทธิ"]).replace('.', '', 1).isdigit() else 0.0)

    with col3:
        วดป = st.date_input("ว.ด.ป.", value=pd.to_datetime(edit_row["ว.ด.ป."]) if edit_row["ว.ด.ป."] else pd.to_datetime("today"))
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=float(edit_row["จำนวนเงิน"]) if str(edit_row["จำนวนเงิน"]).replace('.', '', 1).isdigit() else 0.0)
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=float(edit_row["ค่าขนส่ง กทม."]) if str(edit_row["ค่าขนส่ง กทม."]).replace('.', '', 1).isdigit() else 0.0)
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=float(edit_row["ค่าขนส่ง ตจว."]) if str(edit_row["ค่าขนส่ง ตจว."]).replace('.', '', 1).isdigit() else 0.0)
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", value=str(edit_row["เลขที่ใบโอน"]))

    st.markdown("---")

    # 🔽 หมายเหตุ (Dropdown + Text Input)
    หมายเหตุตัวเลือก = st.selectbox(
        "หมายเหตุ",
        ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"],
        index=["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"].index(str(edit_row["หมายเหตุ"]).split(":", 1)[0]) if edit_row["หมายเหตุ"] else 0
    )

    รายละเอียดเพิ่มเติม = ""
    if หมายเหตุตัวเลือก != "":
        รายละเอียดเพิ่มเติม = st.text_input("รายละเอียดเพิ่มเติม", value=str(edit_row["หมายเหตุ"]).split(":", 1)[1] if ":" in str(edit_row["หมายเหตุ"]) else "")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")
    cancelled = st.form_submit_button("❌ ยกเลิก")

if submitted:
    หมายเหตุรวม = f"{หมายเหตุตัวเลือก}: {รายละเอียดเพิ่มเติม}" if หมายเหตุตัวเลือก else ""
    new_data = pd.DataFrame([[
        วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size,
        ราคาขาย, ส่วนลด, สุทธิ, วดป, จำนวนเงิน,
        ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน, หมายเหตุรวม
    ]], columns=COLUMNS)

    if st.session_state.edit_index is not None:
        df.iloc[st.session_state.edit_index] = new_data.iloc[0]
        st.session_state.edit_index = None
        st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
    else:
        df = pd.concat([df, new_data], ignore_index=True)
        st.success("✅ เพิ่มข้อมูลเรียบร้อยแล้ว!")

    df = df.sort_values(by="วันที่สั่งซื้อ", ascending=True)
    df.to_excel(DATA_FILE, index=False)
    st.rerun()

if cancelled:
    st.session_state.edit_index = None
    st.rerun()

# ==========================
# 📋 แสดงข้อมูลแบบตาราง
# ==========================
st.subheader("📋 ข้อมูลทั้งหมด")

if len(df) == 0:
    st.info("ยังไม่มีข้อมูลในระบบ")
else:
    for i, row in df.iterrows():
        cols = st.columns([2, 3, 2, 3, 2, 1, 1])
        cols[0].write(row["วันที่สั่งซื้อ"])
        cols[1].write(row["เลขที่ใบกำกับ"])
        cols[2].write(row["Seller"])
        cols[3].write(row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"])
        cols[4].write(row["สุทธิ"])
        cols[5].write(row["หมายเหตุ"])

        edit_col, delete_col = st.columns([1, 1])
        if edit_col.button("✏️ แก้ไข", key=f"edit_{i}"):
            st.session_state.edit_index = i
            st.rerun()
        if delete_col.button("🗑️ ลบ", key=f"delete_{i}"):
            df = df.drop(i).reset_index(drop=True)
            df.to_excel(DATA_FILE, index=False)
            st.success("🗑️ ลบข้อมูลเรียบร้อยแล้ว!")
            st.rerun()

# ==========================
# ⬇️ ดาวน์โหลดไฟล์ Excel
# ==========================
st.subheader("⬇️ ดาวน์โหลดข้อมูลทั้งหมด")
buffer = BytesIO()
df.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    label="📥 ดาวน์โหลดไฟล์ Excel",
    data=buffer,
    file_name="sales_daily.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
