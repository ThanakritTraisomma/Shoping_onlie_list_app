import streamlit as st
import pandas as pd
from io import BytesIO

# ==========================
# 🧭 ตั้งค่าหน้าเว็บ
# ==========================
st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")

st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")

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
try:
    df = pd.read_excel(DATA_FILE)
except Exception:
    df = pd.DataFrame(columns=COLUMNS)

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ==========================
# 🧾 ฟอร์มกรอกข้อมูล
# ==========================
st.subheader("🧾 ฟอร์มกรอกข้อมูล")

if st.session_state.edit_index is not None:
    st.info(f"✏️ กำลังแก้ไขแถวที่ {st.session_state.edit_index + 1}")
    edit_data = df.iloc[st.session_state.edit_index].to_dict()
else:
    edit_data = {c: "" for c in COLUMNS}

with st.form("sales_form", clear_on_submit=st.session_state.edit_index is None):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ")
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=int(edit_data.get("ลำดับ") or 1))
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", edit_data.get("เลขที่ใบกำกับ"))
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent", "อื่นๆ"], index=0)
        เลขที่คำสั่งซื้อ = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", edit_data.get("เลขที่คำสั่งซื้อ/ชื่อลูกค้า"))

    with col2:
        รหัส = st.text_input("รหัส", edit_data.get("รหัส"))
        สี = st.text_input("สี", edit_data.get("สี"))
        Size = st.text_input("Size", edit_data.get("Size"))
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=float(edit_data.get("ราคาขาย") or 0))
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=float(edit_data.get("ส่วนลด") or 0))
        สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=float(edit_data.get("สุทธิ") or 0))

    with col3:
        วดป = st.date_input("ว.ด.ป.")
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=float(edit_data.get("จำนวนเงิน") or 0))
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=float(edit_data.get("ค่าขนส่ง กทม.") or 0))
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=float(edit_data.get("ค่าขนส่ง ตจว.") or 0))
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", edit_data.get("เลขที่ใบโอน"))

    st.markdown("### 📝 หมายเหตุ")
    หมายเหตุตัวเลือก = st.selectbox("เลือกหมายเหตุ", ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"])
    หมายเหตุข้อความ = ""
    if หมายเหตุตัวเลือก:
        หมายเหตุข้อความ = st.text_area("รายละเอียดเพิ่มเติม", edit_data.get("หมายเหตุ"))

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

if submitted:
    new_data = pd.DataFrame([[
        วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller, เลขที่คำสั่งซื้อ,
        รหัส, สี, Size, ราคาขาย, ส่วนลด, สุทธิ, วดป, จำนวนเงิน,
        ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน,
        f"{หมายเหตุตัวเลือก} - {หมายเหตุข้อความ}" if หมายเหตุตัวเลือก else ""
    ]], columns=COLUMNS)

    if st.session_state.edit_index is not None:
        df.iloc[st.session_state.edit_index] = new_data.iloc[0]
        st.session_state.edit_index = None
        st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
    else:
        df = pd.concat([df, new_data], ignore_index=True)
        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

    df.sort_values(by="วันที่สั่งซื้อ", ascending=True, inplace=True)
    df.to_excel(DATA_FILE, index=False)

# ==========================
# 📋 ตารางแสดงข้อมูล
# ==========================
st.subheader("📋 ข้อมูลทั้งหมด")

if len(df) > 0:
    for i, row in df.iterrows():
        with st.container():
            cols = st.columns([6, 1, 1])
            with cols[0]:
                st.write(f"**{i+1}.** วันที่: {row['วันที่สั่งซื้อ']} | เลขที่ใบกำกับ: {row['เลขที่ใบกำกับ']} | ลูกค้า: {row['เลขที่คำสั่งซื้อ/ชื่อลูกค้า']} | ยอดสุทธิ: {row['สุทธิ']}")
                st.write(f"📦 หมายเหตุ: {row['หมายเหตุ']}")
            with cols[1]:
                if st.button("✏️ แก้ไข", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.experimental_rerun()
            with cols[2]:
                if st.button("🗑️ ลบ", key=f"delete_{i}"):
                    df = df.drop(i).reset_index(drop=True)
                    df.to_excel(DATA_FILE, index=False)
                    st.success(f"🗑️ ลบแถวที่ {i+1} เรียบร้อยแล้ว!")
                    st.experimental_rerun()
else:
    st.info("ยังไม่มีข้อมูล กรุณากรอกใหม่ด้านบน")

# ==========================
# 📥 ดาวน์โหลด
# ==========================
st.download_button(
    label="📥 ดาวน์โหลดไฟล์ Excel",
    data=BytesIO(df.to_excel(index=False, engine="openpyxl")),
    file_name="sales_daily.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
