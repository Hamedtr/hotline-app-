import streamlit as st
import jdatetime
import json
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import os

# ثبت فونت عمومی فارسی
FONT_PATH = "DejaVuSans.ttf"  # مطمئن شوید این فایل کنار فایل .py قرار دارد
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))
else:
    FONT_PATH = None

# بارگذاری فایل‌های داده
with open("activities.json", "r", encoding="utf-8") as f:
    activity_options = json.load(f)
with open("consumables.json", "r", encoding="utf-8") as f:
    consumables = json.load(f)
with open("scraps.json", "r", encoding="utf-8") as f:
    scraps = json.load(f)

st.set_page_config(page_title="Hotline 3.0", layout="centered")

def with_empty_option(lst):
    return ["--- انتخاب کنید ---"] + lst

# مقداردهی اولیه
if "activities" not in st.session_state:
    st.session_state.activities = []
if "current_address" not in st.session_state:
    st.session_state.current_address = {
        "line_station": "",
        "code": "",
        "work_type": "",
        "request_code": "",
        "related_department": "",
        "address": "",
        "groups": "",
        "gps": {"lat": "29.6100", "lon": "52.5310", "accuracy": "±10m"},
        "operations": []
    }
if "current_operation" not in st.session_state:
    st.session_state.current_operation = {
        "operation": "",
        "count": 1,
        "consumables": [{"item": "", "count": 1}],
        "scraps": [{"item": "", "count": 1}],
        "photos": {"before": None, "during": None, "after": None}
    }

st.title("ثبت عملیات برای یک آدرس")
st.markdown("### اطلاعات کلی آدرس")
st.session_state.current_address["work_type"] = st.selectbox("نوع کار", ["طرح شخصی", "طرح اداری", "اتفاقاتی", "تعمیرات پیشگیرانه"])
st.session_state.current_address["request_code"] = st.text_input("شماره درخواست خط گرم")
st.session_state.current_address["related_department"] = st.text_input("امور مربوطه")
st.session_state.current_address["address"] = st.text_input("آدرس محل کار")
st.session_state.current_address["groups"] = st.text_input("نام گروه‌های همکار")
st.session_state.current_address["line_station"] = st.text_input("شماره خط و ایستگاه")
st.session_state.current_address["code"] = st.text_input("کد تضمین")

st.markdown("---")
st.markdown("### شرح عملیات جدید")

col_op1, col_op2 = st.columns([3, 1])
st.session_state.current_operation["operation"] = col_op1.selectbox(
    "شرح فعالیت", with_empty_option(activity_options), index=0
)
st.session_state.current_operation["count"] = col_op2.number_input("تعداد", min_value=1, step=1)

st.markdown("#### اقلام مصرفی")
for i, item in enumerate(st.session_state.current_operation["consumables"]):
    col1, col2 = st.columns([3, 1])
    item["item"] = col1.selectbox(f"کالای مصرفی {i+1}", with_empty_option(consumables), key=f"cons_item_{i}")
    item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"cons_count_{i}")
if st.button("افزودن کالای مصرفی"):
    st.session_state.current_operation["consumables"].append({"item": "", "count": 1})

st.markdown("#### اقلام برگشتی")
for i, item in enumerate(st.session_state.current_operation["scraps"]):
    col1, col2 = st.columns([3, 1])
    item["item"] = col1.selectbox(f"کالای برگشتی {i+1}", with_empty_option(scraps), key=f"scr_item_{i}")
    item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"scr_count_{i}")
if st.button("افزودن کالای برگشتی"):
    st.session_state.current_operation["scraps"].append({"item": "", "count": 1})

st.markdown("#### عکس‌ها")
st.session_state.current_operation["photos"]["before"] = st.file_uploader("عکس قبل", type=["jpg", "jpeg", "png"])
st.session_state.current_operation["photos"]["during"] = st.file_uploader("عکس حین", type=["jpg", "jpeg", "png"])
st.session_state.current_operation["photos"]["after"] = st.file_uploader("عکس بعد", type=["jpg", "jpeg", "png"])

col_add, col_preview = st.columns(2)

if col_add.button("افزودن عملیات"):
    if st.session_state.current_operation["operation"] == "--- انتخاب کنید ---":
        st.warning("لطفاً یک شرح فعالیت معتبر انتخاب کنید.")
    else:
        st.session_state.current_address["operations"].append(
            st.session_state.current_operation.copy()
        )
        st.session_state.current_operation = {
            "operation": "",
            "count": 1,
            "consumables": [{"item": "", "count": 1}],
            "scraps": [{"item": "", "count": 1}],
            "photos": {"before": None, "during": None, "after": None}
        }
        st.success("عملیات ثبت شد. می‌توانید عملیات جدیدی اضافه کنید.")

