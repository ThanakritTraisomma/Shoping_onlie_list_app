from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")
st.title("📊 รายงานภาษีขายรายวัน (เวอร์ชัน AgGrid)")

DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน", "หมายเหตุ"
]

# โหลดข้อมูล
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
else:
    df = pd.DataFrame(columns=COLUMNS)

st.write("🧾 กรอกข้อมูลใหม่")

# ---- ฟอร์มกรอก ----
with st.form("form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ")
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1)
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ")
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent"])
        เลขที่คำสั่งซื้อ = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า")
    with col2:
        รหัส = st.text_input("รหัส")
        สี = st.text_input("สี")
        Size = st.text_input("Size")
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0)
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0)
        สุทธิ = st.number_input("สุทธิ", min_value=0.0)
    with col3:
        วดป = st.date_input("ว.ด.ป.")
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0)
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0)
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0)
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน")
        หมายเหตุ = st.text_input("หมายเหตุ")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

if submitted:
    new_row = pd.DataFrame([[
        วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อ, รหัส, สี, Size,
        ราคาขาย, ส่วนลด, สุทธิ, วดป, จำนวนเงิน,
        ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน, หมายเหตุ
    ]], columns=COLUMNS)

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)
    st.success("✅ บันทึกเรียบร้อย!")

# ---- แสดงตารางแบบ AgGrid ----
st.subheader("📋 ข้อมูลทั้งหมด")

gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_default_column(editable=False, groupable=True)
gb.configure_selection(selection_mode="single", use_checkbox=True)
grid_options = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme="balham",
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
)

selected = grid_response["selected_rows"]

if selected:
    st.info(f"คุณเลือกแถว: {selected[0].get('เลขที่ใบกำกับ', '')}")
    if st.button("✏️ แก้ไขข้อมูลที่เลือก"):
        st.session_state.edit_data = selected[0]
        st.rerun()
    if st.button("🗑️ ลบข้อมูลที่เลือก"):
        df = df[df["เลขที่ใบกำกับ"] != selected[0]["เลขที่ใบกำกับ"]]
        df.to_excel(DATA_FILE, index=False)
        st.success("✅ ลบข้อมูลเรียบร้อยแล้ว!")
        st.rerun()
