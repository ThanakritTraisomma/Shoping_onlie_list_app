import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ======================
# ตั้งค่าหน้าเว็บ
# ======================
st.set_page_config(page_title="ระบบบันทึกภาษีขายรายวัน", page_icon="📑", layout="wide")
st.title("📑 ระบบบันทึกข้อมูลรายงานภาษีขายรายวัน")

DATA_FILE = "sales_daily.xlsx"

# ======================
# สร้างคอลัมน์หลัก
# ======================
COLUMNS = [
    "วันที่สั่งซื้อ",
    "เลขที่คำสั่งซื้อ",
    "ชื่อลูกค้า",
    "ที่อยู่จัดส่ง",
    "เบอร์โทรศัพท์",
    "ยอดรวมสุทธิ",
    "ช่องทางการขาย",
    "ชื่อร้านค้า",
    "เลขที่ใบโอน",
    "หมายเหตุ",
]

# ======================
# โหลดไฟล์ / สร้างใหม่
# ======================
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_excel(DATA_FILE)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[COLUMNS]
    except Exception:
        df = pd.DataFrame(columns=COLUMNS)
else:
    df = pd.DataFrame(columns=COLUMNS)

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ======================
# ฟอร์มกรอกข้อมูล
# ======================
st.subheader("🧾 ฟอร์มกรอกข้อมูล")

with st.form("input_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        order_date = st.date_input("วันที่สั่งซื้อ", datetime.today())
        order_id = st.text_input("เลขที่คำสั่งซื้อ")
        customer_name = st.text_input("ชื่อลูกค้า")
        address = st.text_area("ที่อยู่จัดส่ง")

    with col2:
        phone = st.text_input("เบอร์โทรศัพท์")
        total_amount = st.number_input("ยอดรวมสุทธิ (บาท)", min_value=0.0, step=0.01)
        sale_channel = st.selectbox(
            "ช่องทางการขาย", ["Shopee", "Lazada", "Facebook", "Line", "อื่น ๆ"]
        )
        shop_name = st.text_input("ชื่อร้านค้า")

    with col3:
        transfer_id = st.text_input("เลขที่ใบโอน")
        remark_choice = st.selectbox(
            "หมายเหตุ", ["", "รอตรวจสอบ", "ชำระไม่ครบ", "ส่งไม่สำเร็จ", "อื่น ๆ"]
        )
        remark_text = ""
        if remark_choice != "":
            remark_text = st.text_area("รายละเอียดเพิ่มเติม")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

# ======================
# บันทึกข้อมูล
# ======================
if submitted:
    new_row = {
        "วันที่สั่งซื้อ": order_date,
        "เลขที่คำสั่งซื้อ": order_id,
        "ชื่อลูกค้า": customer_name,
        "ที่อยู่จัดส่ง": address,
        "เบอร์โทรศัพท์": phone,
        "ยอดรวมสุทธิ": total_amount,
        "ช่องทางการขาย": sale_channel,
        "ชื่อร้านค้า": shop_name,
        "เลขที่ใบโอน": transfer_id,
        "หมายเหตุ": f"{remark_choice} - {remark_text}" if remark_choice else "",
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
# แสดงข้อมูลในตาราง
# ======================
st.divider()
st.subheader("📋 ข้อมูลทั้งหมด")

if not df.empty:
    df = df.sort_values(by="วันที่สั่งซื้อ", ascending=True).reset_index(drop=True)

    # หัวตาราง
    st.write("### 🧮 ตารางข้อมูล")
    header_cols = st.columns([1.5, 2, 2, 2, 2, 1.5, 1.5, 2, 1.5, 2, 1])
    headers = [
        "วันที่สั่งซื้อ", "เลขที่คำสั่งซื้อ", "ชื่อลูกค้า", "ที่อยู่จัดส่ง",
        "เบอร์โทรศัพท์", "ยอดรวมสุทธิ", "ช่องทาง", "ร้านค้า", "ใบโอน", "หมายเหตุ", "จัดการ"
    ]
    for col, head in zip(header_cols, headers):
        col.markdown(f"**{head}**")

    for i, row in df.iterrows():
        cols = st.columns([1.5, 2, 2, 2, 2, 1.5, 1.5, 2, 1.5, 2, 1])

        cols[0].write(row["วันที่สั่งซื้อ"])
        cols[1].write(row["เลขที่คำสั่งซื้อ"])
        cols[2].write(row["ชื่อลูกค้า"])
        cols[3].write(row["ที่อยู่จัดส่ง"])
        cols[4].write(row["เบอร์โทรศัพท์"])

        # ✅ แก้จุดบั๊ก — format เฉพาะตัวเลข
        try:
            amount = float(row["ยอดรวมสุทธิ"])
            cols[5].write(f"{amount:,.2f}")
        except Exception:
            cols[5].write(row["ยอดรวมสุทธิ"])

        cols[6].write(row["ช่องทางการขาย"])
        cols[7].write(row["ชื่อร้านค้า"])
        cols[8].write(row["เลขที่ใบโอน"])
        cols[9].write(row.get("หมายเหตุ", ""))

        with cols[10]:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.experimental_rerun()
            if st.button("🗑️", key=f"delete_{i}"):
                df = df.drop(i).reset_index(drop=True)
                df.to_excel(DATA_FILE, index=False)
                st.experimental_rerun()
else:
    st.info("ยังไม่มีข้อมูลในระบบ")
