import streamlit as st
import json
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# بارگذاری فایل‌های داده
with open("activities.json", "r", encoding="utf-8") as f:
    activity_options = json.load(f)
with open("consumables.json", "r", encoding="utf-8") as f:
    consumables = json.load(f)
with open("scraps.json", "r", encoding="utf-8") as f:
    scraps = json.load(f)

# تنظیمات اولیه
st.set_page_config(page_title="Hotline 3.0", layout="centered")

# حالت اولیه
if 'daily_data' not in st.session_state:
    st.session_state.daily_data = []

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

# فرم ثبت اطلاعات روزانه
group_name = st.text_input("نام گروه:")
activity_details = st.text_area("جزئیات فعالیت‌های روزانه:")
comments = st.text_area("نظرات و یادداشت‌ها:")

if st.button("ثبت اطلاعات روزانه"):
    date = datetime.now().strftime("%Y-%m-%d")
    daily_entry = {
        "date": date,
        "group_name": group_name,
        "activity_details": activity_details,
        "comments": comments
    }
    st.session_state.daily_data.append(daily_entry)
    st.success("اطلاعات روزانه ثبت شد.")

# نمایش اطلاعات ثبت‌شده
for entry in st.session_state.daily_data:
    st.markdown(f"**تاریخ:** {entry['date']}  ")
    st.markdown(f"**گروه:** {entry['group_name']}")
    st.markdown(f"**فعالیت‌ها:** {entry['activity_details']}")
    st.markdown(f"**نظرات:** {entry['comments']}")
    st.markdown("---")

# اطلاعات آدرس و عملیات جدید
st.header("ثبت عملیات برای یک آدرس")
st.session_state.current_address["work_type"] = st.selectbox("نوع کار", ["طرح شخصی", "طرح اداری", "اتفاقاتی", "تعمیرات پیشگیرانه"])
st.session_state.current_address["request_code"] = st.text_input("شماره درخواست خط گرم")
st.session_state.current_address["related_department"] = st.text_input("امور مربوطه")
st.session_state.current_address["address"] = st.text_input("آدرس محل کار")
st.session_state.current_address["groups"] = st.text_input("نام گروه‌های همکار")
st.session_state.current_address["line_station"] = st.text_input("شماره خط و ایستگاه")
st.session_state.current_address["code"] = st.text_input("کد تضمین")

st.subheader("شرح عملیات جدید")
col1, col2 = st.columns([3, 1])
st.session_state.current_operation["operation"] = col1.selectbox("شرح فعالیت", ["--- انتخاب کنید ---"] + activity_options)
st.session_state.current_operation["count"] = col2.number_input("تعداد", min_value=1, step=1)

st.subheader("اقلام مصرفی")
for i, item in enumerate(st.session_state.current_operation["consumables"]):
    col1, col2 = st.columns([3, 1])
    item["item"] = col1.selectbox(f"کالای مصرفی {i+1}", ["--- انتخاب کنید ---"] + consumables, key=f"cons_item_{i}")
    item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"cons_count_{i}")
if st.button("افزودن کالای مصرفی"):
    st.session_state.current_operation["consumables"].append({"item": "", "count": 1})

st.subheader("اقلام برگشتی")
for i, item in enumerate(st.session_state.current_operation["scraps"]):
    col1, col2 = st.columns([3, 1])
    item["item"] = col1.selectbox(f"کالای برگشتی {i+1}", ["--- انتخاب کنید ---"] + scraps, key=f"scr_item_{i}")
    item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"scr_count_{i}")
if st.button("افزودن کالای برگشتی"):
    st.session_state.current_operation["scraps"].append({"item": "", "count": 1})

# عکس‌ها
st.subheader("عکس‌ها")
st.session_state.current_operation["photos"]["before"] = st.file_uploader("عکس قبل")
st.session_state.current_operation["photos"]["during"] = st.file_uploader("عکس حین")
st.session_state.current_operation["photos"]["after"] = st.file_uploader("عکس بعد")

# دکمه‌ها
if st.button("افزودن عملیات"):
    st.session_state.current_address["operations"].append(st.session_state.current_operation.copy())
    st.session_state.current_operation = {
        "operation": "",
        "count": 1,
        "consumables": [{"item": "", "count": 1}],
        "scraps": [{"item": "", "count": 1}],
        "photos": {"before": None, "during": None, "after": None}
    }
    st.success("عملیات اضافه شد.")

if st.button("پایان عملیات و ذخیره آدرس"):
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
    st.success("آدرس ذخیره شد.")

# تولید PDF
if st.button("دانلود PDF گزارش‌ها"):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setFont("Helvetica", 12)
    width, height = A4
    y = height - 50

    for addr in st.session_state.activities:
        pdf.drawString(50, y, f"آدرس: {addr['address']}")
        y -= 20
        for op in addr["operations"]:
            pdf.drawString(70, y, f"- {op['operation']} × {op['count']}")
            y -= 20
        y -= 20

    pdf.save()
    buffer.seek(0)
    st.download_button("دانلود فایل PDF", buffer, file_name="report.pdf", mime="application/pdf")
