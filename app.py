import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")
st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")

DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน"
]

# โหลดข้อมูล
if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
    df = pd.read_excel(DATA_FILE)
else:
    df = pd.DataFrame(columns=COLUMNS)

# --- ฟังก์ชันบันทึกไฟล์ ---
def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# ==============================
# 📋 ตารางข้อมูลหลัก (AgGrid)
# ==============================
st.subheader("📋 ข้อมูลทั้งหมด")

if df.empty:
    st.info("ยังไม่มีข้อมูล กรุณากรอกข้อมูลใหม่")
else:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_default_column(editable=False, groupable=False, wrapText=True, autoHeight=True)
    gb.configure_selection("single", use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        theme="alpine",
        height=400,
        allow_unsafe_jscode=True,
    )

    selected = grid_response["selected_rows"]

    st.markdown("---")

    # ปุ่มสำหรับแถวที่เลือก
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        add_btn = st.button("➕ เพิ่มข้อมูลใหม่")
    with col2:
        edit_btn = st.button("✏️ แก้ไขแถวที่เลือก")
    with col3:
        delete_btn = st.button("🗑️ ลบแถวที่เลือก")

    # เพิ่มข้อมูลใหม่
    if add_btn:
        st.session_state["edit_mode"] = "add"
        st.session_state["selected_row"] = None
        st.rerun()

    # แก้ไขข้อมูล
    if edit_btn:
        if selected:
            st.session_state["edit_mode"] = "edit"
            st.session_state["selected_row"] = selected[0]
            st.rerun()
        else:
            st.warning("⚠️ กรุณาเลือกแถวก่อน")

    # ลบข้อมูล
    if delete_btn:
        if selected:
            selected_index = df.index[df["เลขที่ใบกำกับ"] == selected[0]["เลขที่ใบกำกับ"]].tolist()
            if selected_index:
                df = df.drop(selected_index[0]).reset_index(drop=True)
                save_data(df)
                st.success("🗑️ ลบข้อมูลเรียบร้อยแล้ว!")
                st.rerun()
        else:
            st.warning("⚠️ กรุณาเลือกแถวก่อน")

# ==============================
# 🧾 ฟอร์มเพิ่ม/แก้ไขข้อมูล
# ==============================
if "edit_mode" in st.session_state:
    mode = st.session_state["edit_mode"]
    selected_row = st.session_state.get("selected_row", None)
    st.markdown("---")
    st.subheader("🧾 เพิ่ม / แก้ไขข้อมูล")

    with st.form("sales_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ", value=pd.to_datetime(selected_row["วันที่สั่งซื้อ"]) if mode == "edit" else None)
            ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=int(selected_row["ลำดับ"]) if mode == "edit" else 1)
            เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", value=selected_row["เลขที่ใบกำกับ"] if mode == "edit" else "")
            Seller = st.selectbox("Seller", ["shopee", "lazada", "cent", "อื่นๆ"], 
                                  index=["shopee", "lazada", "cent", "อื่นๆ"].index(selected_row["Seller"]) if mode == "edit" else 0)
            เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", value=selected_row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"] if mode == "edit" else "")

        with col2:
            รหัส = st.text_input("รหัส", value=selected_row["รหัส"] if mode == "edit" else "")
            สี = st.text_input("สี", value=selected_row["สี"] if mode == "edit" else "")
            Size = st.text_input("Size", value=selected_row["Size"] if mode == "edit" else "")
            ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=float(selected_row["ราคาขาย"]) if mode == "edit" else 0.0)
            ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=float(selected_row["ส่วนลด"]) if mode == "edit" else 0.0)
            สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=float(selected_row["สุทธิ"]) if mode == "edit" else 0.0)

        with col3:
            วดป = st.date_input("ว.ด.ป.", value=pd.to_datetime(selected_row["ว.ด.ป."]) if mode == "edit" else None)
            จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=float(selected_row["จำนวนเงิน"]) if mode == "edit" else 0.0)
            ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=float(selected_row["ค่าขนส่ง กทม."]) if mode == "edit" else 0.0)
            ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=float(selected_row["ค่าขนส่ง ตจว."]) if mode == "edit" else 0.0)
            เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", value=selected_row["เลขที่ใบโอน"] if mode == "edit" else "")

        submitted = st.form_submit_button("💾 บันทึกข้อมูล")

    if submitted:
        new_data = pd.DataFrame([[วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
                                  เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size, ราคาขาย,
                                  ส่วนลด, สุทธิ, วดป, จำนวนเงิน, ค่าขนส่งกทม,
                                  ค่าขนส่งตจว, เลขที่ใบโอน]], columns=COLUMNS)
        if mode == "edit":
            index = df.index[df["เลขที่ใบกำกับ"] == selected_row["เลขที่ใบกำกับ"]].tolist()[0]
            df.iloc[index] = new_data.iloc[0]
            st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
        else:
            df = pd.concat([df, new_data], ignore_index=True)
            st.success("✅ เพิ่มข้อมูลเรียบร้อยแล้ว!")

        save_data(df)
        del st.session_state["edit_mode"]
        st.rerun()
