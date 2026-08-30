def correct_digikala_currency(results):
    """
    گاهی API دیجی‌کالا قیمت را به‌جای تومان، به ریال برمی‌گرداند (۱۰ برابر واقعی).
    این تابع با مقایسه با میانه‌ی قیمت‌های کل نتایج، این خطا را تشخیص و اصلاح می‌کند.
    """
    if len(results) < 2:
        return results

    prices = sorted(r["price"] for r in results)
    mid = len(prices) // 2
    median_price = prices[mid]

    if median_price <= 0:
        return results

    for r in results:
        if r.get("seller") != "دیجی‌کالا":
            continue

        # اگر قیمت بیش از ۵ برابر میانه بود، شاید ریال باشد
        if r["price"] > median_price * 5:
            corrected = r["price"] // 10
            # اگر بعد از تقسیم بر ۱۰، به بازه‌ی منطقی نزدیک میانه رسید، تایید می‌کنیم
            if median_price * 0.3 <= corrected <= median_price * 3:
                r["price"] = corrected
                r["currency_corrected"] = True

    return results