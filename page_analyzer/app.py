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

from url_engine import check_url_status
from url_repository import UrlRepository

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def get_db_connection():
    DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://localhost:5432/fake_db")
    
    return psycopg.connect(DATABASE_URL)


repo = UrlRepository(get_db_connection)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/urls', methods=['GET'])
def urls_get():

    urls = repo.get_content()

    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def urls_post():

    url_data = request.form.to_dict()
    errors = validate(url_data)

    if errors:
        return render_template(
            'index.html',
            url=url_data,
            errors=errors,
        )
    
    url_data['id'] = repo.save(url_data)

    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('urls_show', id=url_data['id']), code=302)


@app.route('/urls/<id>')
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
        errors['url'] = "Сайт не может быть пустым"
    else:

        if len(url_address) > 255:
            errors['length'] = \
                "Длина адреса сайта не может быть свыше 255 символов"

        if not validators.url(url_address):
            errors['url'] = "Указанный адрес сайта не прошел валидацию"

        if repo.find_url_by_name(url_address):
            errors['duple'] = "Указанный адрес сайта был добавлен ранее"

    return errors


@app.post('/urls/<id>/checks')
def url_checks_post(id):

    url = repo.find_url_by_id(id)
    status_code = check_url_status(url['name'])

    if not status_code:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        flash('Страница успешно проверена', 'success')
        repo.save_check(id, status_code)
    
    return redirect(url_for('urls_show', id=id), code=302)