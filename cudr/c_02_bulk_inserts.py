# 插入多条数据

from peewee import *
from cudr.c_01_insert import Tweet
from models import MyModel

db = MySQLDatabase(host='127.0.0.1', port=3306, user='root', passwd='root', database="peewee_doc")
db.connect()


# 1.Model.create() in a loop
data_source = [
    {'field1': 'val1-1', 'field2': 'val1-2'},
    {'field1': 'val2-1', 'field2': 'val2-2'},
]
# for data_dict in data_source:
#     MyModel.create(**data_dict)
# 这个方法会很慢，因为：
# 1.如果不在事务中包装循环，则每次调用 create() 发生在它自己的事务中。那真是太慢了
# 2.上述代码有相当多的python逻辑，并且 InsertQuery 必须生成并解析为SQL
# 3.我们正在检索 上次插入ID, 这会导致在某些情况下执行额外的查询。


# 2.将其包装在事务中 atomic()，
# with db.atomic():
#     for data_dict in data_source:
#         MyModel.create(**data_dict)
# 比循环亏啊，但是仍然受2,3影响


# 3.使用insert_many()
# Fastest way to INSERT multiple rows.
MyModel.insert_many(data_source).execute()

#这个 insert_many() 方法还接受行元组列表，前提是还指定了相应的字段
data = [('val1-1', 'val1-2'),
        ('val2-1', 'val2-2'),
        ('val3-1', 'val3-2')]

# But we need to indicate which fields the values correspond to.
MyModel.insert_many(data, fields=[MyModel.field1, MyModel.field2]).execute()

# 在事务中使用insert_many
with db.atomic():
    MyModel.insert_many(data, fields=[MyModel.field1, MyModel.field2]).execute()


# chunked大批量插入
# Insert rows 100 at a time.
from peewee import chunked
with db.atomic():
    for batch in chunked(data_source, 100):
        MyModel.insert_many(batch).execute()


# Model.bulk_create()大批量插入
class User(Model):
    id = AutoField()
    username = CharField()

    class Meta:
        database = db
with open('user_list.txt') as fh:
    # Create a list of unsaved User instances.
    users = [User(username=line.strip()) for line in fh.readlines()]

# Wrap the operation in a transaction and batch INSERT the users
# 100 at a time.
with db.atomic():
    User.bulk_create(users, batch_size=100)


# Model.bulk_update()批量更新
u1, u2, u3 = [User.create(username='u%s' % i) for i in (1, 2, 3)]
# Now we'll modify the user instances.
u1.username = 'u1-x'
u2.username = 'u2-y'
u3.username = 'u3-z'
# Update all three users with a single UPDATE query.
User.bulk_update([u1, u2, u3], fields=[User.username])

# For large lists of objects, call to bulk_update() with Database.atomic()
with db.atomic():
    User.bulk_update(users, fields=['username'], batch_size=50)


# 从另一个表的查询记录插入新数据
# 使用insert_many
class TweetArchive():
    id = AutoField()
    message = CharField()
    user = ForeignKeyField(User, backref='user')

    class Meta:
        database = db

res = (TweetArchive
       .insert_from(
           Tweet.select(Tweet.user, Tweet.message),
           fields=[TweetArchive.user, TweetArchive.message])
       .execute())

# 相当于
# INSERT INTO "tweet_archive" ("user_id", "message")
# SELECT "user_id", "message" FROM "tweet"