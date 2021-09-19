import datetime
from playhouse.mysql_ext import JSONField
from peewee import *
from models import Tweet, User


#  Field 类用于描述 Model 数据库列的属性。
#  每个字段类型都有一个对应的SQL存储类（即varchar、int），并且可以透明地处理python数据类型和底层存储之间的转换。


# 1.常见的字段类如下
# Field Type	Sqlite	Postgresql	MySQL
# AutoField	integer	serial	integer
# BigAutoField	integer	bigserial	bigint
# IntegerField	integer	integer	integer
# BigIntegerField	integer	bigint	bigint
# SmallIntegerField	integer	smallint	smallint
# IdentityField	not supported	int identity	not supported
# FloatField	real	real	real
# DoubleField	real	double precision	double precision
# DecimalField	decimal	numeric	numeric
# CharField	varchar	varchar	varchar
# FixedCharField	char	char	char
# TextField	text	text	text
# BlobField	blob	bytea	blob
# BitField	integer	bigint	bigint
# BigBitField	blob	bytea	blob
# UUIDField	text	uuid	varchar(40)
# BinaryUUIDField	blob	bytea	varbinary(16)
# DateTimeField	datetime	timestamp	datetime
# DateField	date	date	date
# TimeField	time	time	time
# TimestampField	integer	integer	integer
# IPField	integer	bigint	bigint
# BooleanField	integer	boolean	bool
# BareField	untyped	not supported	not supported
# ForeignKeyField	integer	integer	integer


# 2.字段初始化参数
# null = False --允许空值
# index = False --在此列上创建索引
# unique = False --在此列上创建唯一索引
# column_name = None --在数据库中显式指定列名。
# default = None --默认值
# primary_key = False --表的主键
# constraints = None - one or more constraints, e.g. [Check('price > 0')]
# sequence = None --序列名（如果后端支持）
# collation = None --用于排序字段/索引的排序规则
# unindexed = False --指示应取消对虚拟表上的字段的索引（sqlite only*）
# choices = None -- 可选择的包含二元数组的可迭代对象
# help_text = None --表示此字段的任何有用文本的字符串
# verbose_name = None --表示此字段的“用户友好”名称的字符串
# index_type = None --指定自定义索引类型，例如，对于Postgres，可以指定 'BRIN' 或 'GIN' 索引。
# 注意：default和choices都可以在数据库级别实现，分别为DEFAULT 和 CHECK CONSTRAINT
# 但是，任何应用程序更改都需要模式更改。因此，default仅仅应用在python里，choices没有经过验证，但是目的仅是存在于元数据


# 3.一些字段的特殊参数
# Field type	Special Parameters
# CharField	max_length
# FixedCharField	max_length
# DateTimeField	formats
# DateField	formats
# TimeField	formats
# TimestampField	resolution, utc
# DecimalField	max_digits, decimal_places, auto_round, rounding
# ForeignKeyField	model, field, backref, on_delete, on_update, deferrable lazy_load
# BareField	adapt


# 4.默认字段值
# 创建对象时，peewee可以为字段提供默认值。
class Message(Model):
    context = TextField()
    read_count = IntegerField(default=0)
# 在某些情况下，默认值可能是动态的。一个常见的场景是使用当前日期和时间。
# Peewee允许您在这些情况下指定一个函数，其返回值将在创建对象时使用。
class Message(Model):
    context = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
# 注意：如果使用的字段接受可变类型（list， dict, 等），并且希望提供默认值，
# 最好将默认值包装在一个简单函数中，这样多个模型实例就不会共享对同一基础对象的引用：
def house_defaults():
    return {'beds': 0, 'baths': 0}
class House(Model):
    number = TextField()
    street = TextField()
    attributes = JSONField(default=house_defaults)
# 数据库还可以提供字段的默认值。虽然peewee没有显式地提供用于设置服务器端默认值的API，
# 但是可以使用 constraints 用于指定服务器默认值的参数：
class Message(Model):
    context = TextField()
    timestamp = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
# 注意：使用 default 参数，这些值由peewee设置，而不是作为实际表和列定义的一部分。


