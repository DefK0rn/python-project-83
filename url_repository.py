import psycopg


class UrlRepository:
    def __init__(self, conn):
        self.get_conn = conn

    def get_content(self):
        with self.get_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute("""
                    with urlchecks as (
                        select
                            url_id,
                            status_code,
                            cast(created_at as date) as check_created_at,
                            row_number() over(
                                partition by url_id order by created_at desc
                            ) as rn
                        from
                            url_checks
                    )
                    SELECT
                        u.id,
                        u.name,
                        cast(u.created_at as date) as created_at,
                        uc.check_created_at,
                        uc.status_code
                    FROM
                        urls u
                    left join urlchecks uc on
                        uc.url_id = u.id
                        and uc.rn = 1
                    ORDER BY
                        u.id desc
                """)
                return cur.fetchall()

    def find_url_by_name(self, url_address):
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

    def find_url_by_id(self, url_id):
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

    def find_checks_by_url_id(self, url_id):
        with self.get_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute("""
                    SELECT
                        id,
                        status_code,
                        h1,
                        title,
                        description,
                        cast(created_at as date) as created_at
                    FROM
                        url_checks
                    WHERE
                        url_id = %s
                    ORDER BY
                        id desc
                """, (url_id,))
                return cur.fetchall()

    def save_check(self, url_id, status_code):
        with self.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO url_checks (url_id, status_code)
                    VALUES (%s, %s) RETURNING id
                """, (url_id, status_code,))
                url_check_id = cur.fetchone()[0]
                conn.commit()
                return url_check_id