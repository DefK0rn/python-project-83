import page_analyzer
from page_analyzer import app


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