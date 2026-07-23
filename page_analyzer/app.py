import os

import psycopg
import validators
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from url_engine import check_url_status, get_url_host
from url_repository import UrlRepository

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY', 'dev-key-placeholder-never-use-in-prod'
)


def get_db_connection():
    DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://localhost:5432/fake_db")
    
    return psycopg.connect(DATABASE_URL)


repo = UrlRepository(get_db_connection)


@app.get("/")
def index():
    return render_template("index.html")


@app.get('/urls')
def urls_get():

    urls = repo.get_content()

    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def urls_post():

    url_data = request.form.to_dict()
    url_data['url'] = get_url_host(url_data.get('url'))

    errors = validate(url_data)

    if errors:

        if errors.get('duple'):
            url = repo.find_url_by_name(url_data['url'])

            flash('Страница уже существует', 'danger')
            return redirect(url_for('urls_show', id=url['id']), code=302)

        return render_template(
            'index.html',
            url=url_data,
            errors=errors,
        ), 422
    
    url_data['id'] = repo.save(url_data)

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('urls_show', id=url_data['id']), code=302)


@app.get('/urls/<id>')
def urls_show(id):

    url = repo.find_url_by_id(id)
    url_checks = repo.find_checks_by_url_id(id)

    if not url:
        abort(404)

    return render_template(
        'show.html',
        url=url,
        url_checks=url_checks
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def validate(url_data):

    errors = {}
    url_address = url_data['url']
    print(f"Проверяем на валидность страницу {url_address}")

    if not url_address:
        errors['url'] = "Страница не может быть пустой"
    else:

        if len(url_address) > 255:
            errors['length'] = \
                "Длина страницы не может быть свыше 255 символов"

        if not validators.url(url_address):
            errors['url'] = "Некорректный URL"

        if repo.find_url_by_name(url_address):
            errors['duple'] = "Страница уже существует"

    return errors


@app.post('/urls/<id>/checks')
def url_checks_post(id):

    url = repo.find_url_by_id(id)
    url_status = check_url_status(url['name'])

    if not url_status.get('status_code'):
        flash('Произошла ошибка при проверке', 'danger')
    else:
        flash('Страница успешно проверена', 'success')
        repo.save_check(id, url_status)
    
    return redirect(url_for('urls_show', id=id), code=302)