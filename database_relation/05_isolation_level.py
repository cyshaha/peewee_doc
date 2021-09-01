# 设置隔离级别
from peewee import *
from psycopg2.extensions import ISOLATION_LEVEL_SERIALIZABLE

db = PostgresqlDatabase('my_app', user='postgres', host='db-host',
                        isolation_level=ISOLATION_LEVEL_SERIALIZABLE)

