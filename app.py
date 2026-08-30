import os
from flask import Flask, render_template, request
from scrapers import digikala, technolife, divar
from utils.price_normalizer import normalize_price
from utils.title_matcher import is_relevant
from utils.outlier_detector import flag_outliers
from utils.currency_fixer import correct_digikala_currency

app = Flask(__name__)


def get_filtered_results(scraper_module, query):
    try:
        raw_results = scraper_module.search(query)
    except Exception as e:
        print(f"خطا در اجرای اسکرپر {scraper_module.__name__}: {e}")
        return []

    filtered = [r for r in raw_results if is_relevant(r["title"], query)]
    for r in filtered:
        r["price"] = normalize_price(r["price"])
    return [r for r in filtered if r["price"]]


def search_all_sources(query):
    all_results = []
    all_results += get_filtered_results(digikala, query)
    all_results += get_filtered_results(technolife, query)
    all_results += get_filtered_results(divar, query)

    all_results = correct_digikala_currency(all_results)
    all_results = flag_outliers(all_results)
    all_results.sort(key=lambda r: r["price"])

    valid_prices = [r["price"] for r in all_results if not r.get("is_outlier")]
    cheapest_price = min(valid_prices) if valid_prices else None

    for r in all_results:
        r["is_cheapest"] = (r["price"] == cheapest_price) and not r.get("is_outlier")
        r["price_diff"] = (r["price"] - cheapest_price) if cheapest_price else 0

    return all_results


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    query = ""
    error_message = None

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            try:
                results = search_all_sources(query)
                if not results:
                    error_message = "نتیجه‌ای برای این عبارت جستجو پیدا نشد."
            except Exception as e:
                error_message = "خطایی رخ داد. لطفاً دوباره تلاش کنید."
                print(f"خطای کلی: {e}")
        else:
            error_message = "لطفاً نام کالا را وارد کنید."

    return render_template(
        "index.html",
        results=results,
        query=query,
        error_message=error_message,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)