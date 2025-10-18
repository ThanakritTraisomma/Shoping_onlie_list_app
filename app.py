import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="รายงานภาษีขายรายวัน", layout="wide")

st.title("📑 ระบบกรอกและแก้ไขรายงานภาษีขายรายวัน")

# ==============================
# 📂 โหลดข้อมูล (ไม่ต้องอัปโหลด)
# ==============================
DATA_FILE = "sales_daily.xlsx"
COLUMNS = [
    "วันที่สั่งซื้อ", "ลำดับ", "เลขที่ใบกำกับ", "Seller",
    "เลขที่คำสั่งซื้อ/ชื่อลูกค้า", "รหัส", "สี", "Size",
    "ราคาขาย", "ส่วนลด", "สุทธิ", "ว.ด.ป.", "จำนวนเงิน",
    "ค่าขนส่ง กทม.", "ค่าขนส่ง ตจว.", "เลขที่ใบโอน", "หมายเหตุ"
]

if "df" not in st.session_state:
    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=COLUMNS)
    st.session_state.df = df

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None


# ==============================
# 🧾 ฟอร์มกรอกข้อมูล
# ==============================
st.subheader("🧾 ฟอร์มกรอกข้อมูล")

def clear_form():
    st.session_state.edit_index = None
    st.rerun()

df = st.session_state.df

edit_row = None
if st.session_state.edit_index is not None:
    edit_row = df.loc[st.session_state.edit_index]
    st.info(f"✏️ กำลังแก้ไขแถวที่ {st.session_state.edit_index + 1}")

with st.form("sales_form", clear_on_submit=False):
    col1, col2, col3 = st.columns(3)

    with col1:
        วันที่สั่งซื้อ = st.date_input("วันที่สั่งซื้อ", value=pd.to_datetime(edit_row["วันที่สั่งซื้อ"]) if edit_row is not None else pd.Timestamp.today())
        ลำดับ = st.number_input("ลำดับ", min_value=1, step=1, value=int(edit_row["ลำดับ"]) if edit_row is not None and str(edit_row["ลำดับ"]).isdigit() else 1)
        เลขที่ใบกำกับ = st.text_input("เลขที่ใบกำกับ", value=str(edit_row["เลขที่ใบกำกับ"]) if edit_row is not None else "")
        Seller = st.selectbox("Seller", ["shopee", "lazada", "cent", "อื่นๆ"], index=0)
        เลขที่คำสั่งซื้อชื่อลูกค้า = st.text_input("เลขที่คำสั่งซื้อ/ชื่อลูกค้า", value=str(edit_row["เลขที่คำสั่งซื้อ/ชื่อลูกค้า"]) if edit_row is not None else "")

    with col2:
        รหัส = st.text_input("รหัส", value=str(edit_row["รหัส"]) if edit_row is not None else "")
        สี = st.text_input("สี", value=str(edit_row["สี"]) if edit_row is not None else "")
        Size = st.text_input("Size", value=str(edit_row["Size"]) if edit_row is not None else "")
        ราคาขาย = st.number_input("ราคาขาย", min_value=0.0, value=float(edit_row["ราคาขาย"]) if edit_row is not None else 0.0)
        ส่วนลด = st.number_input("ส่วนลด", min_value=0.0, value=float(edit_row["ส่วนลด"]) if edit_row is not None else 0.0)
        สุทธิ = st.number_input("สุทธิ", min_value=0.0, value=float(edit_row["สุทธิ"]) if edit_row is not None else 0.0)

    with col3:
        วดป = st.date_input("ว.ด.ป.", value=pd.to_datetime(edit_row["ว.ด.ป."]) if edit_row is not None else pd.Timestamp.today())
        จำนวนเงิน = st.number_input("จำนวนเงิน", min_value=0.0, value=float(edit_row["จำนวนเงิน"]) if edit_row is not None else 0.0)
        ค่าขนส่งกทม = st.number_input("ค่าขนส่ง กทม.", min_value=0.0, value=float(edit_row["ค่าขนส่ง กทม."]) if edit_row is not None else 0.0)
        ค่าขนส่งตจว = st.number_input("ค่าขนส่ง ตจว.", min_value=0.0, value=float(edit_row["ค่าขนส่ง ตจว."]) if edit_row is not None else 0.0)
        เลขที่ใบโอน = st.text_input("เลขที่ใบโอน", value=str(edit_row["เลขที่ใบโอน"]) if edit_row is not None else "")

    st.markdown("---")
    st.markdown("### 📝 หมายเหตุ")

    remark_options = ["", "คืนสินค้า", "พัสดุตีกลับ", "ยกเลิกออเดอร์", "อื่นๆ"]
    current_remark = ""
    remark_text = ""

    if edit_row is not None and isinstance(edit_row["หมายเหตุ"], str):
        for opt in remark_options:
            if opt and opt in edit_row["หมายเหตุ"]:
                current_remark = opt
                if "(" in edit_row["หมายเหตุ"]:
                    remark_text = edit_row["หมายเหตุ"].split("(")[-1].rstrip(")")
                break

    หมายเหตุหลัก = st.selectbox("เลือกหมายเหตุ", remark_options, index=remark_options.index(current_remark))
    รายละเอียดเพิ่มเติม = ""
    if หมายเหตุหลัก != "":
        รายละเอียดเพิ่มเติม = st.text_area("รายละเอียดเพิ่มเติม", value=remark_text)

    หมายเหตุ = หมายเหตุหลัก
    if รายละเอียดเพิ่มเติม:
        หมายเหตุ += f" ({รายละเอียดเพิ่มเติม})"

    submitted = st.form_submit_button("💾 บันทึกข้อมูล", use_container_width=True)
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
        df.loc[st.session_state.edit_index] = new_data
        st.success("✅ แก้ไขข้อมูลเรียบร้อยแล้ว!")
        st.session_state.edit_index = None
    else:
        df.loc[len(df)] = new_data
        st.success("✅ เพิ่มข้อมูลใหม่เรียบร้อยแล้ว!")

    df.sort_values(by="วันที่สั่งซื้อ", ascending=True, inplace=True)
    df.to_excel(DATA_FILE, index=False)
    st.session_state.df = df
    st.rerun()


# ==============================
# 📋 ตารางพร้อมปุ่มแก้ไข/ลบ
# ==============================
st.subheader("📋 ตารางข้อมูลทั้งหมด")

for i, row in df.iterrows():
    cols = st.columns([1, 1, 8])  # ปุ่ม + ข้อมูล
    with cols[0]:
        if st.button("✏️", key=f"edit_{i}"):
            st.session_state.edit_index = i
            st.rerun()
    with cols[1]:
        if st.button("🗑️", key=f"del_{i}"):
            df = df.drop(i).reset_index(drop=True)
            df.to_excel(DATA_FILE, index=False)
            st.session_state.df = df
            st.success(f"ลบแถวที่ {i+1} แล้ว")
            st.rerun()
    with cols[2]:
        st.write(row.to_dict())

# ==============================
# ⬇️ ดาวน์โหลดไฟล์
# ==============================
buffer = BytesIO()
df.to_excel(buffer, index=False)
buffer.seek(0)
st.download_button(
    label="📥 ดาวน์โหลด Excel",
    data=buffer,
    file_name="sales_daily.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
