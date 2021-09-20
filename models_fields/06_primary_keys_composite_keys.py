# 主键和复合主键及其他技巧
import uuid
from models import User,db_mysql
from peewee import *
import datetime
from relationsAndJoins.model_and_data import BaseModel


# 1. AutoField 用于标识自动递增的整数主键。如果不指定主键，peewee将自动创建一个名为“id”的自动递增主键。
# 要使用其他字段名指定自动递增的ID，可以写入：
class Event(Model):
    event_id = AutoField()  # Event.event_id will be auto-incrementing PK.
    name = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    metadata = BlobField()
# 如果定义一个其他字段作为主键，将不会自动创建主键'id'

# 复合主键可以使用 CompositeKey . 请注意，这样做可能会导致 ForeignKeyField 因为Peewee不支持“复合外键”的概念。
# 因此，我发现只有在少数情况下使用复合主键才是明智的，例如琐碎的多对多连接表：
class Image(Model):
    filename = TextField()
    mimetype = CharField()

class Tag(Model):
    label = CharField()

class ImageTag(Model):  # Many-to-many relationship.
    image = ForeignKeyField(Image)
    tag = ForeignKeyField(Tag)

    class Meta:
        primary_key = CompositeKey('image', 'tag')
# 极少数情况下不想要主键，可以设置meta属性为primary_key = False


# 2.非整数主键
# 如果要使用非整数主键（我通常不建议使用），可以指定 primary_key=True 创建字段时。
# 注意当使用非自动增量主键为模型创建一个新实例时，需要确保 save() 并指定 force_insert=True
class UUIDModel(Model):
    id = UUIDField(primary_key=True)

# 自增长ID，向数据库中插入新行时，会自动生成自动递增的ID
# 当调用save()时，peewee会根据主键的值决定执行insert还是update
# 但是如上面UUIDModel的例子，没有自增长id，我们需要手动的明确指出，第一次调用save()，需要force_insert = True
# This works because .create() will specify `force_insert=True`.
obj1 = UUIDModel.create(id=uuid.uuid4())
# This will not work, however. Peewee will attempt to do an update:
obj2 = UUIDModel(id=uuid.uuid4())
obj2.save() # WRONG
obj2.save(force_insert=True) # CORRECT
# Once the object has been created, you can call save() normally.
obj2.save()


# 3.复合主键
# 使用组合键，必须设置 primary_key 模型选项的属性 CompositeKey 实例
class Blog(Model):
    pass
class BlogToTag(Model):
    """A simple "through" table for many-to-many relationship."""
    blog = ForeignKeyField(Blog)
    tag = ForeignKeyField(Tag)

    class Meta:
        primary_key = CompositeKey('blog', 'tag')


# 4.手动指定主键
# 有时，您不希望数据库自动为主键生成值，例如在批量加载关系数据时。
# 在一次性的基础上处理这个请求，你可以简单地告诉Peewee关掉 auto_increment 导入过程中：
def load_user_csv():
    pass
data = load_user_csv()
User._meta.auto_increment = False # turn off auto incrementing IDs
fields = [User.id, User.username]
with db_mysql.atomic():
    User.insert_many(data, fields=fields).execute()
User._meta.auto_increment = True



# 5.无主键模型
# 如果要创建没有主键的模型，可以指定 primary_key = False
class MyData(BaseModel):
    timestamp = DateTimeField()
    value = IntegerField()

    class Meta:
        primary_key = False
#例如，对于没有主键的模型，某些模型API可能无法正常工作。 save() 和 delete_instance()
# 可以使用insert(), update() and delete())代替
