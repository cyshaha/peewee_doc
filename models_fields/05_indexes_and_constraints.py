# 索引和约束
# Peewee可以在单个或多个列上创建索引，也可以选择包括 UNIQUE 约束。Peewee还支持对模型和字段的用户定义约束。

from peewee import *

# 1.单列索引和约束
# 用字段初始化参数定义单列索引。
class User(Model):
    username = CharField(unique=True)
    email = CharField(index=True)
# 添加用户自定义约束，可以使用constraints参数
class Product(Model):
    name = CharField(unique=True)
    price = DecimalField(constraints=[Check('price < 10000')])
    created = DateTimeField(
        constraints=[SQL("DEFAULT (datetime('now'))")])


# 2.多列索引
# 多列索引使用嵌套元组定义为 Meta的属性
# 每个数据库索引都是一个2元组，第一部分是字段名称的元组，第二部分是指示索引是否应唯一的布尔值。
class Transaction(Model):
    from_acct = CharField()
    to_acct = CharField()
    amount = DecimalField()
    date = DateTimeField()

    class Meta:
        indexes = (
            # create a unique on from/to/date
            (('from_acct', 'to_acct', 'date'), True),
            # create a non-unique on from/to
            (('from_acct', 'to_acct'), False),
        )
# 注意：有一个索引，后面也要加逗号


# 3.高级索引创建
# Peewee支持更结构化的API，使用Model.add_index()或直接使用eModelIndex辅助类
class Article(Model):
    name = TextField()
    timestamp = TimestampField()
    status = IntegerField()
    flags = IntegerField()
# Add an index on "name" and "timestamp" columns.
Article.add_index(Article.name, Article.timestamp)
# Add a partial index on name and timestamp where status = 1.
Article.add_index(Article.name, Article.timestamp,
                  where=(Article.status == 1))
# Create a unique index on timestamp desc, status & 4.
idx = Article.index(
    Article.timestamp.desc(),
    Article.flags.bin_and(4),
    unique=True)
Article.add_index(idx)
# SQLite does not support parameterized CREATE INDEX queries, so
# we declare it manually.
Article.add_index(SQL('CREATE INDEX ...'))


# 表约束
# peewee允许给model添加任意的表约束，当模式创建的时候将成为表的定义的一部分
# 现在有个Person类，有个复合主键，'first'和 'last'，如果想另一个表关联Person这个表，因此需要一个外键约束
class Person(Model):
    first = CharField()
    last = CharField()

    class Meta:
        primary_key = CompositeKey('first', 'last')

class Pet(Model):
    owner_first = CharField()
    owner_last = CharField()
    pet_name = CharField()

    class Meta:
        constraints = [SQL('FOREIGN KEY(owner_first, owner_last) '
                           'REFERENCES person(first, last)')]

# 也可以在表级里定义CHECK约束
class Product(Model):
    name = CharField(unique=True)
    price = DecimalField()

    class Meta:
        constraints = [Check('price < 10000')]