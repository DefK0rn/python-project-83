import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


def init_db():
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise ValueError("Переменная окружения DATABASE_URL не задана!")

    # Если render вернул postgres вместо postgresql
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Нужно проверить, что файл со схемой БД в наличии
    sql_file_path = "database.sql"
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"Файл схемы '{sql_file_path}' не найден!")

    print("Чтение схемы и инициализация базы данных...")
    
    try:
        with open(sql_file_path, "r", encoding="utf-8") as file:
            sql_script = file.read()

        conn = psycopg.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute(sql_script)
        conn.commit()
        
        print("База данных успешно обновлена согласно схеме")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        raise RuntimeError(f"Не смогли инициализировать базу данных: {e}")


if __name__ == "__main__":

    init_db()