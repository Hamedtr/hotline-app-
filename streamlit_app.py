import streamlit as st
import json
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from twilio.rest import Client

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
st.title("📋 ثبت اطلاعات روزانه گروه")
group_name = st.text_input("نام گروه:")
activity_details = st.text_area("جزئیات فعالیت‌های روزانه:")
comments = st.text_area("نظرات و یادداشت‌ها:")

if st.button("✅ ثبت اطلاعات روزانه"):
    date = datetime.now().strftime("%Y-%m-%d")
    daily_entry = {
        "date": date,
        "group_name": group_name,
        "activity_details": activity_details,
        "comments": comments
    }
    st.session_state.daily_data.append(daily_entry)
    st.success("✅ اطلاعات روزانه ثبت شد.")

# نمایش اطلاعات ثبت شده
if st.session_state.daily_data:
    st.markdown("### اطلاعات ثبت‌شده روز:")
    for entry in st.session_state.daily_data:
        st.markdown(f"""
        **تاریخ:** {entry['date']}  
        **گروه:** {entry['group_name']}  
        **جزئیات فعالیت:** {entry['activity_details']}  
        **نظرات:** {entry['comments']}  
        ---
        """)

# فرم عملیات برای یک آدرس
st.markdown("---")
st.title("🏗️ ثبت عملیات برای یک آدرس")
st.session_state.current_address["work_type"] = st.selectbox("نوع کار", ["طرح شخصی", "طرح اداری", "اتفاقاتی", "تعمیرات پیشگیرانه"])
st.session_state.current_address["request_code"] = st.text_input("شماره درخواست خط گرم")
st.session_state.current_address["related_department"] = st.text_input("امور مربوطه")
st.session_state.current_address["address"] = st.text_input("آدرس محل کار")
st.session_state.current_address["groups"] = st.text_input("نام گروه‌های همکار")
st.session_state.current_address["line_station"] = st.text_input("شماره خط و ایستگاه")
st.session_state.current_address["code"] = st.text_input("کد تضمین")

st.markdown("### 🔧 شرح عملیات جدید")
col_op1, col_op2 = st.columns([3, 1])
st.session_state.current_operation["operation"] = col_op1.selectbox(
    "شرح فعالیت", ["--- انتخاب کنید ---"] + activity_options, index=0
)
st.session_state.current_operation["count"] = col_op2.number_input("تعداد", min_value=1, step=1)

# اقلام مصرفی
st.markdown("#### 📦 اقلام مصرفی")
for i, item in enumerate(st.session_state.current_operation["consumables"]):
    col1, col2 = st.columns([3, 1])
    item["item"] = col1.selectbox(f"کالای مصرفی {i+1}", ["--- انتخاب کنید ---"] + consumables, key=f"cons_item_{i}")
    item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"cons_count_{i}")
if st.button("➕ افزودن کالای مصرفی"):
    st.session_state.current_operation["consumables"].append({"item": "", "count": 1})

# اقلام برگشتی
st.markdown("#### ♻️ اقلام برگشتی")
for i, item in enumerate(st.session_state.current_operation["scraps"]):
    col1, col2 = st.columns([3, 1])
    item["item"] = col1.selectbox(f"کالای برگشتی {i+1}", ["--- انتخاب کنید ---"] + scraps, key=f"scr_item_{i}")
    item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"scr_count_{i}")
if st.button("➕ افزودن کالای برگشتی"):
    st.session_state.current_operation["scraps"].append({"item": "", "count": 1})

# عکس‌ها
st.markdown("#### 🖼️ عکس‌ها")
st.session_state.current_operation["photos"]["before"] = st.file_uploader("عکس قبل")
st.session_state.current_operation["photos"]["during"] = st.file_uploader("عکس حین")
st.session_state.current_operation["photos"]["after"] = st.file_uploader("عکس بعد")

# دکمه‌ها
col1, col2 = st.columns(2)
if col1.button("📌 افزودن عملیات"):
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
    st.success("✅ عملیات ثبت شد.")

if col2.button("✅ نهایی‌سازی آدرس"):
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
    st.success("✅ آدرس نهایی شد.")

# ساخت PDF ساده از عملیات‌ها
def create_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 12)
    width, height = A4
    y = height - 50
    for address in data:
        c.drawString(50, y, f"آدرس: {address['address']}")
        y -= 20
        for op in address["operations"]:
            c.drawString(60, y, f"- {op['operation']} x{op['count']}")
            y -= 20
        y -= 30
    c.save()
    buffer.seek(0)
    return buffer

if st.button("📄 دانلود PDF"):
    if st.session_state.activities:
        pdf = create_pdf(st.session_state.activities)
        st.download_button("⬇️ دانلود فایل", data=pdf, file_name="report.pdf", mime="application/pdf")

# ارسال به واتس‌اپ با Twilio
def send_whatsapp(body, to_number):
    account_sid = 'your_sid'
    auth_token = 'your_token'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=body,
        from_='whatsapp:+14155238886',
        to=to_number
    )
    return message.sid

if st.button("📤 ارسال خلاصه به واتس‌اپ"):
    if st.session_state.activities:
        summary = ""
        for addr in st.session_state.activities:
            summary += f"آدرس: {addr['address']}\n"
            for op in addr["operations"]:
                summary += f" - {op['operation']} × {op['count']}\n"
            summary += "----------------------\n"
        sid = send_whatsapp(summary, "whatsapp:+989123456789")
        st.success(f"پیام ارسال شد. SID: {sid}")
