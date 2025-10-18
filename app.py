import streamlit as st
import pandas as pd
import os
from io import BytesIO

# ==========================
# ตั้งค่าหน้าเว็บ
# ==========================
st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")
st.title("📑 ระบบรายงานภาษีขายรายวัน")

DATA_FILE = "sales_daily.xlsx"

COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน", "หมายเหตุ"
]

# ==========================
# โหลดข้อมูล (หรือสร้างใหม่)
# ==========================
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_excel(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=COLUMNS)
else:
    df = pd.DataFrame(columns=COLUMNS)

for col in COLUMNS:
    if col not in df.columns:
        df[col] = ""

# ==========================
# เก็บ index ที่กำลังแก้ไขใน session
# ==========================
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ==========================
# ฟอร์มกรอก / แก้ไขข้อมูล
# ==========================
st.subheader("🧾 กรอกหรือแก้ไขข้อมูล")

edit_mode = st.session_state.edit_index is not None
form_title = "✏️ แก้ไขข้อมูล" if edit_mode else "➕ เพิ่มข้อมูลใหม่"
st.markdown(f"### {form_title}")

if edit_mode:
    row = df.iloc[st.session_state.edit_index]
else:
    row = {col: "" for col in COLUMNS}

with st.form("sales_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ", pd.to_datetime(row["วันที่สั่งซื้อ"]) if row["วันที่สั่งซื้อ"] else None)
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=int(row["ลำดับ"]) if str(row["ลำดับ"]).isdigit() else 1)
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", row["เลขที่ใบกำกับ"])
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent", "อื่นๆ"], index=0 if row["Seller"] == "" else ["shopee", "lazada", "cent", "อื่นๆ"].index(row["Seller"]))
        เลขที่คำสั่งซื้อ = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"])

    with col2:
        รหัส = st.text_input("รหัส", row["รหัส"])
        สี = st.text_input("สี", row["สี"])
        Size = st.text_input("Size", row["Size"])
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=float(row["ราคาขาย"]) if row["ราคาขาย"] else 0.0)
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=float(row["ส่วนลด"]) if row["ส่วนลด"] else 0.0)
        สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=float(row["สุทธิ"]) if row["สุทธิ"] else 0.0)

    with col3:
        วดป = st.date_input("ว.ด.ป.", pd.to_datetime(row["ว.ด.ป."]) if row["ว.ด.ป."] else None)
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=float(row["จำนวนเงิน"]) if row["จำนวนเงิน"] else 0.0)
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=float(row["ค่าขนส่ง กทม."]) if row["ค่าขนส่ง กทม."] else 0.0)
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=float(row["ค่าขนส่ง ตจว."]) if row["ค่าขนส่ง ตจว."] else 0.0)
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", row["เลขที่ใบโอน"])

    st.markdown("### 📝 หมายเหตุ")
    หมายเหตุตัวเลือก = st.selectbox("เลือกหมายเหตุ", ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"], index=0 if not row["หมายเหตุ"] else
        ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"].index(row["หมายเหตุ"].split(" - ")[0] if " - " in row["หมายเหตุ"] else row["หมายเหตุ"]))
    หมายเหตุข้อความ = ""
    if หมายเหตุตัวเลือก:
        หมายเหตุข้อความ = st.text_area("รายละเอียดเพิ่มเติม", row["หมายเหตุ"].split(" - ")[1] if " - " in row["หมายเหตุ"] else "")

    submitted = st.form_submit_button("💾 บันทึก")
    cancelled = st.form_submit_button("❌ ยกเลิก")

if submitted:
    new_row = {
        "วันที่สั่งซื้อ": วันที่สั่งซื้อ,
        "ลำดับ": ลำดับ,
        "เลขที่ใบกำกับ": เลขที่ใบกำกับ,
        "Seller": Seller,
        "เลขที่คำสั่งซื้อ/ชื่อลูกค้า": เลขที่คำสั่งซื้อ,
        "รหัส": รหัส,
        "สี": สี,
        "Size": Size,
        "ราคาขาย": ราคาขาย,
        "ส่วนลด": ส่วนลด,
        "สุทธิ": สุทธิ,
        "ว.ด.ป.": วดป,
        "จำนวนเงิน": จำนวนเงิน,
        "ค่าขนส่ง กทม.": ค่าขนส่งกทม,
        "ค่าขนส่ง ตจว.": ค่าขนส่งตจว,
        "เลขที่ใบโอน": เลขที่ใบโอน,
        "หมายเหตุ": f"{หมายเหตุตัวเลือก} - {หมายเหตุข้อความ}" if หมายเหตุตัวเลือก else ""
    }

    if edit_mode:
        df.iloc[st.session_state.edit_index] = new_row
        st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
        st.session_state.edit_index = None
    else:
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.success("✅ เพิ่มข้อมูลเรียบร้อยแล้ว!")

    df.sort_values(by="วันที่สั่งซื้อ", ascending=True, inplace=True)
    df.to_excel(DATA_FILE, index=False)
    st.experimental_rerun()

if cancelled:
    st.session_state.edit_index = None
    st.experimental_rerun()

# ==========================
# ตารางข้อมูล (อ่านอย่างเดียว)
# ==========================
st.subheader("📋 ข้อมูลทั้งหมด")

if len(df) > 0:
    for i, row in df.iterrows():
        with st.container(border=True):
            cols = st.columns([2, 3, 2, 2, 3, 2, 1])
            cols[0].write(f"📅 วันที่สั่งซื้อ: {row['วันที่สั่งซื้อ']}")
            cols[1].write(f"💬 คำสั่งซื้อ: {row['เลขที่คำสั่งซื้อ/ชื่อลูกค้า']}")
            cols[2].write(f"🧾 ใบกำกับ: {row['เลขที่ใบกำกับ']}")
            cols[3].write(f"💸 สุทธิ: {row['สุทธิ']}")
            cols[4].write(f"🏷️ หมายเหตุ: {row['หมายเหตุ']}")
            if cols[5].button("✏️ แก้ไข", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.experimental_rerun()
            if cols[6].button("🗑️ ลบ", key=f"delete_{i}"):
                df = df.drop(i).reset_index(drop=True)
                df.to_excel(DATA_FILE, index=False)
                st.experimental_rerun()
else:
    st.info("ยังไม่มีข้อมูลในระบบ")

# ==========================
# ดาวน์โหลดไฟล์
# ==========================
st.download_button(
    label="📥 ดาวน์โหลด Excel",
    data=df.to_excel(index=False, engine="openpyxl"),
    file_name="sales_daily.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
