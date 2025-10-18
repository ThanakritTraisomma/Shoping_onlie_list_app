import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import date

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")
st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")
st.write("กรอกข้อมูล, อัปโหลดไฟล์เดิม หรือดาวน์โหลดข้อมูลที่กรอกไว้")

DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน", "หมายเหตุ"
]

# โหลดข้อมูล
try:
    if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=COLUMNS)
except Exception:
    st.warning("⚠️ ไม่สามารถอ่านไฟล์ Excel เดิมได้")
    df = pd.DataFrame(columns=COLUMNS)

# ==========================
# 📤 อัปโหลดไฟล์ Excel เดิม
# ==========================
st.subheader("📤 อัปโหลดไฟล์ Excel เดิม (ถ้ามี)")
uploaded = st.file_uploader("เลือกไฟล์ Excel", type=["xlsx"])

if uploaded:
    try:
        xls = pd.ExcelFile(uploaded)
        target_sheet = None
        for name in xls.sheet_names:
            if "รายงานภาษีขายรายวัน" in name:
                target_sheet = name
                break

        if target_sheet:
            new_df = pd.read_excel(xls, sheet_name=target_sheet)
        else:
            sheet_name = st.selectbox("เลือกชีต", xls.sheet_names)
            new_df = pd.read_excel(xls, sheet_name=sheet_name)

        if set(COLUMNS).issubset(set(new_df.columns)):
            new_df = new_df[COLUMNS]
            before = len(df)
            df = pd.concat([df, new_df], ignore_index=True)
            df.drop_duplicates(subset=["เลขที่ใบกำกับ", "เลขที่คำสั่งซื้อ/ชื่อลูกค้า"], inplace=True)
            df.sort_values(by="วันที่สั่งซื้อ", ascending=True, inplace=True)
            df.to_excel(DATA_FILE, index=False)
            st.success(f"✅ รวมข้อมูลเรียบร้อยแล้ว ({len(df)-before} แถวใหม่)")
        else:
            st.error("❌ คอลัมน์ไม่ตรง")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")

# ==========================
# 🧾 ฟอร์มกรอกข้อมูลใหม่
# ==========================
st.subheader("🧾 กรอกข้อมูลใหม่หรือแก้ไข")

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# โหลดข้อมูลเดิมถ้าอยู่ในโหมดแก้ไข
edit_data = df.iloc[st.session_state.edit_index].to_dict() if st.session_state.edit_index is not None else {}

with st.form("sales_form", clear_on_submit=(st.session_state.edit_index is None)):
    col1, col2, col3 = st.columns(3)
    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ", value=edit_data.get("วันที่สั่งซื้อ", date.today()))
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=int(edit_data.get("ลำดับ", 1)))
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", value=edit_data.get("เลขที่ใบกำกับ", ""))
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent", "อื่นๆ"], index=0)
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", value=edit_data.get("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", ""))

    with col2:
        รหัส = st.text_input("รหัส", value=edit_data.get("รหัส", ""))
        สี = st.text_input("สี", value=edit_data.get("สี", ""))
        Size = st.text_input("Size", value=edit_data.get("Size", ""))
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=float(edit_data.get("ราคาขาย", 0)))
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=float(edit_data.get("ส่วนลด", 0)))
        สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=float(edit_data.get("สุทธิ", 0)))

    with col3:
        วดป = st.date_input("ว.ด.ป.", value=edit_data.get("ว.ด.ป.", date.today()))
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=float(edit_data.get("จำนวนเงิน", 0)))
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=float(edit_data.get("ค่าขนส่ง กทม.", 0)))
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=float(edit_data.get("ค่าขนส่ง ตจว.", 0)))
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", value=edit_data.get("เลขที่ใบโอน", ""))

    st.markdown("### 📝 หมายเหตุ")
    col_note1, col_note2, col_note3, col_note4 = st.columns(4)
    คืนสินค้า = col_note1.checkbox("คืนสินค้า")
    พัสดุตีกลับ = col_note2.checkbox("พัสดุตีกลับ")
    ยกเลิกออเดอร์ = col_note3.checkbox("ยกเลิกออเดอร์")
    อื่นๆ = col_note4.checkbox("อื่นๆ")

    หมายเหตุ = ""
    if any([คืนสินค้า, พัสดุตีกลับ, ยกเลิกออเดอร์, อื่นๆ]):
        หมายเหตุ_คืนสินค้า = st.text_input("รายละเอียดคืนสินค้า") if คืนสินค้า else ""
        หมายเหตุ_พัสดุตีกลับ = st.text_input("รายละเอียดพัสดุตีกลับ") if พัสดุตีกลับ else ""
        หมายเหตุ_ยกเลิกออเดอร์ = st.text_input("รายละเอียดยกเลิกออเดอร์") if ยกเลิกออเดอร์ else ""
        หมายเหตุ_อื่นๆ = st.text_input("รายละเอียดอื่นๆ") if อื่นๆ else ""
        หมายเหตุ = " | ".join(
            [x for x in [
                หมายเหตุ_คืนสินค้า, หมายเหตุ_พัสดุตีกลับ, หมายเหตุ_ยกเลิกออเดอร์, หมายเหตุ_อื่นๆ
            ] if x]
        )

    submitted = st.form_submit_button("💾 บันทึก")

if submitted:
    new_data = pd.DataFrame([[
        วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size,
        ราคาขาย, ส่วนลด, สุทธิ, วดป, จำนวนเงิน,
        ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน, หมายเหตุ
    ]], columns=COLUMNS)

    if st.session_state.edit_index is not None:
        df.iloc[st.session_state.edit_index] = new_data.iloc[0]
        st.session_state.edit_index = None
        st.success("✏️ แก้ไขข้อมูลเรียบร้อยแล้ว!")
    else:
        df = pd.concat([df, new_data], ignore_index=True)
        st.success("✅ เพิ่มข้อมูลเรียบร้อยแล้ว!")

    df.sort_values(by="วันที่สั่งซื้อ", ascending=True, inplace=True)
    df.to_excel(DATA_FILE, index=False)
    st.rerun()

# ==========================
# 📋 ตารางข้อมูล (พร้อมปุ่มแก้ไข)
# ==========================
st.subheader("📋 ข้อมูลที่มีอยู่แล้ว")
df_sorted = df.sort_values(by="วันที่สั่งซื้อ", ascending=True).reset_index(drop=True)
for i, row in df_sorted.iterrows():
    with st.expander(f"{row['วันที่สั่งซื้อ']} | {row['เลขที่ใบกำกับ']} | {row['เลขที่คำสั่งซื้อ/ชื่อลูกค้า']}"):
        st.write(row)
        if st.button("✏️ แก้ไขแถวนี้", key=f"edit_{i}"):
            st.session_state.edit_index = i
            st.rerun()

# ==========================
# ⬇️ ดาวน์โหลดไฟล์
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
