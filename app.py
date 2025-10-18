import streamlit as st
import pandas as pd
import os
from io import BytesIO

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

def clear_form():
    for key in list(st.session_state.keys()):
        if key not in ["edit_index"]:
            del st.session_state[key]

st.subheader("🧾 กรอกหรือแก้ไขข้อมูล")

edit_mode = "edit_index" in st.session_state and st.session_state.edit_index is not None
edit_row = df.loc[st.session_state.edit_index] if edit_mode else None

with st.form("sales_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ", value=None if not edit_mode else pd.to_datetime(edit_row["วันที่สั่งซื้อ"], errors="coerce"))
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=1 if not edit_mode else int(edit_row["ลำดับ"]))
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", value="" if not edit_mode else str(edit_row["เลขที่ใบกำกับ"]))
        Seller = st.selectbox(
            "Seller", ["shopee", "lazada", "cent", "อื่นๆ"],
            index=0 if not edit_mode else (
                ["shopee", "lazada", "cent", "อื่นๆ"].index(edit_row["Seller"])
                if edit_row["Seller"] in ["shopee", "lazada", "cent", "อื่นๆ"] else 0
            ),
        )
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", value="" if not edit_mode else str(edit_row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"]))

    with col2:
        รหัส = st.text_input("รหัส", value="" if not edit_mode else str(edit_row["รหัส"]))
        สี = st.text_input("สี", value="" if not edit_mode else str(edit_row["สี"]))
        Size = st.text_input("Size", value="" if not edit_mode else str(edit_row["Size"]))
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["ราคาขาย"]))
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["ส่วนลด"]))
        สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["สุทธิ"]))

    with col3:
        วดป = st.date_input("ว.ด.ป.", value=None if not edit_mode else pd.to_datetime(edit_row["ว.ด.ป."], errors="coerce"))
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["จำนวนเงิน"]))
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["ค่าขนส่ง กทม."]))
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=0.0 if not edit_mode else float(edit_row["ค่าขนส่ง ตจว."]))

        # 🔹 แยกเลขที่ใบโอน + หมายเหตุ (เวลาแก้ไข)
        edit_เลขที่ใบโอน = ""
        edit_หมายเหตุ = ""
        if edit_mode:
            txt = str(edit_row["เลขที่ใบโอน"])
            if "| หมายเหตุ:" in txt:
                parts = txt.split("| หมายเหตุ:")
                edit_เลขที่ใบโอน = parts[0].strip()
                edit_หมายเหตุ = parts[1].strip()
            else:
                edit_เลขที่ใบโอน = txt

        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", value=edit_เลขที่ใบโอน if edit_mode else "")
        หมายเหตุ_ตัวเลือก = st.selectbox(
            "หมายเหตุ", ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"],
            index=0 if not edit_mode else (
                ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"].index(edit_หมายเหตุ.split(":", 1)[0])
                if any(edit_หมายเหตุ.startswith(opt) for opt in ["คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"]) else 0
            )
        )

        หมายเหตุ_รายละเอียด = ""
        if หมายเหตุ_ตัวเลือก != "":
            หมายเหตุ_รายละเอียด = st.text_input(
                "รายละเอียดเพิ่มเติม",
                value="" if not edit_mode else (
                    edit_หมายเหตุ.split(":", 1)[1].strip() if ":" in edit_หมายเหตุ else ""
                )
            )

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

if submitted:
    หมายเหตุรวม = f" | หมายเหตุ: {หมายเหตุ_ตัวเลือก}: {หมายเหตุ_รายละเอียด}" if หมายเหตุ_ตัวเลือก else ""
    เลขที่ใบโอน_เต็ม = str(เลขที่ใบโอน) + หมายเหตุรวม

    new_data = pd.DataFrame([[วันที่สั่งซื้อ, ลำดับ, เลขที่ใบกำกับ, Seller,
        เลขที่คำสั่งซื้อชื่อลูกค้า, รหัส, สี, Size, ราคาขาย, ส่วนลด,
        สุทธิ, วดป, จำนวนเงิน, ค่าขนส่งกทม, ค่าขนส่งตจว, เลขที่ใบโอน_เต็ม]],
        columns=COLUMNS)

    if edit_mode:
        df.iloc[st.session_state.edit_index] = new_data.iloc[0]
        st.session_state.edit_index = None
        st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
    else:
        df = pd.concat([df, new_data], ignore_index=True)
        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว!")

    df["วันที่สั่งซื้อ"] = pd.to_datetime(df["วันที่สั่งซื้อ"], errors="coerce")
    df = df.sort_values(by="วันที่สั่งซื้อ", ascending=True).reset_index(drop=True)

    df.to_excel(DATA_FILE, index=False)
    clear_form()
    st.rerun()

# ==========================
# 📋 ตารางข้อมูล
# ==========================
st.subheader("📋 ข้อมูลทั้งหมด")
if not df.empty:
    st.dataframe(df, use_container_width=True)

    for i, row in df.iterrows():
        cols = st.columns([0.1, 0.1, 1, 1, 1, 1])
        with cols[0]:
            edit_btn = st.button("✏️ แก้ไข", key=f"edit_{i}")
        with cols[1]:
            delete_btn = st.button("🗑️ ลบ", key=f"delete_{i}")
        cols[2].write(row["เลขที่ใบกำกับ"])
        cols[3].write(row["Seller"])
        cols[4].write(row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"])
        cols[5].write(row["เลขที่ใบโอน"])

        if edit_btn:
            st.session_state.edit_index = i
            st.rerun()

        if delete_btn:
            df = df.drop(i).reset_index(drop=True)
            df.to_excel(DATA_FILE, index=False)
            st.warning("🗑️ ลบข้อมูลเรียบร้อยแล้ว!")
            st.rerun()
else:
    st.info("ยังไม่มีข้อมูล กรุณากรอกข้อมูลใหม่")
