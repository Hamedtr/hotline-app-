import streamlit as st
import json
from datetime import datetime
import jdatetime

st.set_page_config(page_title="Hotline", page_icon="🧾", layout="centered")

if "user_code" not in st.session_state:
    st.session_state.user_code = None

def login():
    st.title("ورود به Hotline")
    user_code = st.text_input("کد اختصاصی کاربر", max_chars=20)
    if st.button("ورود"):
        if user_code:
            st.session_state.user_code = user_code
        else:
            st.warning("لطفاً یک کد وارد کنید")

def form_page():
    st.title("Hotline | ثبت روزانه")

    st.subheader("۱. اطلاعات پرسنل")
    supervisor = st.text_input("نام سرپرست")
    person2 = st.text_input("نام نفر دوم")
    person3 = st.text_input("نام نفر سوم")
    driver = st.text_input("نام راننده")

    st.subheader("۲. اقلام مصرفی")
    consumables = []
    with st.expander("افزودن اقلام مصرفی"):
        item = st.text_input("نام قلم")
        qty = st.number_input("تعداد", min_value=1, step=1)
        if st.button("افزودن به لیست مصرفی"):
            if item:
                st.session_state.setdefault("consumables", []).append({"name": item, "quantity": qty})
    
    st.write("اقلام ثبت‌شده:")
    for c in st.session_state.get("consumables", []):
        st.markdown(f"- {c['name']} ({c['quantity']})")

    st.subheader("۳. اقلام اسقاطی")
    scrap = []
    with st.expander("افزودن اقلام اسقاطی"):
        item_s = st.text_input("نام قلم اسقاطی")
        qty_s = st.number_input("تعداد اسقاطی", min_value=1, step=1, key="scrap_qty")
        if st.button("افزودن به لیست اسقاطی"):
            if item_s:
                st.session_state.setdefault("scraps", []).append({"name": item_s, "quantity": qty_s})
    
    st.write("اقلام اسقاطی ثبت‌شده:")
    for s in st.session_state.get("scraps", []):
        st.markdown(f"- {s['name']} ({s['quantity']})")

    if st.button("ثبت اطلاعات امروز"):
        today = jdatetime.date.today().isoformat()
        record = {
            "date": today,
            "user": st.session_state.user_code,
            "personnel": {
                "supervisor": supervisor,
                "person2": person2,
                "person3": person3,
                "driver": driver
            },
            "consumables": st.session_state.get("consumables", []),
            "scraps": st.session_state.get("scraps", [])
        }
        st.session_state.setdefault("records", []).append(record)
        st.success("ثبت شد!")

def end_day():
    st.title("پایان کار امروز")
    today = jdatetime.date.today().isoformat()
    records = [r for r in st.session_state.get("records", []) if r["date"] == today]
    
    if not records:
        st.info("هیچ رکوردی برای امروز ثبت نشده است.")
        return

    st.subheader("رکوردهای امروز:")
    for i, r in enumerate(records, 1):
        st.markdown(f"### فرم {i} - {r['personnel']['supervisor']}")

    if st.button("ساخت فایل JSON و ارسال"):
        json_data = json.dumps(records, ensure_ascii=False, indent=2)
        st.download_button("دانلود فایل JSON", data=json_data, file_name=f"hotline_{today}.json", mime="application/json")
        st.info("برای ارسال فایل به واتساپ، از دکمه دانلود استفاده و سپس در واتساپ ارسال کنید.")

if st.session_state.user_code is None:
    login()
else:
    page = st.sidebar.selectbox("انتخاب صفحه", ["ثبت جدید", "پایان کار امروز"])
    if page == "ثبت جدید":
        form_page()
    elif page == "پایان کار امروز":
        end_day()