import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")
st.title("📑 ระบบกรอกข้อมูลรายงานภาษีขายรายวัน")

DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน",
    "หมายเหตุ", "รายละเอียด"
]

# โหลดข้อมูล
if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
    df = pd.read_excel(DATA_FILE)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
else:
    df = pd.DataFrame(columns=COLUMNS)

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

def clear_form():
    for key in list(st.session_state.keys()):
        if key not in ["selected_index"]:
            del st.session_state[key]

# ==========================
# 📋 ตารางข้อมูล
# ==========================
st.subheader("📋 ตารางข้อมูล (เรียงตามวันที่สั่งซื้อ)")
df["วันที่สั่งซื้อ"] = pd.to_datetime(df["วันที่สั่งซื้อ"], errors="coerce")
df_sorted = df.sort_values(by="วันที่สั่งซื้อ", ascending=True).reset_index(drop=True)

if not df_sorted.empty:
    # แสดงตาราง
    st.dataframe(df_sorted, use_container_width=True)

    # เลือกแถวแบบ radio (ซ่อนด้านข้าง)
    selected = st.radio(
        "คลิกเลือกแถวเพื่อแก้ไข",
        options=df_sorted.index,
        format_func=lambda i: f"ลำดับ {df_sorted.loc[i, 'ลำดับ']} | {df_sorted.loc[i, 'เลขที่ใบกำกับ']}"
    )
    st.session_state.selected_index = selected
else:
    st.info("ยังไม่มีข้อมูล กรุณากรอกข้อมูลใหม่")
    selected = None

# ==========================
# 🧾 ฟอร์มกรอก/แก้ไขข้อมูล
# ==========================
st.subheader("🧾 กรอกหรือแก้ไขข้อมูล")

edit_mode = "selected_index" in st.session_state and st.session_state.selected_index is not None
edit_row = df_sorted.loc[st.session_state.selected_index] if edit_mode else None

with st.form("sales_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input(
            "วันที่สั่งซื้อ",
            value=None if not edit_mode else pd.to_datetime(edit_row["วันที่สั่งซื้อ"], errors="coerce")
        )
        ลำดับ = st.number_input(
            "ลำดับ", min_value=1, step=1,
            value=1 if not edit_mode else int(edit_row["ลำดับ"])
        )
        เลขที่ใบกำกับ = st.text_input(
            "เลขที่ใบกำกับ",
            value="" if not edit_mode else str(edit_row["เลขที่ใบกำกับ"])
        )
        Seller = st.selectbox(
            "Seller",
            ["shopee", "lazada", "cent", "อื่นๆ"],
            index=0 if not edit_mode else (
                ["shopee", "lazada", "cent", "อื่นๆ"].index(edit_row["Seller"])
                if edit_row["Seller"] in ["shopee", "lazada", "cent", "อื่นๆ"]
                else 0
            ),
        )
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input(
            "เลขที่คำสั่งซื้อ/ชื่อลูกค้า",
            value="" if not edit_mode else str(edit_row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"])
        )

    with col2:
        รหัส = st.text_input("รหัส", value="" if not edit_mode else str(edit_row["รหัส"]))
        สี = st.text_input("สี", value="" if not edit_mode else str(edit_row["สี"]))
        Size = st.text_input("Size", value="" if not edit_mode else str(edit_row["Size"]))
        ราคาขาย = st.number_input(
            "ราคาขาย", min_value=0.0,
            value=0.0 if not edit_mode else float(edit_row["ราคาขาย"])
        )
        ส่วนลด = st.number_input(
            "ส่วนลด", min_value=0.0,
            value=0.0 if not edit_mode else float(edit_row["ส่วนลด"])
        )
        สุทธิ = st.number_input(
            "สุทธิ", min_value=0.0,
            value=0.0 if not edit_mode else float(edit_row["สุทธิ"])
        )

    with col3:
        วดป = st.date_input(
            "ว.ด.ป.",
            value=None if not edit_mode else pd.to_datetime(edit_row["ว.ด.ป."], errors="coerce")
        )
        จำนวนเงิน = st.number_input(
            "จำนวนเงิน", min_value=0.0,
            value=0.0 if not edit_mode else float(edit_row["จำนวนเงิน"])
        )
        ค่าขนส่งกทม = st.number_input(
            "ค่าขนส่ง กทม.", min_value=0.0,
            value=0.0 if not edit_mode else float(edit_row["ค่าขนส่ง กทม."])
        )
        ค่าขนส่งตจว = st.number_input(
            "ค่าขนส่ง ตจว.", min_value=0.0,
            value=0.0 if not edit_mode else float(edit_row["ค่าขนส่ง ตจว."])
        )
        เลขที่ใบโอน = st.text_input(
            "เลขที่ใบโอน",
            value="" if not edit_mode else str(edit_row["เลขที่ใบโอน"])
        )

        หมายเหตุ_ตัวเลือก = st.selectbox(
            "หมายเหตุ",
            ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"],
            index=0 if not edit_mode else (
                ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"].index(str(edit_row["หมายเหตุ"]))
                if edit_row["หมายเหตุ"] in ["คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"] else 0
            )
        )

        รายละเอียด = ""
        if หมายเหตุ_ตัวเลือก:
            รายละเอียด = st.text_input(
                "รายละเอียดเพิ่มเติม",
                value="" if not edit_mode else str(edit_row["รายละเอียด"])
            )

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")
    delete_btn = st.form_submit_button("🗑️ ลบข้อมูล") if edit_mode else False

# ==========================
# ✅ บันทึกหรือ ลบข้อมูล
# ==========================
if submitted and edit_mode:
    df.iloc[st.session_state.selected_index] = [
        วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size,
        ราคาขาย, ส่วนลด, สุทธิ, วดป, จำนวนเงิน,
        ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน,
        หมายเหตุ_ตัวเลือก, รายละเอียด
    ]
    save_data(df)
    st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
    clear_form()
    st.session_state.selected_index = None
    st.experimental_rerun()

if delete_btn and edit_mode:
    df = df.drop(st.session_state.selected_index).reset_index(drop=True)
    save_data(df)
    st.warning("🗑️ ลบข้อมูลเรียบร้อยแล้ว!")
    clear_form()
    st.session_state.selected_index = None
    st.experimental_rerun()
