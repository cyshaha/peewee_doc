# 创建表

# 为了创建表，必须先打开到数据库的连接并创建表。
# Peewee将运行必要的 CREATE TABLE 查询，另外创建任何约束和索引

# Connect to our database.
from models import db_mysql, User, Tweet

db_mysql.connect()
# Create the tables.
db_mysql.create_tables([User, Tweet])
#  默认情况下，peewee创建表时使用包括 IF NOT EXISTS。如果要禁用此功能，请指定 safe=False .
# 如果要更改模型，可参考 schema migrations 的细节
