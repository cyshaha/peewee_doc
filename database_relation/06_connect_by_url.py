# 使用url连接数据库
import os

from peewee import *
from playhouse.db_url import connect

db = connect(os.environ.get("DATABASE") or 'sqlite:///default.db')


class BaseModel(Model):
    class Meta:
        database = db


# 数据库URL示例：
# sqlite:///my_database.db 将创建一个 SqliteDatabase 文件的实例 my_database.db 在当前目录中。
# sqlite:///:memory: 将在内存中创建 SqliteDatabase 实例。
# postgresql://postgres:my_password@localhost:5432/my_database 将创建一个 PostgresqlDatabase 实例。提供用户名和密码，以及要连接的主机和端口。
# mysql://user:passwd@ip:port/my_db 将创建一个 MySQLDatabase 本地mysql数据库实例 my_db.