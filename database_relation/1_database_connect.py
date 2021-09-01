from peewee import *

# 1连接sqlite
sqlite_db = SqliteDatabase('/path/to/app.db',pragmas={'journal_mode': 'wal','cache_size': -1024 * 64})

# 2连接mysql
mysql_db = MySQLDatabase('my_app', user='app', password='db_pasword', host='10.1.0.8', port=3306)

# 3连接postgres数据库
pg_db = PostgresqlDatabase('my_app', user='postgres', password='secret', host='10.1.0.9', port=5432)
