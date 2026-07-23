import psycopg


class UrlRepository:
    def __init__(self, conn):
        self.get_conn = conn

    def get_content(self):
        with self.get_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        cast(created_at as date) as created_at
                    FROM
                        urls
                    ORDER BY
                        id desc
                """)
                return cur.fetchall()

    def find_by_name(self, url_address):
        with self.get_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        cast(created_at as date) as created_at
                    FROM
                        urls
                    WHERE
                        name = %s
                    ORDER BY
                        created_at desc
                """, (url_address,))
                return cur.fetchone()

    def find_by_id(self, url_id):
        with self.get_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute("""
                    SELECT
                        id,
                        name,
                        cast(created_at as date) as created_at
                    FROM
                        urls
                    WHERE
                        id = %s
                    ORDER BY
                        created_at desc
                """, (url_id,))
                return cur.fetchone()

    def save(self, url_data):
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                if 'id' not in url_data:
                    # New url
                    cur.execute(
                        "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                        (url_data['url'],)
                    )
                    url_data['id'] = cur.fetchone()[0]
                else:
                    # Existing url
                    cur.execute(
                        "UPDATE urls SET name = %s WHERE id = %s",
                        (url_data['url'], url_data['id'],)
                    )
            conn.commit()
            return url_data['id']

    def destroy(self, id):
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM urls WHERE id = %s", (id,))
            conn.commit()