if col_preview.button("ثبت اولیه"):
    if not st.session_state.current_address["operations"]:
        st.warning("لطفاً حداقل یک عملیات ثبت کنید.")
    else:
        st.session_state.preview_mode = True

if st.session_state.get("preview_mode", False):
    st.markdown("## پیش‌نمایش اطلاعات ثبت‌شده")
    addr = st.session_state.current_address
    st.subheader("اطلاعات کلی آدرس")
    st.text(f"""نوع کار: {addr['work_type']}
شماره درخواست: {addr['request_code']}
امور مربوطه: {addr['related_department']}
آدرس: {addr['address']}
گروه‌ها: {addr['groups']}
خط و ایستگاه: {addr['line_station']}
کد تضمین: {addr['code']}
موقعیت GPS: {addr['gps']['lat']}, {addr['gps']['lon']} ({addr['gps']['accuracy']})""")

    st.subheader("عملیات‌ها")
    for idx, op in enumerate(addr["operations"], 1):
        st.markdown(f"### عملیات {idx}")
        st.markdown(f"**شرح فعالیت:** {op['operation']} | **تعداد:** {op['count']}")
        if op["consumables"]:
            st.markdown("**اقلام مصرفی:**")
            for c in op["consumables"]:
                if c["item"]:
                    st.markdown(f"- {c['item']} × {c['count']}")
        if op["scraps"]:
            st.markdown("**اقلام برگشتی:**")
            for s in op["scraps"]:
                if s["item"]:
                    st.markdown(f"- {s['item']} × {s['count']}")
        st.markdown("**عکس‌ها:**")
        cols = st.columns(3)
        for i, lbl in enumerate(["before", "during", "after"]):
            img = op["photos"].get(lbl)
            if img:
                cols[i].image(img, caption=f"عکس {lbl}")

    col_confirm, col_cancel = st.columns(2)

    def generate_pdf(data):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont("DejaVu" if FONT_PATH else "Helvetica", 12)

        width, height = A4
        y = height - 2 * cm
        c.drawString(2 * cm, y, f"تاریخ گزارش: {jdatetime.date.today().strftime('%Y/%m/%d')}")
        y -= 1 * cm

        c.drawString(2 * cm, y, f"نوع کار: {data['work_type']} | شماره درخواست: {data['request_code']}")
        y -= 1 * cm
        c.drawString(2 * cm, y, f"آدرس: {data['address']} | امور: {data['related_department']}")
        y -= 1 * cm
        c.drawString(2 * cm, y, f"گروه‌ها: {data['groups']} | خط: {data['line_station']}")
        y -= 1.5 * cm

        for idx, op in enumerate(data["operations"], 1):
            c.drawString(2 * cm, y, f"{idx}- {op['operation']} × {op['count']}")
            y -= 0.8 * cm
            for cns in op["consumables"]:
                if cns["item"]:
                    c.drawString(3 * cm, y, f"مصرفی: {cns['item']} × {cns['count']}")
                    y -= 0.6 * cm
            for scr in op["scraps"]:
                if scr["item"]:
                    c.drawString(3 * cm, y, f"برگشتی: {scr['item']} × {scr['count']}")
                    y -= 0.6 * cm
            y -= 0.5 * cm
            if y < 3 * cm:
                c.showPage()
                c.setFont("DejaVu" if FONT_PATH else "Helvetica", 12)
                y = height - 2 * cm

        c.save()
        buffer.seek(0)
        return buffer

    if col_confirm.button("تأیید نهایی و ثبت"):
        st.session_state.activities.append(addr.copy())
        st.session_state.current_address = {
            "line_station": "",
            "code": "",
            "work_type": "",
            "request_code": "",
            "related_department": "",
            "address": "",
            "groups": "",
            "gps": {"lat": "29.6100", "lon": "52.5310", "accuracy": "±10m"},
            "operations": []
        }
        st.session_state.current_operation = {
            "operation": "",
            "count": 1,
            "consumables": [{"item": "", "count": 1}],
            "scraps": [{"item": "", "count": 1}],
            "photos": {"before": None, "during": None, "after": None}
        }
        st.session_state.preview_mode = False

        # خروجی PDF
        pdf_buffer = generate_pdf(addr)
        st.download_button("دانلود گزارش PDF", data=pdf_buffer, file_name="report.pdf", mime="application/pdf")

    if col_cancel.button("بازگشت برای ویرایش"):
        st.session_state.preview_mode = False
        st.info("بازگشت به حالت ویرایش.")
