from scrapers.base import fetch

SOURCE_NAME = "دیجی‌کالا"
SOURCE_TYPE = "shop"
MAX_PAGES = 2


def search(query):
    results = []
    url = "https://api.digikala.com/discovery/api/v2/search"

    for page in range(1, MAX_PAGES + 1):
        params = {"q": query, "page": page, "columns_per_page": 2}

        try:
            resp = fetch(url, params=params, timeout=8, max_retries=1)
            if resp.status_code != 200:
                print(f"دیجی‌کالا صفحه {page}: کد وضعیت غیرمنتظره {resp.status_code}")
                break

            data = resp.json()
            widgets = data["data"]["widgets"][0]["data"]["widgets"]

            if not widgets:
                break

            for w in widgets:
                product = w.get("data", {})
                title = product.get("title_fa")
                variant = product.get("default_variant", {})
                price_info = variant.get("price", {})
                price = price_info.get("selling_price")
                uri = product.get("url", {}).get("uri")

                if not (title and price and uri):
                    continue

                results.append({
                    "title": title,
                    "price": price,
                    "seller": SOURCE_NAME,
                    "link": "https://www.digikala.com" + uri,
                    "source_type": SOURCE_TYPE,
                })

        except Exception as e:
            print(f"خطا در اسکرپر دیجی‌کالا صفحه {page}: {e}")
            break

    return results