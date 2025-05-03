
import streamlit as st
import jdatetime
import json
from datetime import datetime

# بارگذاری لیست فعالیت‌ها از فایل JSON
with open("activities_cleaned_final.json", "r", encoding="utf-8") as f:
    activity_options = json.load(f)

st.set_page_config(page_title="Hotline 2.0", layout="centered")

if "user_code" not in st.session_state:
    st.session_state.user_code = None
if "personnel" not in st.session_state:
    st.session_state.personnel = {}
if "activities" not in st.session_state:
    st.session_state.activities = []
if "locations" not in st.session_state:
    st.session_state.locations = [{"line_station": "", "code": ""}]
if "gps" not in st.session_state:
    st.session_state.gps = {"lat": "", "lon": "", "accuracy": ""}

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

    with st.form("meta_form"):
        st.markdown("### اطلاعات محل اجرا")
        for i, loc in enumerate(st.session_state.locations):
            col1, col2 = st.columns([3, 2])
            loc["line_station"] = col1.text_input(f"شماره خط و ایستگاه ({i+1})", value=loc["line_station"], placeholder="مثال: 301قرآن", key=f"line_station_{i}")
            loc["code"] = col2.text_input(f"کد تضمین ({i+1})", value=loc["code"], key=f"code_{i}")
        if st.form_submit_button("+ افزودن خط جدید"):
            st.session_state.locations.append({"line_station": "", "code": ""})

    # نمایش مکان جی‌پی‌اس فرضی (به‌جای داده واقعی)
    st.markdown("**موقعیت مکانی (مثال):**")
    st.session_state.gps = {
        "lat": "29.6100",
        "lon": "52.5310",
        "accuracy": "±10m"
    }
    st.info(f"موقعیت فعلی: عرض {st.session_state.gps['lat']}، طول {st.session_state.gps['lon']} ({st.session_state.gps['accuracy']})")

    with st.form("act_form", clear_on_submit=True):
        st.markdown("### اطلاعات عملیات")
        op = st.selectbox("شرح فعالیت", activity_options)
        work_type = st.selectbox("نوع کار", ["طرح شخصی", "طرح اداری", "اتفاقاتی", "تعمیرات پیشگیرانه"])
        cons_items = st.text_area("اقلام مصرفی (مثلاً: پیچ 200 - 3)")
        scrp_items = st.text_area("اقلام برگشتی (مثلاً: برقگیر سرامیکی - 1)")
        p1 = st.file_uploader("عکس قبل")
        p2 = st.file_uploader("عکس حین")
        p3 = st.file_uploader("عکس بعد")
        submit = st.form_submit_button("ثبت عملیات")
        if submit and p1 and p2 and p3:
            st.session_state.activities.append({
                "operation": op,
                "work_type": work_type,
                "locations": st.session_state.locations.copy(),
                "gps": st.session_state.gps,
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
        st.markdown(f"### عملیات {i}: {act['operation']} - نوع کار: {act['work_type']}")

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
