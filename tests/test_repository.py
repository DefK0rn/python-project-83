import datetime
import os

import psycopg
import pytest

from url_repository import UrlRepository

RUN_LOCAL_DB_TESTS = os.getenv("RUN_LOCAL_DB_TESTS", "false")


def get_db_connection():

    DATABASE_URL_TEST = os.getenv('DATABASE_URL_TEST', "postgresql://localhost:5432/fake_db")
    
    return psycopg.connect(DATABASE_URL_TEST)


@pytest.fixture()
def db_conn():

    # Заглушка для gitHub
    if not RUN_LOCAL_DB_TESTS:
        pytest.skip("Тесты базы данных пропускаются в этой среде ")
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()

    yield get_db_connection

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS urls;")
        conn.commit()


@pytest.fixture()
def repo(db_conn):
    return UrlRepository(db_conn)


# Тест на добавление сайта
def test_save_new_url(repo):
    url_data = {'url': 'https://ru.hexlet.io'}
    
    url_id = repo.save(url_data)
    
    assert url_id is not None
    assert url_data['id'] == url_id

    saved_url = repo.find_by_id(url_id)
    assert saved_url['name'] == 'https://ru.hexlet.io'
    assert isinstance(saved_url['created_at'], datetime.date)


# Тест на изменение адреса сайта
def test_save_existing_url(repo):
    url_data = {'url': 'https://google.com'}
    url_id = repo.save(url_data)

    url_data['url'] = 'https://google.ru'
    updated_id = repo.save(url_data)

    assert url_id == updated_id
    
    updated_url = repo.find_by_id(url_id)
    assert updated_url['name'] == 'https://google.ru'


# Тест на поиск по адресу сайта
def test_find_by_name(repo):
    repo.save({'url': 'https://github.com'})

    result = repo.find_by_name('https://github.com')
    assert result is not None
    assert result['name'] == 'https://github.com'

    assert repo.find_by_name('https://non-existent.com') is None


# Тест на получение списка сохраненных сайтов
def test_get_content_ordering(repo):
    repo.save({'url': 'https://site1.com'})
    repo.save({'url': 'https://site2.com'})

    content = repo.get_content()
    
    assert len(content) == 2
    assert content[0]['name'] == 'https://site2.com'
    assert content[1]['name'] == 'https://site1.com'


# Тест на удаление сайта
def test_destroy(repo):
    url_id = repo.save({'url': 'https://yandex.ru'})
    
    assert repo.find_by_id(url_id) is not None

    repo.destroy(url_id)

    assert repo.find_by_id(url_id) is None