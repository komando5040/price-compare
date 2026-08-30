import re
from urllib.parse import unquote
from bs4 import BeautifulSoup
from scrapers.base import fetch

SOURCE_NAME = "تکنولایف"
SOURCE_TYPE = "shop"

PRICE_PATTERN = re.compile(r'^[\d,]{7,}$')
MAX_PAGES = 2  # خواندن صفحه اول و دوم نتایج


def extract_title_from_url(href):
    decoded = unquote(href)
    path_part = decoded.split('?')[0]
    slug = path_part.rstrip('/').split('/')[-1]
    title = slug.replace('-', ' ').strip()
    return title


def search(query):
    results = []
    seen_links = set()

    for page in range(1, MAX_PAGES + 1):
        url = "https://www.technolife.com/product/list/search"
        params = {"keywords": query, "page": page}

        try:
            resp = fetch(url, params=params, timeout=8, max_retries=1)
            if resp.status_code != 200:
                print(f"تکنولایف صفحه {page}: کد وضعیت غیرمنتظره {resp.status_code}")
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            price_candidates = soup.find_all(string=PRICE_PATTERN)

            page_had_new_result = False

            for price_text in price_candidates:
                parent = price_text.parent
                current = parent
                link_tag = None

                for _ in range(8):
                    if current is None:
                        break
                    if hasattr(current, "find"):
                        found = current.find("a", href=True)
                        if found:
                            link_tag = found
                            break
                    current = current.parent

                if not link_tag:
                    continue

                href = link_tag.get("href")
                if href in seen_links:
                    continue
                seen_links.add(href)
                page_had_new_result = True

                try:
                    price_number = int(price_text.strip().replace(",", ""))
                except ValueError:
                    continue

                title = extract_title_from_url(href)

                results.append({
                    "title": title,
                    "price": price_number,
                    "seller": SOURCE_NAME,
                    "link": "https://www.technolife.com" + href,
                    "source_type": SOURCE_TYPE,
                })

            # اگر صفحه‌ی جدید هیچ نتیجه‌ی جدیدی نداشت، دیگر صفحه‌ی بعد را نخوان
            if not page_had_new_result:
                break

        except Exception as e:
            print(f"خطا در اسکرپر تکنولایف صفحه {page}: {e}")
            break

    return results