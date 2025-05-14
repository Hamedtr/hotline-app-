import streamlit as st
import json
from datetime import datetime
from twilio.rest import Client
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# بارگذاری فایل‌های داده
with open("activities.json", "r", encoding="utf-8") as f:
    activity_options = json.load(f)
with open("consumables.json", "r", encoding="utf-8") as f:
    consumables = json.load(f)
with open("scraps.json", "r", encoding="utf-8") as f:
    scraps = json.load(f)

# برای ذخیره اطلاعات روزانه
if 'daily_data' not in st.session_state:
    st.session_state.daily_data = []

# برای ذخیره اطلاعات آدرس و عملیات‌ها
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

# بارگذاری تنظیمات Twilio
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
client = Client(account_sid, auth_token)

# تابع برای ارسال پیام واتس‌اپ
def send_whatsapp_message(body, to):
    message = client.messages.create(
        body=body,
        from_='whatsapp:+14155238886',  # شماره واتس‌اپ Twilio
        to=to
    )
    return message.sid

# تابع برای ایجاد PDF
def generate_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    
    # تنظیمات فونت و اندازه
    c.setFont("Helvetica", 12)
    
    # تنظیم محل نوشتن اطلاعات
    y_position = 800  # موقعیت عمودی برای نوشتن
    
    # نوشتن داده‌ها به فایل PDF
    c.drawString(50, y_position, f"تاریخ: {data['date']}")
    y_position -= 20
    c.drawString(50, y_position, f"گروه: {data['group_name']}")
    y_position -= 20
    c.drawString(50, y_position, f"جزئیات فعالیت: {data['activity_details']}")
    y_position -= 20
    c.drawString(50, y_position, f"نظرات: {data['comments']}")
    
    # ذخیره فایل PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

# فرم ثبت اطلاعات روزانه گروه
st.title("ثبت اطلاعات روزانه گروه")
group_name = st.text_input("نام گروه:")
activity_details = st.text_area("جزئیات فعالیت‌های روزانه:")
comments = st.text_area("نظرات و یادداشت‌ها:")

# دکمه ثبت اطلاعات روزانه
if st.button("ثبت اطلاعات روزانه"):
    date = datetime.now().strftime("%Y-%m-%d")
    daily_entry = {
        "date": date,
        "group_name": group_name,
        "activity_details": activity_details,
        "comments": comments
    }
    st.session_state.daily_data.append(daily_entry)
    st.success("اطلاعات روزانه ثبت شد!")

# نمایش اطلاعات ثبت شده
if st.session_state.daily_data:
    st.markdown("### اطلاعات ثبت شده:")
    for entry in st.session_state.daily_data:
        st.write(f"تاریخ: {entry['date']}, گروه: {entry['group_name']}")
        st.write(f"جزئیات فعالیت: {entry['activity_details']}")
        st.write(f"نظرات: {entry['comments']}")
        st.markdown("---")

# ارسال اطلاعات به واتس‌اپ
if st.button("ارسال داده‌ها به واتس‌اپ"):
    if st.session_state.daily_data:
        message_body = ""
        for entry in st.session_state.daily_data:
            message_body += f"تاریخ: {entry['date']}\n"
            message_body += f"گروه: {entry['group_name']}\n"
            message_body += f"جزئیات فعالیت: {entry['activity_details']}\n"
            message_body += f"نظرات: {entry['comments']}\n"
            message_body += "\n-------------------------\n"
        
        # شماره مقصد واتس‌اپ
        recipient_number = 'whatsapp:+989123456789'  # شماره خود را وارد کنید
        sid = send_whatsapp_message(message_body, recipient_number)
        st.success(f"پیام با SID: {sid} ارسال شد.")

# فرم اطلاعات آدرس
st.markdown("---")
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
    "شرح فعالیت", ["--- انتخاب کنید ---"] + activity_options, index=0
)
st.session_state.current_operation["count"] = col_op2.number_input("تعداد", min_value=1, step=1)

# اقلام مصرفی
st.markdown("#### اقلام مصرفی")
for i, item in enumerate(st.session_state.current_operation["consumables"]):
    col1, col2 = st.columns([3, 1])
    item["item"] = col1.selectbox(f"کالای مصرفی {i+1}", ["--- انتخاب کنید ---"] + consumables, key=f"cons_item_{i}")
    item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"cons_count_{i}")
if st.button("افزودن کالای مصرفی"):
    st.session_state.current_operation["consumables"].append({"item": "", "count": 1})

# اقلام برگشتی
st.markdown("#### اقلام برگشتی")
for i, item in enumerate(st.session_state.current_operation["scraps"]):
    col1, col2 = st.columns([3, 1])
    item["item"] = col1.selectbox(f"کالای برگشتی {i+1}", ["--- انتخاب کنید ---"] + scraps, key=f"scr_item_{i}")
    item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"scr_count_{i}")
if st.button("افزودن کالای برگشتی"):
    st.session_state.current_operation["scraps"].append({"item": "", "count": 1})

# عکس‌ها
st.markdown("#### عکس‌ها")
st.session_state.current_operation["photos"]["before"] = st.file_uploader("عکس قبل")
st.session_state.current_operation["photos"]["during"] = st.file_uploader("عکس حین")
st.session_state.current_operation["photos"]["after"] = st.file_uploader("عکس بعد")

# دکمه‌ها
col_add, col_finish = st.columns(2)

if col_add.button("افزودن عملیات"):
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
        "consumables": [{"item":
