# 1 初始化数据库

# 这个 Database 初始化方法要求将数据库的名称作为第一个参数。在建立连接时，
# 后续的关键字参数将传递给基础数据库驱动程序，使您能够轻松传递特定于供应商的参数。

from peewee import *

db = PostgresqlDatabase(
    "database_name",  # 这个是peewee需要的参数
    user='postgres',  # 下面三个是直接传递给psycopg2
    password='seret',
    host='db.mysite.com'
)

# mysql连接
db = MySQLDatabase('database_name', user='www-data', charset='utf8mb4')