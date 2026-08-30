def flag_outliers(results, threshold_multiplier=3):
    """
    قیمت‌هایی که بیش از threshold_multiplier برابر میانگین بقیه‌ی نتایج هستند
    را با یک پرچم هشدار مشخص می‌کند (به‌جای حذف کردن، فقط علامت‌گذاری).
    """
    if len(results) < 2:
        for r in results:
            r["is_outlier"] = False
        return results

    prices = [r["price"] for r in results]
    avg_price = sum(prices) / len(prices)

    for r in results:
        # میانگین را بدون خود این آیتم دوباره حساب می‌کنیم تا خودش میانگین را منحرف نکند
        other_prices = [p for p in prices if p != r["price"]]
        if other_prices:
            avg_others = sum(other_prices) / len(other_prices)
        else:
            avg_others = avg_price

        r["is_outlier"] = r["price"] > avg_others * threshold_multiplier

    return results 