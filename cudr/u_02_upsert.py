# 更新插入
from datetime import datetime
from peewee import *


db_mysql = MySQLDatabase(host='127.0.0.1', port=3306, user='root', passwd='root', database="peewee_doc")
db_mysql.connect()

# db_psql = PostgresqlDatabase(user='postgres', password='123456', host='127.0.0.1', port=5432, database="peewee_doc")
# db_psql.connect()


class User2(Model):
    username = CharField(unique=True)
    last_login = DateTimeField(null=True)
    login_count = IntegerField(null=True)

    class Meta:
        database = db_mysql


class KV(Model):
    key = CharField(unique=True)
    value = IntegerField()

    class Meta:
        database = db_mysql


# db_mysql.create_tables([User2, KV])


# 1，replace和on_conflict_replace
# 插入或更新user,主键冲突就更新，否则插入
# user_id = User2.replace(username="the-user", last_login=datetime.now()).execute()
#下面这个也是等价的
# user_id = User2.insert(id=4, username='the-user', last_login=datetime.now())\
#     .on_conflict_replace().execute()


# 2.on_conflict_ignore()
# 有主键冲突就忽略，不进行插入操作
# user_id = User2.insert(id=4, username='the-user4', last_login=datetime.now())\
#     .on_conflict_ignore().execute()


# 3.on_conflict()
# 提供插入时如何解决冲突：
#   conflict_target：构成约束的列(Postgresql and SQLite 支持)
#   preserve，冲突时，更新值为insert语句里的值，如insert里last_login=now，则冲突last_login就更新为now
#   update：冲突时，字段的更精细的控制
# User2.create(username='huey', login_count=0)
# now = datetime.now()
# rowid = (User2
#          .insert(id=6, username='huey', last_login=now, login_count=1)
#          .on_conflict(
#              preserve=[User2.last_login],  # Use the value we would have inserted.
#              update={User2.login_count: User2.login_count + 1})
#          .execute())
