import re

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ENGLISH_DIGITS = "0123456789"


def normalize_price(value):
    """
    ورودی را (چه رشته چه عدد) به یک عدد صحیح تومان تبدیل می‌کند.
    """
    if isinstance(value, (int, float)):
        return int(value)

    text = str(value)

    # تبدیل ارقام فارسی به انگلیسی
    translation = str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)
    text = text.translate(translation)

    # حذف هر چیزی غیر از رقم
    digits_only = re.sub(r'[^\d]', '', text)

    if not digits_only:
        return None

    return int(digits_only)


def rial_to_toman(rial_value):
    """تبدیل ریال به تومان (تقسیم بر ۱۰)"""
    return int(rial_value) // 10