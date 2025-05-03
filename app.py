
import streamlit as st
import jdatetime
import json
from datetime import datetime

# Load activity list from JSON
with open("activities_cleaned_final.json", encoding="utf-8") as f:
    operations = json.load(f)

consumables = [
    "12*40", "اسپیسر", "اشپیل", "پیچ", "پیچ 40*12", "پیچ دوسر350", "پیچ دوسر400", "پیچ200", "پیچ250", "پیچ300",
    "پیچ350", "پیچ400", "پیچ450", "پیچ450دوسر", "پیچ5 سانتی", "پیچ500", "تسمه", "جمپرگیر", "راس تیری",
    "سیم باندینگ", "سیم مسی25", "سیم120 روکشدار", "سیم50 روکشدار", "سیم70 روکشدار", "کابل مسی25",
    "کابلشو بیمتال120", "کابلشو بیمتال50", "کابلشو بیمتال70", "کابلشو مسی25", "کانکتورشکافدار35-16",
    "کانکتورمسی", "کاور برقگیر", "کاور بوشینگ", "کاور جرقه گیر", "کاور سوزنی پلیمری", "کاور سوزنی سرامیکی",
    "کاور کات اوت", "کاور کلمپ", "کراس آرم2.44", "کرپی400", "کرپی450", "کلمپ بیمتال", "کلمپ جمپر",
    "مقره بشقابی سرامیکی", "مقره بشقابی پلیمری", "مقره جمپرگیر", "مقره سوزنی سرامیکی", "مقره سوزنی پلیمری",
    "مهره اضاف", "مهره چشمی", "واشرمربع"
]

scraps = [
    "12*40", "اسپیسر", "برقگیر پلیمری", "برقگیر سرامیکی", "پیچ200", "پیچ250", "پیچ300", "پیچ350", "پیچ400",
    "تسمه", "راس تیر", "زین هات لاین", "کلمپ هات لاین", "سیم روکشدار120", "سیم روکشدار50", "سیم روکشدار70",
    "سیم مسی16", "سیم مهار", "سیم120 بدون روکش", "سیم35بدون روکش", "سیم50بدون روکش", "سیم70بدون روکش",
    "کات اوت پلیمری", "کات اوت تیغه ای", "کات اوت سرامیکی", "کاور سوزنی پلیمری", "کاور سوزنی سرامیکی",
    "کاور کات اوت", "کاوربوشینگ", "کراس آرم2.44", "کراس آرم 2متری", "کلمپ جمپر", "کلمپ هات لاین",
    "مقره اتکایی", "مقره بشقابی پلیمری", "مقره بشقابی سرامیکی", "مقره جمپرگیر", "مقره سوزنی پلیمری",
    "مقره سوزنی سرامیکی+میله مقره"
]

st.set_page_config(page_title="Hotline 2.0", layout="centered")

if "user_code" not in st.session_state:
    st.session_state.user_code = None
if "personnel" not in st.session_state:
    st.session_state.personnel = {}
if "activities" not in st.session_state:
    st.session_state.activities = []

def show_login():
    st.title("ورود روزانه")
    today = jdatetime.date.today().strftime("%A %d %B %Y")
    st.markdown(f"### امروز: {today}")
    with st.form("login_form"):
        supervisor = st.text_input("نام سرپرست")
        p2 = st.text_input("نفر دوم")
        p3 = st.text_input("نفر سوم")
        driver = st.text_input("راننده")
        submitted = st.form_submit_button("شروع ثبت")
        if submitted:
            st.session_state.user_code = "ok"
            st.session_state.personnel = {
                "supervisor": supervisor,
                "person2": p2,
                "person3": p3,
                "driver": driver
            }

def show_activity_form():
    st.subheader("افزودن عملیات جدید")
    with st.form("act_form", clear_on_submit=True):
        op = st.selectbox("نوع عملیات", operations)
        line = st.text_input("شماره خط")
        station = st.text_input("نام ایستگاه")
        code = st.text_input("کد تضمین")
        work_type = st.selectbox("نوع کار", ["طرح شخصی", "طرح اداری", "اتفاقاتی", "تعمیرات پیشگیرانه"])
        address = st.text_input("آدرس محل اجرا")
        request_number = st.text_input("شماره درخواست خط گرم")

        st.markdown("### اقلام مصرفی")
        cons_data = []
        for i in range(2):
            c_item = st.selectbox(f"کالای مصرفی {i+1}", options=consumables, key=f"cons{i}")
            c_count = st.number_input(f"تعداد", min_value=1, step=1, key=f"cons_count{i}")
            cons_data.append({"item": c_item, "count": c_count})

        st.markdown("### اقلام برگشتی")
        scrp_data = []
        for i in range(2):
            s_item = st.selectbox(f"کالای برگشتی {i+1}", options=scraps, key=f"scr{i}")
            s_count = st.number_input(f"تعداد ", min_value=1, step=1, key=f"scr_count{i}")
            scrp_data.append({"item": s_item, "count": s_count})

        p1 = st.file_uploader("عکس قبل")
        p2 = st.file_uploader("عکس حین")
        p3 = st.file_uploader("عکس بعد")
        submit = st.form_submit_button("ثبت عملیات")

        if submit and p1 and p2 and p3:
            st.session_state.activities.append({
                "operation": op,
                "line": line,
                "station": station,
                "code": code,
                "work_type": work_type,
                "address": address,
                "request_number": request_number,
                "consumables": cons_data,
                "scraps": scrp_data,
                "photos": {
                    "before": p1.name,
                    "during": p2.name,
                    "after": p3.name
                },
                "datetime": str(datetime.now())
            })
            st.success("عملیات ثبت شد.")

def show_end_page():
    st.title("پایان روز")
    for i, act in enumerate(st.session_state.activities, 1):
        st.markdown(f"### عملیات {i}: {act['operation']} - خط {act['line']}")

    if st.button("تایید و دانلود گزارش"):
        data = {
            "date": jdatetime.date.today().isoformat(),
            "personnel": st.session_state.personnel,
            "activities": st.session_state.activities
        }
        st.download_button("دانلود فایل JSON", json.dumps(data, ensure_ascii=False), file_name="hotline_v2.json")

# Page flow
if st.session_state.user_code is None:
    show_login()
else:
    page = st.sidebar.radio("منو", ["ثبت عملیات", "پایان روز"])
    if page == "ثبت عملیات":
        show_activity_form()
    else:
        show_end_page()
