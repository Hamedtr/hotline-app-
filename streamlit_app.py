import streamlit as st
import json
import jdatetime
from datetime import datetime

st.set_page_config(page_title="Hotline", page_icon="🧾", layout="centered")

if "user_code" not in st.session_state:
    st.session_state.user_code = None
if "records" not in st.session_state:
    st.session_state.records = []

# ورود کاربر
def login():
    st.title("ورود به Hotline")
    code = st.text_input("کد کاربر (مثلاً 101-Ahmadi)")
    if st.button("ورود"):
        if code:
            st.session_state.user_code = code
        else:
            st.warning("کد را وارد کنید")

# فرم ثبت جدید
def new_form():
    st.title("ثبت جدید")

    with st.form("hotline_form"):
        st.subheader("مشخصات پرسنل (فقط امروز)")
        supervisor = st.text_input("نام سرپرست")
        person2 = st.text_input("نفر دوم")
        person3 = st.text_input("نفر سوم")
        driver = st.text_input("راننده")

        st.subheader("اطلاعات عملیات")
        op_type = st.selectbox("نوع طرح", ["طرح شخصی", "طرح اداری", "اتفاقاتی", "تعمیرات پیشگیرانه"])
        request_number = st.text_input("شماره درخواست")

        st.subheader("سرپرستان مشترک")
        shared = st.text_area("نام‌ها (با ویرگول جدا کنید)")

        st.subheader("خطوط")
        line_data = st.text_area("شماره خط و ایستگاه (مثلاً: 12-ایستگاه حافظ\n34-ایستگاه سعدی)")

        line_load = st.text_input("بار خط")
        address = st.text_input("آدرس محل اجرا")

        st.subheader("نوع عملیات")
        operation_code = st.text_input("کد عملیات")
        operation_title = st.text_input("عنوان عملیات")
        quantity = st.number_input("تعداد", step=1, min_value=1)

        st.subheader("اقلام مصرفی")
        consumables = st.text_area("هر قلم در یک خط (مثلاً: پیچ 200 - 3)")

        st.subheader("اقلام اسقاطی")
        scraps = st.text_area("هر قلم در یک خط (مثلاً: برقگیر پلیمری - 1)")

        st.subheader("عکس‌ها")
        photo_before = st.file_uploader("عکس قبل از کار")
        photo_during = st.file_uploader("عکس حین کار")
        photo_after = st.file_uploader("عکس بعد از کار")

        submitted = st.form_submit_button("ثبت فرم")
        if submitted:
            today = jdatetime.date.today().isoformat()
            rec = {
                "user": st.session_state.user_code,
                "date": today,
                "datetime": str(datetime.now()),
                "personnel": {
                    "supervisor": supervisor,
                    "person2": person2,
                    "person3": person3,
                    "driver": driver
                },
                "type": op_type,
                "request_number": request_number,
                "shared_supervisors": [x.strip() for x in shared.split(",") if x.strip()],
                "lines": [{"line": x.split("-")[0], "station": x.split("-")[1]} for x in line_data.split("\n") if "-" in x],
                "line_load": line_load,
                "address": address,
                "operation": {"code": operation_code, "title": operation_title},
                "quantity": quantity,
                "consumables": parse_items(consumables),
                "scraps": parse_items(scraps),
                "photos": {
                    "before": photo_before.name if photo_before else None,
                    "during": photo_during.name if photo_during else None,
                    "after": photo_after.name if photo_after else None
                }
            }
            st.session_state.records.append(rec)
            st.success("فرم با موفقیت ثبت شد.")

def parse_items(text):
    result = []
    for line in text.split("\n"):
        parts = line.split("-")
        if len(parts) == 2:
            result.append({"name": parts[0].strip(), "quantity": int(parts[1].strip())})
    return result

# پایان روز و خروجی
def end_day():
    st.title("پایان کار امروز")
    today = jdatetime.date.today().isoformat()
    records = [r for r in st.session_state.records if r["date"] == today]

    if not records:
        st.info("هیچ رکوردی برای امروز ثبت نشده است.")
        return

    for i, rec in enumerate(records, 1):
        st.markdown(f"### فرم {i} | عملیات: {rec['operation']['title']}")

    json_data = json.dumps(records, ensure_ascii=False, indent=2)
    st.download_button("دانلود خروجی JSON", data=json_data, file_name=f"hotline_{today}.json", mime="application/json")

    number = st.text_input("شماره واتساپ (بدون 0، مثل 912...)")
    if st.button("ارسال در واتساپ"):
        link = f"https://wa.me/98{number}?text=فایل گزارش امروز آماده ارسال است."
        st.markdown(f"[ارسال واتساپ]({link})", unsafe_allow_html=True)

# اجرای اپ
if st.session_state.user_code is None:
    login()
else:
    option = st.sidebar.radio("انتخاب عملیات", ["ثبت جدید", "پایان کار امروز"])
    if option == "ثبت جدید":
        new_form()
    else:
        end_day()