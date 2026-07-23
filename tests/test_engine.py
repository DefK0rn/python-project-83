from unittest.mock import MagicMock

import requests

from url_engine import check_url_status


# Тест успешного ответа
def test_check_url_status_success(monkeypatch):

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
        <html>
            <title>Тест</title>
            <body>
                <h1>Заголовок</h1>
                <meta name='description' content='Описание'>
            </body>
        </html>
    """
    
    mock_head = MagicMock(return_value=mock_response)
    monkeypatch.setattr(requests, 'get', mock_head)

    result = check_url_status('https://ru.hexlet.io')
    
    assert result.get('status_code') == 200

    mock_head.assert_called_once_with(
        'https://ru.hexlet.io',
        timeout=5,
        allow_redirects=True
    )


# Тест ошибки клиента
def test_check_url_status_client_error(monkeypatch):

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = """
        <html>
            <title>Тест</title>
            <body>
                <h1>Заголовок</h1>
                <meta name='description' content='Описание'>
            </body>
        </html>
    """
    
    monkeypatch.setattr(requests, 'get', MagicMock(return_value=mock_response))

    result = check_url_status('https://ru.hexlet.io')
    
    assert result.get('status_code') is None


# Тест ошибки сервера
def test_check_url_status_server_error(monkeypatch):

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = """
        <html>
            <title>Тест</title>
            <body>
                <h1>Заголовок</h1>
                <meta name='description' content='Описание'>
            </body>
        </html>
    """
    
    monkeypatch.setattr(requests, 'get', MagicMock(return_value=mock_response))

    result = check_url_status('https://absent-site.xyz')
    
    assert result.get('status_code') is None


# Тест сетевого сбоя
def test_check_url_status_network_exception(monkeypatch):

    mock_head = MagicMock(side_effect=requests.RequestException)
    monkeypatch.setattr(requests, 'get', mock_head)

    result = check_url_status('https://absent-site.xyz')
    
    assert result.get('status_code') is None