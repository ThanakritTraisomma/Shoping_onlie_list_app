import streamlit as st
import pandas as pd
import os
from io import BytesIO

# ==========================
# 🧭 ตั้งค่าหน้าเว็บ
# ==========================
st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")

st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")
st.write("กรอกข้อมูล, อัปโหลดไฟล์เดิม หรือดาวน์โหลดข้อมูลที่กรอกไว้")

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
try:
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=COLUMNS)
except Exception:
    st.warning("⚠️ ไม่สามารถอ่านไฟล์ Excel เดิมได้ (ไฟล์อาจเสียหรือไม่ใช่ .xlsx)")
    df = pd.DataFrame(columns=COLUMNS)

# ==========================
# 📤 อัปโหลดไฟล์ Excel เดิม
# ==========================
st.subheader("📤 อัปโหลดไฟล์ Excel เดิม (ถ้ามี)")
uploaded = st.file_uploader("เลือกไฟล์ Excel เพื่อโหลดข้อมูลเก่าหรือรวมข้อมูลใหม่", type=["xlsx"])

if uploaded:
    try:
        xls = pd.ExcelFile(uploaded)
        target_sheet = next((s for s in xls.sheet_names if "รายงานภาษีขายรายวัน" in s), None)

        if target_sheet:
            new_df = pd.read_excel(xls, sheet_name=target_sheet)
            st.success(f"✅ โหลดข้อมูลจากชีต '{target_sheet}' เรียบร้อยแล้ว!")
        else:
            sheet_name = st.selectbox("เลือกชีตที่ต้องการดู", xls.sheet_names)
            new_df = pd.read_excel(xls, sheet_name=sheet_name)
            st.warning("⚠️ ไม่พบชีต 'รายงานภาษีขายรายวัน' ในไฟล์ที่อัปโหลด")

        if set(COLUMNS).issubset(set(new_df.columns)):
            new_df = new_df[COLUMNS]
            before = len(df)
            df = pd.concat([df, new_df], ignore_index=True)
            df.drop_duplicates(subset=["เลขที่ใบกำกับ", "เลขที่คำสั่งซื้อ/ชื่อลูกค้า"], inplace=True)
            df.to_excel(DATA_FILE, index=False)
            st.success(f"🔄 รวมข้อมูลเรียบร้อยแล้ว! (เพิ่มใหม่ {len(df)-before} รายการ)")
        else:
            st.error("❌ คอลัมน์ในไฟล์ไม่ตรงกับที่กำหนดไว้")

    except Exception as e:
        st.error(f"❌ ไม่สามารถอ่านไฟล์ Excel ได้: {e}")

# ==========================
# 🔁 จัดการ session สำหรับแก้ไข
# ==========================
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ==========================
# 🧾 ฟอร์มกรอกข้อมูล
# ==========================
st.subheader("🧾 กรอกข้อมูลใหม่")

def clear_form():
    st.session_state.clear()

with st.form("sales_form"):
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
    st.markdown("### 📝 หมายเหตุ")

    คืนสินค้า = st.checkbox("คืนสินค้า")
    พัสดุตีกลับ = st.checkbox("พัสดุตีกลับ")
    ยกเลิกออเดอร์ = st.checkbox("ยกเลิกออเดอร์")
    อื่นๆ = st.checkbox("อื่นๆ")

    remark_list = []
    show_text_box = any([คืนสินค้า, พัสดุตีกลับ, ยกเลิกออเดอร์, อื่นๆ])

    if show_text_box:
        รายละเอียดเพิ่มเติม = st.text_area("รายละเอียดเพิ่มเติม")
    else:
        รายละเอียดเพิ่มเติม = ""

    if คืนสินค้า: remark_list.append("คืนสินค้า")
    if พัสดุตีกลับ: remark_list.append("พัสดุตีกลับ")
    if ยกเลิกออเดอร์: remark_list.append("ยกเลิกออเดอร์")
    if อื่นๆ: remark_list.append("อื่นๆ")

    หมายเหตุ = ", ".join(remark_list)
    if รายละเอียดเพิ่มเติม:
        หมายเหตุ += f" ({รายละเอียดเพิ่มเติม})"

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

if submitted:
    new_data = pd.DataFrame([[
        วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size,
        ราคาขาย, ส่วนลด, สุทธิ, วดป, จำนวนเงิน,
        ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน, หมายเหตุ
    ]], columns=COLUMNS)

    if st.session_state.edit_index is not None:
        for col in COLUMNS:
            df.at[st.session_state.edit_index, col] = new_data.iloc[0][col]
        st.session_state.edit_index = None
        st.success("✏️ แก้ไขข้อมูลเรียบร้อยแล้ว!")
    else:
        df = pd.concat([df, new_data], ignore_index=True)
        st.success("✅ เพิ่มข้อมูลเรียบร้อยแล้ว!")

    df.sort_values(by="วันที่สั่งซื้อ", inplace=True)
    df.to_excel(DATA_FILE, index=False)
    st.rerun()

# ==========================
# 📋 แสดงข้อมูล + ปุ่มแก้ไข
# ==========================
st.subheader("📋 ข้อมูลที่มีอยู่แล้ว")

if not df.empty:
    df = df.sort_values(by="วันที่สั่งซื้อ", ascending=True).reset_index(drop=True)

    for i, row in df.iterrows():
        with st.expander(f"{i+1}. {row['เลขที่ใบกำกับ']} - {row['เลขที่คำสั่งซื้อ/ชื่อลูกค้า']}"):
            st.write(row.to_dict())
            if st.button(f"✏️ แก้ไขแถว {i+1}", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.rerun()
else:
    st.info("ยังไม่มีข้อมูล")

# ==========================
# ⬇️ ดาวน์โหลด Excel
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
