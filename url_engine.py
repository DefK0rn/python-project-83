import requests
from bs4 import BeautifulSoup


def check_url_status(url_address):

    result = {}

    try:
        response = requests.get(url_address, timeout=5, allow_redirects=True)
        result['status_code'] = response.status_code
        html = response.text

        # Парсим страницу сайта, который проверяем
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            result['h1'] = soup.h1.text if soup.h1.text else ""
            result['title'] = soup.title.string if soup.title.string else ""

            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                result['description'] = meta_tag.get('content')

        if 400 <= result['status_code'] < 600:
            result['status_code'] = None

    # На всякий случай, если потом потребуется дополнительная обработка
    except requests.RequestException:
        result['status_code'] = None

    return result