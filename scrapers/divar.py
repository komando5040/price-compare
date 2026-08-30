import requests
import re
from scrapers.base import DEFAULT_HEADERS

SOURCE_NAME = "دیوار"
SOURCE_TYPE = "personal_ad"  # آگهی شخصی/دست‌دوم - باید برچسب بخورد

API_URL = "https://api.divar.ir/v8/postlist/w/search"


def extract_price_number(price_text):
    """تبدیل رشته‌ی فارسی قیمت (مثل '۸۰,۰۰۰,۰۰۰ تومان') به عدد صحیح"""
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translation = str.maketrans(persian_digits, english_digits)
    text = price_text.translate(translation)
    digits_only = re.sub(r'[^\d]', '', text)
    return int(digits_only) if digits_only else None


def search(query):
    results = []

    payload = {
        "city_ids": ["1"],
        "source_view": "SEARCH",
        "disable_recommendation": False,
        "map_state": {"camera_info": {"bbox": {}}},
        "previous_place_ids": [],
        "search_data": {
            "form_data": {
                "data": {
                    "category": {"str": {"value": "ROOT"}}
                }
            },
            "query": query,
        }
    }

    try:
        resp = requests.post(
            API_URL,
            headers={**DEFAULT_HEADERS, "Content-Type": "application/json"},
            json=payload,
            timeout=8,
        )

        if resp.status_code != 200:
            print(f"دیوار: کد وضعیت غیرمنتظره {resp.status_code}")
            return results

        data = resp.json()
        widgets = data.get("list_widgets", [])

        for w in widgets:
            if w.get("widget_type") != "POST_ROW":
                continue

            item = w.get("data", {})
            title = item.get("title")
            price_text = item.get("middle_description_text", "")
            token = item.get("action", {}).get("payload", {}).get("token")

            if not (title and token):
                continue

            # قیمت‌های توافقی یا غیرعددی رد شوند
            price = extract_price_number(price_text)
            if price is None:
                continue

            results.append({
                "title": title,
                "price": price,
                "seller": SOURCE_NAME,
                "link": f"https://divar.ir/v/-/{token}",
                "source_type": SOURCE_TYPE,
                "condition": item.get("top_description_text", ""),
            })

    except Exception as e:
        print(f"خطا در اسکرپر دیوار: {e}")

    return results