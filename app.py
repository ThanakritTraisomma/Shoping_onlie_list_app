import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="ใบกำกับลูกค้า", layout="wide")

st.title("📊 ระบบจัดการรายงานภาษีขายรายวัน")

# ========== ส่วนอัปโหลดไฟล์ ==========
uploaded_file = st.file_uploader("📁 อัปโหลดไฟล์ Excel (เลือกชีท: รายงานภาษีขายรายวัน)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="รายงานภาษีขายรายวัน")
    except Exception as e:
        st.error("❌ ไม่สามารถอ่านชีท 'รายงานภาษีขายรายวัน' ได้")
        st.stop()
else:
    st.warning("กรุณาอัปโหลดไฟล์ก่อน")
    st.stop()

# ตรวจสอบว่ามี session state หรือยัง
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# ==============================
# 🔧 ฟังก์ชันช่วย
# ==============================
def clear_form():
    st.session_state.edit_index = None
    st.rerun()

def save_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer


# ==============================
# 🧾 ฟอร์มกรอก/แก้ไขข้อมูล
# ==============================
st.subheader("🧾 ฟอร์มกรอกข้อมูล")

if st.session_state.edit_index is not None:
    edit_row = df.loc[st.session_state.edit_index]
    st.info(f"✏️ กำลังแก้ไขข้อมูลแถวที่ {st.session_state.edit_index + 1}")
else:
    edit_row = {col: "" for col in df.columns}

with st.form("sales_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ", value=pd.to_datetime(edit_row.get("วันที่สั่งซื้อ", pd.Timestamp.today())))
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=int(edit_row.get("ลำดับ", 1)) if str(edit_row.get("ลำดับ")).isdigit() else 1)
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", value=str(edit_row.get("เลขที่ใบกำกับ", "")))
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent", "อื่นๆ"], index=0)
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", value=str(edit_row.get("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "")))

    with col2:
        รหัส = st.text_input("รหัส", value=str(edit_row.get("รหัส", "")))
        สี = st.text_input("สี", value=str(edit_row.get("สี", "")))
        Size = st.text_input("Size", value=str(edit_row.get("Size", "")))
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=float(edit_row.get("ราคาขาย", 0)))
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=float(edit_row.get("ส่วนลด", 0)))
        สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=float(edit_row.get("สุทธิ", 0)))

    with col3:
        วดป = st.date_input("ว.ด.ป.", value=pd.to_datetime(edit_row.get("ว.ด.ป.", pd.Timestamp.today())))
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=float(edit_row.get("จำนวนเงิน", 0)))
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=float(edit_row.get("ค่าขนส่ง กทม.", 0)))
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=float(edit_row.get("ค่าขนส่ง ตจว.", 0)))
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", value=str(edit_row.get("เลขที่ใบโอน", "")))

    st.markdown("---")
    st.markdown("### 📝 หมายเหตุ")

    remark_options = ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"]
    current_remark = ""
    for opt in remark_options:
        if opt and opt in str(edit_row.get("หมายเหตุ", "")):
            current_remark = opt

    หมายเหตุหลัก = st.selectbox("เลือกหมายเหตุ", remark_options, index=remark_options.index(current_remark))
    รายละเอียดเพิ่มเติม = ""

    if หมายเหตุหลัก != "":
        รายละเอียดเพิ่มเติม = st.text_area("รายละเอียดเพิ่มเติม", value=str(edit_row.get("หมายเหตุ", "")) if "(" in str(edit_row.get("หมายเหตุ", "")) else "")

    หมายเหตุ = หมายเหตุหลัก
    if รายละเอียดเพิ่มเติม:
        หมายเหตุ += f" ({รายละเอียดเพิ่มเติม})"

    col_save, col_clear = st.columns(2)
    with col_save:
        submitted = st.form_submit_button("💾 บันทึกข้อมูล", use_container_width=True)
    with col_clear:
        clear = st.form_submit_button("🧹 ล้างฟอร์ม", use_container_width=True)

if clear:
    clear_form()

if submitted:
    new_data = {
        "วันที่สั่งซื้อ": วันที่สั่งซื้อ,
        "ลำดับ": ลำดับ,
        "เลขที่ใบกำกับ": เลขที่ใบกำกับ,
        "Seller": Seller,
        "เลขที่คำสั่งซื้อ/ชื่อลูกค้า": เลขที่คำสั่งซื้อชื่อลูกค้า,
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
        "หมายเหตุ": หมายเหตุ,
    }

    if st.session_state.edit_index is not None:
        df.iloc[st.session_state.edit_index] = new_data
        st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
        st.session_state.edit_index = None
    else:
        df.loc[len(df)] = new_data
        st.success("✅ เพิ่มข้อมูลใหม่เรียบร้อยแล้ว!")

# ==============================
# 📋 ตารางแสดงผล
# ==============================
st.subheader("📋 ตารางข้อมูลทั้งหมด")

edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

# ===== ปุ่มบันทึกเป็นไฟล์ =====
excel_data = save_excel(edited_df)
st.download_button(
    label="⬇️ ดาวน์โหลด Excel",
    data=excel_data,
    file_name="รายงานภาษีขายรายวัน_แก้ไข.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# ===== ปุ่มแก้ไขและลบ =====
st.markdown("### ✏️ แก้ไข / 🗑️ ลบข้อมูล")
for i, row in edited_df.iterrows():
    col_edit, col_delete = st.columns([1, 1])
    with col_edit:
        if st.button(f"✏️ แก้ไขแถวที่ {i+1}", key=f"edit_{i}"):
            st.session_state.edit_index = i
            st.rerun()
    with col_delete:
        if st.button(f"🗑️ ลบแถวที่ {i+1}", key=f"delete_{i}"):
            edited_df = edited_df.drop(i).reset_index(drop=True)
            st.success(f"ลบแถวที่ {i+1} แล้ว")
            excel_data = save_excel(edited_df)
            st.download_button(
                label="⬇️ ดาวน์โหลด Excel หลังลบ",
                data=excel_data,
                file_name="รายงานภาษีขายรายวัน_ลบแล้ว.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            st.stop()
