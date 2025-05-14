import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

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

# بارگذاری داده‌ها و ایجاد PDF
if st.button("ایجاد PDF"):
    # اطلاعات نمونه به جای داده‌های ورودی
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "group_name": "گروه الف",
        "activity_details": "جزئیات فعالیت‌های گروه الف در این روز.",
        "comments": "نظرات و یادداشت‌ها برای فعالیت‌ها."
    }
    
    # ایجاد PDF
    pdf_file = generate_pdf(data)
    
    # دانلود PDF
    st.download_button(
        label="دانلود فایل PDF",
        data=pdf_file,
        file_name="operation_report.pdf",
        mime="application/pdf"
    )
