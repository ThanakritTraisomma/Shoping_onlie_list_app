import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")

st.title("📊 รายงานภาษีขายรายวัน")

# -------------------------------
# 1️⃣ โหลดข้อมูล (หรือสร้าง DataFrame เริ่มต้น)
# -------------------------------
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "วันที่สั่งซื้อ", "ชื่อร้านค้า", "เลขที่ใบเสร็จ",
        "จำนวนเงิน", "เลขที่ใบโอน", "หมายเหตุ"
    ])

df = st.session_state.df

# -------------------------------
# 2️⃣ ฟอร์มกรอกข้อมูลใหม่
# -------------------------------
with st.form("data_entry_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("📅 วันที่สั่งซื้อ", datetime.today())
    with col2:
        shop_name = st.text_input("🏪 ชื่อร้านค้า")
    with col3:
        receipt_no = st.text_input("🧾 เลขที่ใบเสร็จ")

    col4, col5, col6 = st.columns(3)
    with col4:
        amount = st.number_input("💰 จำนวนเงิน", min_value=0.0, step=0.01)
    with col5:
        transfer_no = st.text_input("🏦 เลขที่ใบโอน")
    with col6:
        remark = st.text_input("🗒 หมายเหตุ")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

    if submitted:
        new_row = {
            "วันที่สั่งซื้อ": date,
            "ชื่อร้านค้า": shop_name,
            "เลขที่ใบเสร็จ": receipt_no,
            "จำนวนเงิน": amount,
            "เลขที่ใบโอน": transfer_no,
            "หมายเหตุ": remark
        }
        st.session_state.df = pd.concat(
            [st.session_state.df, pd.DataFrame([new_row])],
            ignore_index=True
        )
        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

# -------------------------------
# 3️⃣ แสดงตารางข้อมูลแบบ AgGrid
# -------------------------------
st.markdown("## 📋 ข้อมูลที่บันทึกไว้")

if not df.empty:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(enabled=True)
    gb.configure_default_column(editable=False, wrapText=True, autoHeight=True)
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_side_bar()
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        theme="alpine_dark",  # ✅ ปรับธีมให้ไอคอนมองเห็นได้
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        height=400,
    )

    selected = grid_response["selected_rows"]
    if selected:
        selected_row = selected[0]
        row_index = df.index[df["เลขที่ใบเสร็จ"] == selected_row["เลขที่ใบเสร็จ"]].tolist()[0]

        st.divider()
        st.subheader("✏️ แก้ไข / ลบข้อมูล")

        with st.form("edit_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                date_edit = st.date_input("📅 วันที่สั่งซื้อ", pd.to_datetime(selected_row["วันที่สั่งซื้อ"]))
            with c2:
                shop_edit = st.text_input("🏪 ชื่อร้านค้า", selected_row["ชื่อร้านค้า"])
            with c3:
                receipt_edit = st.text_input("🧾 เลขที่ใบเสร็จ", selected_row["เลขที่ใบเสร็จ"])

            c4, c5, c6 = st.columns(3)
            with c4:
                amount_edit = st.number_input("💰 จำนวนเงิน", min_value=0.0, step=0.01, value=float(selected_row["จำนวนเงิน"]))
            with c5:
                transfer_edit = st.text_input("🏦 เลขที่ใบโอน", selected_row["เลขที่ใบโอน"])
            with c6:
                remark_edit = st.text_input("🗒 หมายเหตุ", selected_row["หมายเหตุ"])

            edit_submit = st.form_submit_button("💾 บันทึกการแก้ไข")
            delete_submit = st.form_submit_button("🗑️ ลบรายการนี้")

            if edit_submit:
                st.session_state.df.loc[row_index] = [
                    date_edit, shop_edit, receipt_edit, amount_edit, transfer_edit, remark_edit
                ]
                st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
                st.rerun()

            if delete_submit:
                st.session_state.df = st.session_state.df.drop(row_index).reset_index(drop=True)
                st.warning("🗑️ ลบข้อมูลเรียบร้อยแล้ว!")
                st.rerun()

else:
    st.info("📝 ยังไม่มีข้อมูล กรุณากรอกในฟอร์มด้านบนก่อนครับ")

# -------------------------------
# 4️⃣ ปุ่มดาวน์โหลด Excel
# -------------------------------
st.divider()
st.subheader("⬇️ ดาวน์โหลดข้อมูลเป็นไฟล์ Excel")

if not df.empty:
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 ดาวน์โหลดไฟล์ Excel",
        data=buffer,
        file_name="sales_daily.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.write("ยังไม่มีข้อมูลให้ดาวน์โหลดครับ 😅")
