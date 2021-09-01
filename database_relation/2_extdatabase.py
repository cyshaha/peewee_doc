# Peewee通过特定于数据库的扩展模块为SQLite、Postgres和CockroachDB提供高级支持

from playhouse.sqlite_ext import SqliteExtDatabase
db = SqliteExtDatabase('/path/to/app.db', regexp_function=True, timeout=3,
                       pragmas={'journal_mode': 'wal'})

from playhouse.postgres_ext import PostgresqlExtDatabase
db = PostgresqlExtDatabase('my_app', user='pastgres', register_hstore=True)
