from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def check_url_status(url_address):

    result = {
        'status_code': None,
        'h1': "",
        'title': "",
        'description': ""
    }

    try:
        response = requests.get(url_address, timeout=5, allow_redirects=True)
        result['status_code'] = response.status_code
        html = response.text

        # Парсим страницу сайта, который проверяем
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            result['h1'] = soup.h1.text[:255] if soup.h1 else ""
            result['title'] = soup.title.text[:255] if soup.title else ""

            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                if meta_tag.get('content'):
                    result['description'] = meta_tag.get('content')[:255]

        if 400 <= result['status_code'] < 600:
            result['status_code'] = None

    # На всякий случай, если потом потребуется дополнительная обработка
    except requests.RequestException:
        result['status_code'] = None

    return result


def get_url_host(url_address):
    try:
        parsed_url = urlparse(url_address)

        if parsed_url.scheme and parsed_url.netloc:
            normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        else:
            normalized_url = url_address
    except Exception:
        normalized_url = url_address

    return normalized_url