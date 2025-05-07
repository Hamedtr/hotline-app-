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

# بارگذاری داده‌ها
with open("activities.json", "r", encoding="utf-8") as f:
    activity_options = json.load(f)
with open("consumables.json", "r", encoding="utf-8") as f:
    consumables = json.load(f)
with open("scraps.json", "r", encoding="utf-8") as f:
    scraps = json.load(f)

st.set_page_config(page_title="Hotline 3.0", layout="centered")

def with_empty_option(lst):
    return ["--- انتخاب کنید ---"] + lst

# صفحه ورود اولیه
if "user_code" not in st.session_state:
    st.session_state.user_code = None
if "personnel" not in st.session_state:
    st.session_state.personnel = {}

if st.session_state.user_code is None:
    st.title("ورود روزانه")
    today = jdatetime.date.today().strftime("%A %d %B %Y")
    st.markdown(f"### امروز: {today}")
    with st.form("login_form"):
        supervisor = st.text_input("نام سرپرست")
        p2 = st.text_input("نفر دوم")
        p3 = st.text_input("نفر سوم")
        driver = st.text_input("راننده")
        if st.form_submit_button("شروع ثبت"):
            if not supervisor or not p2 or not p3 or not driver:
                st.warning("لطفاً همه فیلدها را کامل کنید.")
            else:
                st.session_state.user_code = "ok"
                st.session_state.personnel = {
                    "supervisor": supervisor,
                    "person2": p2,
                    "person3": p3,
                    "driver": driver
                }
    st.stop()

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

# فرم آدرس و عملیات
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
st.session_state.current_operation["operation"] = col_op1.selectbox("شرح فعالیت", with_empty_option(activity_options), index=0)
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
st.session_state.current_operation["photos"]["before"] = st.file_uploader("عکس قبل")
st.session_state.current_operation["photos"]["during"] = st.file_uploader("عکس حین")
st.session_state.current_operation["photos"]["after"] = st.file_uploader("عکس بعد")

col_add, col_finish = st.columns(2)

if col_add.button("افزودن عملیات"):
    st.session_state.current_address["operations"].append(st.session_state.current_operation.copy())
    st.session_state.current_operation = {
        "operation": "",
        "count": 1,
        "consumables": [{"item": "", "count": 1}],
        "scraps": [{"item": "", "count": 1}],
        "photos": {"before": None, "during": None, "after": None}
    }
    st.success("عملیات ثبت شد.")

if col_finish.button("پایان عملیات"):
    st.session_state.activities.append(st.session_state.current_address.copy())
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
    st.success("آدرس و عملیات‌ها نهایی شدند.")

# نمایش عملیات‌ها
st.markdown("---")
st.markdown("### عملیات‌های ثبت‌شده")
for i, addr in enumerate(st.session_state.activities, 1):
    st.markdown(f"**آدرس {i}: {addr['address']}**")
    for j, op in enumerate(addr["operations"], 1):
        st.markdown(f"- {j}. {op['operation']} × {op['count']}")

# خروجی PDF و JSON
def generate_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    font_path = "fonts/Vazir.ttf"
    if not os.path.exists(font_path):
        st.error("فونت Vazir.ttf پیدا نشد.")
        return None
    pdfmetrics.registerFont(TTFont("Vazir", font_path))
    c.setFont("Vazir", 13)
    width, height = A4
    y = height - 2*cm
    c.drawRightString(width - 2*cm, y, "توزیع برق شیراز – عملیات خط گرم")
    y -= 1*cm
    c.drawRightString(width - 2*cm, y, "گزارش عملیات روزانه - Hotline 3.0")
    y -= 1*cm
    c.setFont("Vazir", 11)
    c.drawRightString(width - 2*cm, y, f"تاریخ: {jdatetime.date.today().strftime('%Y/%m/%d')}")
    y -= 1.2*cm
    for i, addr in enumerate(data["activities"], 1):
        c.drawRightString(width - 2*cm, y, f"آدرس {i}: {addr['address']} ({addr['work_type']})")
        y -= 0.8*cm
        for j, op in enumerate(addr["operations"], 1):
            c.drawRightString(width - 2*cm, y, f"- عملیات {j}: {op['operation']} × {op['count']}")
            y -= 0.6*cm
        y -= 0.6*cm
        if y < 5*cm:
            c.showPage()
            c.setFont("Vazir", 13)
            y = height - 2*cm
    c.save()
    buffer.seek(0)
    return buffer

def export_results():
    st.markdown("---")
    st.markdown("### خروجی گزارش")
    data = {
        "date": jdatetime.date.today().isoformat(),
        "personnel": st.session_state.personnel,
        "activities": st.session_state.activities
    }
    json_buffer = BytesIO()
    json_buffer.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
    json_buffer.seek(0)
    st.download_button("دانلود گزارش JSON", json_buffer, file_name="hotline_report.json", mime="application/json")
    pdf_buffer = generate_pdf(data)
    if pdf_buffer:
        st.download_button("دانلود گزارش PDF", pdf_buffer, file_name="hotline_report.pdf", mime="application/pdf")

export_results()
