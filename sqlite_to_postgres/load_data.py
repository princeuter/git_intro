import os
import sqlite3
import logging
from contextlib import closing, contextmanager
from dataclasses import dataclass, astuple, fields
from typing import Generator
from uuid import UUID
from datetime import datetime, date

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

BATCH_SIZE = 100

dsl = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'options': '-c search_path=content,public',
}


# ──────────────────────────── Датаклассы ────────────────────────────

@dataclass
class Genre:
    id: UUID
    name: str
    description: str
    created: datetime
    modified: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)


@dataclass
class Person:
    id: UUID
    full_name: str
    created: datetime
    modified: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)


@dataclass
class FilmWork:
    id: UUID
    title: str
    description: str
    creation_date: date
    rating: float
    type: str
    created: datetime
    modified: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)


@dataclass
class GenreFilmWork:
    id: UUID
    film_work_id: UUID
    genre_id: UUID
    created: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.film_work_id, str):
            self.film_work_id = UUID(self.film_work_id)
        if isinstance(self.genre_id, str):
            self.genre_id = UUID(self.genre_id)


@dataclass
class PersonFilmWork:
    id: UUID
    film_work_id: UUID
    person_id: UUID
    role: str
    created: datetime

    def __post_init__(self):
        if isinstance(self.id, str):
            self.id = UUID(self.id)
        if isinstance(self.film_work_id, str):
            self.film_work_id = UUID(self.film_work_id)
        if isinstance(self.person_id, str):
            self.person_id = UUID(self.person_id)


# ──────────────────────────── Контекстный менеджер SQLite ────────────────────────────

@contextmanager
def conn_context(db_path: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ──────────────────────────── Извлечение из SQLite ────────────────────────────

def extract_data(sqlite_cursor: sqlite3.Cursor, query: str) -> Generator:
    try:
        sqlite_cursor.execute(query)
        while results := sqlite_cursor.fetchmany(BATCH_SIZE):
            yield results
    except sqlite3.Error as e:
        logger.error(f'Ошибка при чтении из SQLite: {e}')
        raise


# ──────────────────────────── Загрузка в PostgreSQL ────────────────────────────

def load_table(sqlite_cursor, pg_cursor, query: str, dataclass_type, pg_query: str):
    count = 0
    for batch in extract_data(sqlite_cursor, query):
        try:
            objects = [dataclass_type(**dict(row)) for row in batch]
            col_names = ', '.join(f.name for f in fields(dataclass_type))
            placeholders = ', '.join(['%s'] * len(fields(dataclass_type)))
            batch_tuples = [astuple(obj) for obj in objects]
            pg_cursor.executemany(
                f'INSERT INTO content.{pg_query} ({col_names}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING',
                batch_tuples
            )
            count += len(objects)
        except Exception as e:
            logger.error(f'Ошибка при записи в PostgreSQL ({pg_query}): {e}')
            raise
    logger.info(f'Таблица {pg_query}: перенесено {count} записей')


def load_all_data(sqlite_cursor, pg_cursor):
    load_table(
        sqlite_cursor, pg_cursor,
        'SELECT id, name, description, created_at as created, updated_at as modified FROM genre',
        Genre, 'genre'
    )
    load_table(
        sqlite_cursor, pg_cursor,
        'SELECT id, full_name, created_at as created, updated_at as modified FROM person',
        Person, 'person'
    )
    load_table(
        sqlite_cursor, pg_cursor,
        'SELECT id, title, description, creation_date, rating, type, created_at as created, updated_at as modified FROM film_work',
        FilmWork, 'film_work'
    )
    load_table(
        sqlite_cursor, pg_cursor,
        'SELECT id, film_work_id, genre_id, created_at as created FROM genre_film_work',
        GenreFilmWork, 'genre_film_work'
    )
    load_table(
        sqlite_cursor, pg_cursor,
        'SELECT id, film_work_id, person_id, role, created_at as created FROM person_film_work',
        PersonFilmWork, 'person_film_work'
    )


# ──────────────────────────── Тест целостности ────────────────────────────

def test_transfer(sqlite_cursor, pg_cursor):
    tables = [
        ('genre', 'content.genre'),
        ('person', 'content.person'),
        ('film_work', 'content.film_work'),
        ('genre_film_work', 'content.genre_film_work'),
        ('person_film_work', 'content.person_film_work'),
    ]
    for sqlite_table, pg_table in tables:
        sqlite_cursor.execute(f'SELECT COUNT(*) FROM {sqlite_table}')
        sqlite_count = sqlite_cursor.fetchone()[0]

        pg_cursor.execute(f'SELECT COUNT(*) FROM {pg_table}')
        pg_count = list(pg_cursor.fetchone().values())[0]

        assert sqlite_count == pg_count, (
            f'Несоответствие в таблице {sqlite_table}: '
            f'SQLite={sqlite_count}, PostgreSQL={pg_count}'
        )
        logger.info(f'Таблица {sqlite_table}: проверка пройдена ({sqlite_count} записей)')


# ──────────────────────────── Точка входа ────────────────────────────

if __name__ == '__main__':
    with conn_context('db.sqlite') as sqlite_conn:
        with closing(psycopg.connect(**dsl)) as pg_conn:
            with closing(sqlite_conn.cursor()) as sqlite_cur:
                with closing(pg_conn.cursor(row_factory=dict_row)) as pg_cur:
                    load_all_data(sqlite_cur, pg_cur)
                    pg_conn.commit()
                    test_transfer(sqlite_cur, pg_cur)

    print('Данные успешно перенесены!')