from peewee import *


# Model类， Field 实例和模型实例都映射到数据库概念
# Model class	    Database table
# Field instance	Column on a table
# Model instance	Row in a database table

# 下面是经典的使用方法
import datetime
from peewee import *

db = SqliteDatabase('my_app.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)

class Tweet(BaseModel):
    user = ForeignKeyField(User, backref='tweets')
    message = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)

# 步骤有
# 1.创建一个数据库实例
db = SqliteDatabase('my_app.db')
# db对象用来管理数据库的连接

# 2.创建一个指定数据库的基础模型类
class BaseModel(Model):
    class Meta:
        database = db
# 定义一个建立数据库连接的基础模型类，后面继承他的子类都不用再定义数据库了
# 模型的配置在Meta类里

# 3.定义一个模型类
class User(BaseModel):
    username = CharField(unique=True)
# 继承了BaseModel，所以 User 模型将继承数据库连接
# 我们已经明确定义了一个 username 具有唯一约束的列。因为我们没有指定主键，Peewee将自动添加一个名为 id.