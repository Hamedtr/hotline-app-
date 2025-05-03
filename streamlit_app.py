import streamlit as st
import jdatetime
import json
from datetime import datetime

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
        op = st.selectbox("نوع عملیات", ["باز و بسته کردن جمپر", "استفاده از بالابر", "تعویض مقره"])
        line = st.text_input("شماره خط")
        station = st.text_input("نام ایستگاه")
        code = st.text_input("کد تضمین")
        work_type = st.text_input("نوع کار")
        cons_items = st.text_area("اقلام مصرفی (مثلاً: پیچ 200 - 3)")
        scrp_items = st.text_area("اقلام برگشتی (مثلاً: برقگیر سرامیکی - 1)")
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
                "consumables": cons_items,
                "scraps": scrp_items,
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

if st.session_state.user_code is None:
    show_login()
else:
    page = st.sidebar.radio("منو", ["ثبت عملیات", "پایان روز"])
    if page == "ثبت عملیات":
        show_activity_form()
    else:
        show_end_page()