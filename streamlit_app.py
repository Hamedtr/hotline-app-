import streamlit as st
import jdatetime
import json
from datetime import datetime

st.set_page_config(page_title="Hotline", layout="centered")

if "user_code" not in st.session_state:
    st.session_state.user_code = None
if "personnel" not in st.session_state:
    st.session_state.personnel = {}
if "records" not in st.session_state:
    st.session_state.records = []

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

def show_form():
    st.subheader("ثبت عملیات")
    st.markdown("### مشخصات پرسنل امروز:")
    for k, v in st.session_state.personnel.items():
        st.write(f"{k}: {v}")

    with st.form("form1"):
        op = st.text_input("عنوان عملیات")
        con = st.text_input("قلم مصرفی")
        scr = st.text_input("قلم برگشتی")
        p1 = st.file_uploader("عکس قبل")
        p2 = st.file_uploader("عکس حین")
        p3 = st.file_uploader("عکس بعد")
        sub = st.form_submit_button("ثبت عملیات")
        if sub and p1 and p2 and p3:
            st.session_state.records.append({
                "operation": op,
                "consumable": con,
                "scrap": scr,
                "photos": {
                    "before": p1.name,
                    "during": p2.name,
                    "after": p3.name
                },
                "datetime": str(datetime.now())
            })
            st.success("ثبت شد")

def end_day():
    st.title("پایان روز")
    st.markdown("### عملیات‌های ثبت شده:")
    for i, rec in enumerate(st.session_state.records, 1):
        st.markdown(f"- {i}. {rec['operation']}")

    if st.button("تایید و ارسال"):
        full = {
            "personnel": st.session_state.personnel,
            "records": st.session_state.records
        }
        st.download_button("دانلود فایل گزارش", json.dumps(full, ensure_ascii=False), file_name="hotline.json")

if st.session_state.user_code is None:
    show_login()
else:
    pg = st.sidebar.radio("منو", ["ثبت عملیات", "پایان روز"])
    if pg == "ثبت عملیات":
        show_form()
    else:
        end_day()