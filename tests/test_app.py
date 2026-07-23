from unittest.mock import MagicMock

import page_analyzer
from page_analyzer import app
from page_analyzer.app import get_db_connection, repo


def test_app_at_package_level():

    assert hasattr(page_analyzer, 'app')
    
    assert 'app' in page_analyzer.__all__


def test_index_page_status():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200


def test_index_page_content():
    with app.test_client() as client:
        response = client.get('/')
        
        html = response.data.decode('utf-8')

        # Проверяем главный заголовок и описание
        assert '<title>Анализатор страниц</title>' in html
        assert 'Бесплатно проверяйте сайты на SEO-пригодность' in html
        
        # Проверяем, что форма отправляет POST-запрос
        assert 'action="/urls"' in html
        assert 'method="post"' in html
        
        # Проверяем наличие поля ввода для URL и кнопки отправки
        assert 'type="url"' in html
        assert 'name="url"' in html
        assert 'placeholder="https://www.example.com"' in html

        # Проверяем навигацию
        assert 'href="/urls"' in html
        assert 'Сайты' in html
        
        # Проверяем гиперссылку в подвале
        assert 'href="https://hexlet.io"' in html


# Проверяем подключение к базе данных
def test_get_db_connection_success(monkeypatch):
    fake_url = "postgresql://fake_user:fake_pass@localhost:5432/fake_db"
    monkeypatch.setenv("DATABASE_URL", fake_url)

    mock_connect = MagicMock()
    
    monkeypatch.setattr("psycopg.connect", mock_connect)

    get_db_connection()

    mock_connect.assert_called_once_with(fake_url)


# Проверяем странцу со списком сайтов
def test_urls_get_page(monkeypatch):
    mock_get_content = MagicMock(return_value=[
        {'id': 1, 'name': 'https://hexlet.io', 'created_at': '2026-02-20'},
        {'id': 2, 'name': 'https://google.com', 'created_at': '2026-02-21'}
    ])
    monkeypatch.setattr(repo, 'get_content', mock_get_content)

    with app.test_client() as client:
        response = client.get('/urls')
        assert response.status_code == 200
        
        html = response.data.decode('utf-8')
        assert 'https://hexlet.io' in html
        assert 'https://google.com' in html
        mock_get_content.assert_called_once()


# Проверяем страницу сайта по id
def test_urls_show_page_success(monkeypatch):
    mock_find_url_by_id = MagicMock(return_value={
        'id': 42, 
        'name': 'https://github.com', 
        'created_at': '2026-02-22'
    })
    monkeypatch.setattr(repo, 'find_url_by_id', mock_find_url_by_id)

    mock_find_checks_by_url = MagicMock(return_value=[])
    monkeypatch.setattr(repo, 'find_checks_by_url_id', mock_find_checks_by_url)

    with app.test_client() as client:
        response = client.get('/urls/42')
        assert response.status_code == 200
        
        html = response.data.decode('utf-8')
        assert 'Сайт: https://github.com' in html
        assert '42' in html
        mock_find_url_by_id.assert_called_once_with('42')


# Проверяем ошибку 404, когда id нет в базе
def test_urls_show_page_not_found(monkeypatch):

    mock_find_url_by_id = MagicMock(return_value=None)
    monkeypatch.setattr(repo, 'find_url_by_id', mock_find_url_by_id)

    mock_find_checks_by_url = MagicMock(return_value=[])
    monkeypatch.setattr(repo, 'find_checks_by_url_id', mock_find_checks_by_url)

    with app.test_client() as client:
        response = client.get('/urls/999')
        assert response.status_code == 404
        
        html = response.data.decode('utf-8')

        assert 'Сайт не найден' in html
        assert '404' in html


# Проверяем успех добавления сайта
def test_urls_post_success(monkeypatch):
    monkeypatch.setattr(repo, 'find_url_by_name', MagicMock(return_value=None))
    
    mock_save = MagicMock(return_value=100)
    monkeypatch.setattr(repo, 'save', mock_save)

    with app.test_client() as client:
        response = client.post('/urls', data={'url': 'https://yandex.ru'})
        
        assert response.status_code == 302
        assert response.headers['Location'] == '/urls/100'


# Проверяем валидацию на пустой сайт
def test_urls_post_validation_empty(monkeypatch):
    with app.test_client() as client:
        response = client.post('/urls', data={'url': ''})
        assert response.status_code == 200
        
        html = response.data.decode('utf-8')
        assert 'Страница не может быть пустой' in html


# Проверяем валидацию сайта
def test_urls_post_validation_invalid_url(monkeypatch):
    monkeypatch.setattr(repo, 'find_url_by_name', MagicMock(return_value=None))
    with app.test_client() as client:
        response = client.post('/urls', data={'url': 'not-a-valid-url'})
        assert response.status_code == 200
        
        html = response.data.decode('utf-8')
        assert 'Некорректный URL' in html


# Проверяем валидацию на уникальность сайта
def test_urls_post_validation_duplicate(monkeypatch):
    mock_find_url_by_name = MagicMock(return_value={'id': 1, 'name': 'https://hexlet.io'})
    monkeypatch.setattr(repo, 'find_url_by_name', mock_find_url_by_name)

    with app.test_client() as client:
        response = client.post('/urls', data={'url': 'https://hexlet.io'})
        assert response.status_code == 302
        
        assert response.headers['Location'] == '/urls/1'

        with client.session_transaction() as session:
            assert ('danger', 'Страница уже существует') in session['_flashes']


# Проверяем валидацию на длину адреса сайта
def test_urls_post_validation_too_long(monkeypatch):
    monkeypatch.setattr(repo, 'find_url_by_name', MagicMock(return_value=None))

    long_url = "https://" + "a" * 250 + ".com"
    
    with app.test_client() as client:
        response = client.post('/urls', data={'url': long_url})
        assert response.status_code == 200
        
        html = response.data.decode('utf-8')
        assert 'Длина страницы не может быть свыше 255 символов' in html