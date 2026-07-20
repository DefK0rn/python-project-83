import os

import psycopg
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL', "postgresql://localhost:5432/fake_db")
conn = psycopg.connect(DATABASE_URL)


@app.route("/")
def index():
    return render_template("index.html")