# 5.ForeignKeyField
#允许一个模型引用另一个模型的特殊字段类型
# 通常，外键将包含与其相关的模型的主键（但可以通过field指定）
# 有一个外键来自 Tweet 到 User . 这意味着所有用户都存储在自己的表中，tweet也是如此，
# 而从tweet到user的外键允许每个tweet指到特定的用户对象。

# 5.1在peewee中，访问 ForeignKeyField 将返回整个相关对象
tweets = Tweet.select().order_by(Tweet.created_date.desc())
for tweet in tweets:
    # WARNING: an additional query will be issued for EACH tweet
    # to fetch the associated User data.
    print(tweet.user.username, tweet.message)

# 5.2 有时，您只需要外键列中关联的主键值。
# 在这种情况下，Peewee遵循Django建立的惯例，允许您通过追加 "_id" 到外键字段的名称：
tweets = Tweet.select()
for tweet in tweets:
    # Instead of "tweet.user", we will just get the raw ID value stored
    # in the column.
    print(tweet.user_id, tweet.message)

# 5.3为了防止意外解析外键并触发其他查询， ForeignKeyField 支持初始化参数 lazy_load 当被禁用时，其行为类似于 "_id" 属性。例如：
class Tweet(Model):
    # ... same fields, except we declare the user FK to have
    # lazy-load disabled:
    user = ForeignKeyField(User, backref='tweets', lazy_load=False)
for tweet in Tweet.select():
    print(tweet.user, tweet.message)
# 通过禁用lazy_load, 访问 tweet.user will 不会有额外的查询，而是直接返回user ID

# 5.4 Back-references
# ForeignKeyField 允许将反向引用属性绑定到目标模型。
# 默认的，此属性将被命名为 classname_set，classname 是class的小写字母
# 但可以使用参数 backref 重写
class Message(Model):
    from_user = ForeignKeyField(User, backref='outbox')
    to_user = ForeignKeyField(User, backref='inbox')
    text = TextField()
for message in some_user.outbox:
    # We are iterating over all Messages whose from_user is some_user.
    print(message)
for message in some_user.inbox:
    # We are iterating over all Messages whose to_user is some_user
    print(message


# 6. DateTimeField, DateField and TimeField
# 用于处理日期和时间的三个字段具有特殊属性，允许访问年、月、小时等内容。
# DateField具有的属性：
#     year
#     month
#     day
# TimeField具有的属性：
#     hour
#     minute
#     second
# DateTimeField 上面都有
# 这些属性可以像任何其他表达式一样使用。
now = datetime.datetime.now()
Event.select(Event.event_date.day.alias('day')).where(
    (Event.event_date.year == now.year) &
    (Event.event_date.month == now.month))


# 6. 自定义字段
# 在Peewee中，很容易添加对自定义字段类型的支持；
# 要添加自定义字段类型，首先需要确定字段数据将存储在哪种类型的列中。比如如果你想把decimal字段加到python行为上，只要写一个继承 DecimalField的子类
# 另外，如果要让知道peewee知道你添加的字段，则由Field.field_type属性控制
# 在这个例子中，我们将为PostgreSQL创建一个UUID字段
class UUIDField(Field):
    field_type = 'uuid'
# 因为psycopg2会把字段默认看做 string类型, 需要添加两个方法去处理:
import uuid

class UUIDField(Field):

    field_type = 'uuid'

    def db_value(self, value):
        return value.hex  # convert UUID to hex string.

    def python_value(self, value):
        return uuid.UUID(value) # convert hex string to UUID
# 此步骤是可选的，默认field_type会在数据库模式里被用作列的数据类型。
# 如果你想把这个字段用在不同数据库做不同类型，就需要让数据库知道映射关系
# 在Postgres中，我们把自定义的UUIDField转为UUID类型
db = PostgresqlDatabase('my_db', field_types={'uuid': 'uuid'})
# 在Sqlite没有 UUID字段, 我们转为text类型.
db = SqliteDatabase('my_db', field_types={'uuid': 'text'})
