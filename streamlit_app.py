import streamlit as st
import jdatetime
import json
from datetime import datetime

# بارگذاری فایل‌های داده
with open("activities.json", "r", encoding="utf-8") as f:
    activity_options = json.load(f)

with open("consumables.json", "r", encoding="utf-8") as f:
    consumables = json.load(f)

with open("scraps.json", "r", encoding="utf-8") as f:
    scraps = json.load(f)

# تنظیمات اولیه برنامه
st.set_page_config(page_title="Hotline 2.0", layout="centered")

# وضعیت اولیه session
defaults = {
    "user_code": None,
    "personnel": {},
    "activities": [],
    "locations": [{"line_station": "", "code": ""}],
    "gps": {"lat": "29.6100", "lon": "52.5310", "accuracy": "±10m"},
    "consumable_items": [{"item": "", "count": 1}],
    "scrap_items": [{"item": "", "count": 1}],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# فرم ورود
def show_login():
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
                st.warning("لطفاً تمام فیلدهای نام‌ها را کامل وارد کنید.")
            else:
                st.session_state.user_code = "ok"
                st.session_state.personnel = {
                    "supervisor": supervisor,
                    "person2": p2,
                    "person3": p3,
                    "driver": driver,
                }

# فرم ثبت عملیات
def show_activity_form():
    st.subheader("افزودن عملیات جدید")

    with st.form("meta_form", clear_on_submit=False):
        st.markdown("### اطلاعات محل اجرا")
        work_type = st.selectbox("نوع کار", ["طرح شخصی", "طرح اداری", "اتفاقاتی", "تعمیرات پیشگیرانه"])
        work_unit = st.text_input("شماره درخواست خط گرم")
        related_dept = st.text_input("امور مربوطه")
        address = st.text_input("آدرس محل کار")
        group_names = st.text_input("نام گروه‌های همکار")

        for i, loc in enumerate(st.session_state.locations):
            col1, col2 = st.columns([3, 2])
            loc["line_station"] = col1.text_input(f"شماره خط و ایستگاه ({i+1})", value=loc["line_station"], key=f"line_station_{i}")
            loc["code"] = col2.text_input(f"کد تضمین ({i+1})", value=loc["code"], key=f"code_{i}")

        if st.form_submit_button("+ افزودن خط جدید"):
            st.session_state.locations.append({"line_station": "", "code": ""})

    st.markdown(f"**موقعیت فعلی:** عرض {st.session_state.gps['lat']}، طول {st.session_state.gps['lon']} ({st.session_state.gps['accuracy']})")

    # دکمه‌های افزودن کالا (از نظر ظاهری داخل فرم)
    st.markdown("### اقلام مصرفی")
    col1, col2 = st.columns(2)
    if col1.button("ثبت کالای مصرفی جدید"):
        st.session_state.consumable_items.append({"item": "", "count": 1})
    if col2.button("ثبت کالای برگشتی جدید"):
        st.session_state.scrap_items.append({"item": "", "count": 1})

    with st.form("act_form", clear_on_submit=True):
        st.subheader("جزییات اجرا")
        op = st.selectbox("شرح فعالیت", activity_options)

        st.markdown("### اقلام مصرفی")
        cons_data = []
        for i, item in enumerate(st.session_state.consumable_items):
            col1, col2 = st.columns([3, 1])
            item["item"] = col1.selectbox(f"کالای مصرفی {i+1}", options=consumables, key=f"cons_item_{i}")
            item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"cons_count_{i}")
            cons_data.append(item)

        st.markdown("### اقلام برگشتی")
        scrp_data = []
        for i, item in enumerate(st.session_state.scrap_items):
            col1, col2 = st.columns([3, 1])
            item["item"] = col1.selectbox(f"کالای برگشتی {i+1}", options=scraps, key=f"scr_item_{i}")
            item["count"] = col2.number_input("تعداد", min_value=1, step=1, key=f"scr_count_{i}")
            scrp_data.append(item)

        p1 = st.file_uploader("عکس قبل")
        p2 = st.file_uploader("عکس حین")
        p3 = st.file_uploader("عکس بعد")

        if st.form_submit_button("ثبت فعالیت جدید"):
            if not (p1 and p2 and p3):
                st.error("لطفاً هر سه عکس قبل، حین و بعد را بارگذاری کنید.")
            else:
                st.session_state.activities.append({
                    "operation": op,
                    "work_type": work_type,
                    "request_code": work_unit,
                    "related_department": related_dept,
                    "address": address,
                    "groups": group_names,
                    "locations": st.session_state.locations.copy(),
                    "gps": st.session_state.gps,
                    "consumables": cons_data,
                    "scraps": scrp_data,
                    "photos": {
                        "before": p1.name,
                        "during": p2.name,
                        "after": p3.name
                    },
                    "datetime": str(datetime.now())
                })
                st.success("عملیات جدید ثبت شد.")
                st.session_state.locations = [{"line_station": "", "code": ""}]
                st.session_state.gps = {"lat": "29.6100", "lon": "52.5310", "accuracy": "±10m"}
                st.session_state.consumable_items = [{"item": "", "count": 1}]
                st.session_state.scrap_items = [{"item": "", "count": 1}]
                st.experimental_rerun()

# پایان روز و خروجی
def show_end_page():
    st.title("پایان روز")
    for i, act in enumerate(st.session_state.activities, 1):
        st.markdown(f"### عملیات {i}: نوع کار: {act['work_type']}")
    if st.button("تایید و دانلود گزارش"):
        data = {
            "date": jdatetime.date.today().isoformat(),
            "personnel": st.session_state.personnel,
            "activities": st.session_state.activities
        }
        st.download_button("دانلود فایل JSON", json.dumps(data, ensure_ascii=False), file_name="hotline_v2.json")

# کنترل مسیر اصلی
if st.session_state.user_code is None:
    show_login()
else:
    page = st.sidebar.radio("منو", ["ثبت عملیات", "پایان روز"])
    if page == "ثبت عملیات":
        show_activity_form()
    else:
        show_end_page()
