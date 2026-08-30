import requests
import time

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def fetch(url, params=None, timeout=8, max_retries=1):
    """
    دریافت یک صفحه/API با محدودیت تلاش مجدد و timeout مشخص.
    حداکثر یک بار retry، طبق قانون پروژه.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, params=params, timeout=timeout)
            return resp
        except requests.exceptions.RequestException as e:
            last_error = e
            time.sleep(0.5)
    raise last_error