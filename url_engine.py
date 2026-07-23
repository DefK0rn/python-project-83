import requests


def check_url_status(url_address):
    status_code = None
    try:
        response = requests.head(url_address, timeout=5, allow_redirects=True)
        status_code = response.status_code

        if 400 <= status_code < 600:
            status_code = None

    # На всякий случай, если потом потребуется дополнительная обработка
    except requests.RequestException:
        return None

    return status_code