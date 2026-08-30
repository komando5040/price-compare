import re

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ENGLISH_DIGITS = "0123456789"
DIGIT_TRANSLATION = str.maketrans(PERSIAN_DIGITS, ENGLISH_DIGITS)

BRAND_ALIASES = {
    "poco": ["پوکو", "pico"],
    "redmi": ["ردمی"],
    "xiaomi": ["شیائومی"],
    "samsung": ["سامسونگ"],
    "apple": ["اپل"],
    "iphone": ["آیفون"],
    "huawei": ["هواوی"],
    "honor": ["آنر", "انر"],
    "oppo": ["اوپو"],
    "vivo": ["ویوو"],
    "nokia": ["نوکیا"],
    "realme": ["ریلمی"],
    "oneplus": ["وان پلاس"],
    "daewoo": ["دوو"],
    "lg": ["ال جی", "ال‌جی"],
    "snowa": ["اسنوا"],
}

NEGATIVE_WORDS = [
    "قاب", "کاور", "محافظ", "گلس", "لوازم جانبی", "قطعه", "تعمیر",
    "برچسب", "شارژر", "کابل", "هندزفری", "پاوربانک", "استند",
    "بند", "کیف", "تاچ", "ال سی دی", "ال‌سی‌دی", "باتری", "درب پشت", "lcd"
]


def normalize_digits(text):
    return text.translate(DIGIT_TRANSLATION)


def extract_keywords(query):
    normalized = normalize_digits(query)
    return [w.lower() for w in normalized.split() if len(w) > 1]


def is_numeric_token(token):
    return token.isdigit()


def contains_number_isolated(number, text):
    """
    بررسی می‌کند آیا 'number' در 'text' هست، طوری‌که به یک عدد دیگر نچسبیده باشد
    (یعنی '830' در '8300' یا '9830' قبول نمی‌شود، اما '830w' یا 'lm-830s' قبول می‌شود
    چون حرف بعدی رقم نیست).
    """
    pattern = r'(?<!\d)' + re.escape(number) + r'(?!\d)'
    return bool(re.search(pattern, text))


def contains_whole_word(word, text):
    """برای کلمات متنی (نه اعداد) - مرز کلمه استاندارد"""
    pattern = r'\b' + re.escape(word) + r'\b'
    return bool(re.search(pattern, text))


def keyword_in_title(keyword, title_lower):
    if keyword in title_lower:
        return True
    aliases = BRAND_ALIASES.get(keyword, [])
    return any(alias in title_lower for alias in aliases)


def is_relevant(title, query):
    title_normalized = normalize_digits(title.lower())
    query_lower = normalize_digits(query.lower())
    keywords = extract_keywords(query)

    if not keywords:
        return True

    numeric_keywords = [kw for kw in keywords if is_numeric_token(kw)]
    text_keywords = [kw for kw in keywords if not is_numeric_token(kw)]

    for num_kw in numeric_keywords:
        if not contains_number_isolated(num_kw, title_normalized):
            return False

    if text_keywords:
        matched = sum(1 for kw in text_keywords if keyword_in_title(kw, title_normalized))
        match_ratio = matched / len(text_keywords)
        if match_ratio < 0.6:
            return False

    for neg in NEGATIVE_WORDS:
        if contains_whole_word(neg, title_normalized) and neg not in query_lower:
            return False

    return True