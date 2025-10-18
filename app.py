import streamlit as st
import pandas as pd

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")

st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")

# =========================
# 1️⃣ ตั้งค่าเริ่มต้น
# =========================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=[
            "วันที่", "เลขที่ใบกำกับภาษี", "ชื่อลูกค้า",
            "มูลค่าสินค้า", "ภาษีมูลค่าเพิ่ม", "ยอดรวม",
            "หมายเหตุ", "รายละเอียดเพิ่มเติม"
        ]
    )

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

df = st.session_state.df

# =========================
# 2️⃣ ฟังก์ชันบันทึกข้อมูล
# =========================
def save_data(new_data):
    st.session_state.df = pd.concat(
        [st.session_state.df, pd.DataFrame([new_data])],
        ignore_index=True
    )
    st.session_state.df.reset_index(drop=True, inplace=True)

def update_data(index, new_data):
    if 0 <= index < len(st.session_state.df):
        st.session_state.df.iloc[index] = new_data
        st.session_state.df.reset_index(drop=True, inplace=True)
    st.session_state.edit_index = None

def delete_data(index):
    if 0 <= index < len(st.session_state.df):
        st.session_state.df = st.session_state.df.drop(index).reset_index(drop=True)

# =========================
# 3️⃣ ฟอร์มกรอกข้อมูล
# =========================
st.subheader("🖊️ ฟอร์มกรอกข้อมูล")

edit_row = None
if (
    st.session_state.edit_index is not None
    and 0 <= st.session_state.edit_index < len(df)
):
    edit_row = df.iloc[st.session_state.edit_index]
else:
    st.session_state.edit_index = None

with st.form("input_form", clear_on_submit=(edit_row is None)):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("วันที่", value=None if edit_row is None else pd.to_datetime(edit_row["วันที่"]))
        name = st.text_input("ชื่อลูกค้า", value="" if edit_row is None else edit_row["ชื่อลูกค้า"])
    with col2:
        invoice = st.text_input("เลขที่ใบกำกับภาษี", value="" if edit_row is None else edit_row["เลขที่ใบกำกับภาษี"])
        product_value = st.number_input("มูลค่าสินค้า", min_value=0.0, value=0.0 if edit_row is None else float(edit_row["มูลค่าสินค้า"]))
    with col3:
        vat = st.number_input("ภาษีมูลค่าเพิ่ม", min_value=0.0, value=0.0 if edit_row is None else float(edit_row["ภาษีมูลค่าเพิ่ม"]))
        total = st.number_input("ยอดรวม", min_value=0.0, value=0.0 if edit_row is None else float(edit_row["ยอดรวม"]))

    remark = st.selectbox(
        "หมายเหตุ",
        ["", "ชำระแล้ว", "ยังไม่ชำระ", "อื่น ๆ"],
        index=0 if edit_row is None else
        (["", "ชำระแล้ว", "ยังไม่ชำระ", "อื่น ๆ"].index(edit_row["หมายเหตุ"]) if edit_row["หมายเหตุ"] in ["", "ชำระแล้ว", "ยังไม่ชำระ", "อื่น ๆ"] else 0)
    )

    detail = ""
    if remark != "":
        detail = st.text_area("รายละเอียดเพิ่มเติม", value="" if edit_row is None else str(edit_row["รายละเอียดเพิ่มเติม"]))

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")
    if submitted:
        new_row = {
            "วันที่": date,
            "เลขที่ใบกำกับภาษี": invoice,
            "ชื่อลูกค้า": name,
            "มูลค่าสินค้า": product_value,
            "ภาษีมูลค่าเพิ่ม": vat,
            "ยอดรวม": total,
            "หมายเหตุ": remark,
            "รายละเอียดเพิ่มเติม": detail,
        }

        if edit_row is None:
            save_data(new_row)
            st.success("✅ เพิ่มข้อมูลเรียบร้อยแล้ว")
        else:
            update_data(st.session_state.edit_index, new_row)
            st.success("✏️ แก้ไขข้อมูลเรียบร้อยแล้ว")

# =========================
# 4️⃣ ตารางแสดงข้อมูล
# =========================
st.subheader("📋 ตารางข้อมูล")

if not st.session_state.df.empty:
    for i, row in st.session_state.df.iterrows():
        with st.expander(f"🧾 {row['เลขที่ใบกำกับภาษี']} - {row['ชื่อลูกค้า']}"):
            st.write(row.to_frame().T)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ แก้ไข", key=f"edit_{i}"):
                    st.session_state.edit_index = i
                    st.experimental_rerun()
            with col2:
                if st.button("🗑️ ลบ", key=f"delete_{i}"):
                    delete_data(i)
                    st.experimental_rerun()
else:
    st.info("ยังไม่มีข้อมูล กรุณากรอกข้อมูลใหม่")

# =========================
# 5️⃣ ดาวน์โหลดข้อมูลเป็น Excel
# =========================
st.download_button(
    label="⬇️ ดาวน์โหลดข้อมูลเป็น Excel",
    data=st.session_state.df.to_csv(index=False).encode("utf-8-sig"),
    file_name="รายงานภาษีขายรายวัน.csv",
    mime="text/csv",
)
