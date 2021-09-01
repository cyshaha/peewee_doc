from peewee import *

from playhouse.migrate import *


db = MySQLDatabase(host='127.0.0.1', port=3306, user='root', passwd='root', database="peewee_doc")
db.connect()

class User(Model):
    id = AutoField()
    username = CharField()

    class Meta:
        database = db


class Tweet(Model):
    id = AutoField()
    message = CharField()
    user = ForeignKeyField(User, backref='user')
    is_published = BooleanField(default='')
    creation_date = DateTimeField(null=True)

    class Meta:
        database = db

# db.create_tables([User, Tweet])

# is_published = BooleanField(default='')
# creation_date = DateTimeField(null=True)
# #
# migrator = PostgresqlMigrator(db)
# migrate(
#     # migrator.add_column('tweet', 'is_published', is_published),
#     migrator.add_column('tweet', 'creation_date', creation_date),
# )

# 1.use Model.create()
# User.create(username='Charlie')


# 2.call save()
# user = User(username='Charlie')
# user.save()
#
# huey = User()
# huey.username = "huey"
# huey.save()
# print(huey.id)


# 创建外键
# 1.直接使用对象
# huey = User.select().where(User.id==3).first()
# tweet = Tweet.create(user=huey, message='Hello!')
# 2.使用id
# tweet = Tweet.create(user=2, message='Hello again!')


# 3.Model.insert()
# 执行完成会返回记录的主键
# User.insert(username='Mickey').execute()
