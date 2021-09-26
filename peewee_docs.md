# 第一章 安装

使用pip安装

```python
pip install peewee
```

github安装

```python
git clone https://github.com/coleifer/peewee.git
cd peewee
python setup.py install
```

在某些系统上，您可能需要使用 `sudo python setup.py install` 在整个系统范围内安装Peewee。



# 第二章 快速开始

本章简要介绍Peewee的主要功能，涵盖：

- [模型定义](https://www.osgeo.cn/peewee/peewee/quickstart.html#model-definition)
- [存储数据](https://www.osgeo.cn/peewee/peewee/quickstart.html#storing-data)
- [检索数据](https://www.osgeo.cn/peewee/peewee/quickstart.html#retrieving-data)

## 模型定义

模型类、字段和模型实例都映射到数据库概念：

| 对象     | 对应于…        |
| :------- | :------------- |
| 模型类   | 数据库表       |
| 字段实例 | 表上的列       |
| 模型实例 | 数据库表中的行 |

```python
from peewee import *

db = SqliteDatabase('people.db')

class Person(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db #指定的这个模型使用people.db数据库
```

注意：

1.Peewee将自动从类的名称推断数据库表名。您可以通过指定“meta”类中的 `table_name` 内部属性（与 `database` 属性）。

2.我们为模型命名 `Person` 而不是 `People` . 这是您应该遵循的一个惯例——即使表将包含多个人，我们总是使用单数形式命名类。

还有很多字段类型去存储不同类型的数据，还可以设置不同外键关联的关系，下面是一个小例子，详细见后面章节：

```python
class Pet(Model):
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db # this model uses the "people.db" database
```

既然我们有了模型，我们就连接到数据库。尽管不需要显示打开，但是最后还是这样，因为会立即显示数据库连接中的任何错误，而不是在执行第一个查询之后的才报错。完成任务后最好还要关闭连接。

```python
db.connect()
```

模型定义好后，就创建存储数据的表。这将创建具有适当列、索引、序列和外键约束的表：

```python
db.create_tables([Person, Pet])
```



## 存储数据

比如，使用 [`save()`](https://www.osgeo.cn/peewee/peewee/api.html#Model.save) 和 [`create()`](https://www.osgeo.cn/peewee/peewee/api.html#Model.create) 方法添加和更新人员记录。

```python
from datetime import date
uncle_bob = Person(name='Bob', birthday=date(1960, 1, 15))
uncle_bob.save() # bob is now stored in the database
# Returns: 1
```

当调用 `save()` ，返回修改的行数。

也可以通过调用 `create() `方法，返回模型实例：

```python
grandma = Person.create(name='Grandma', birthday=date(1935, 3, 1))
herb = Person.create(name='Herb', birthday=date(1950, 5, 5))
```

要更新行，请修改模型实例并调用 save()

```python
grandma.name = 'Grandma L.'
grandma.save()  # Update grandma's name in the database.
# Returns: 1
```

现在我们在数据库中存储了3个人。让我们给他们一些宠物

```python
bob_kitty = Pet.create(owner=uncle_bob, name='Kitty', animal_type='cat')
herb_fido = Pet.create(owner=herb, name='Fido', animal_type='dog')
herb_mittens = Pet.create(owner=herb, name='Mittens', animal_type='cat')
herb_mittens_jr = Pet.create(owner=herb, name='Mittens Jr', animal_type='cat')
```

在漫长的一生之后，Mittens 会生病死亡。我们需要将他从数据库中删除：

```python
herb_mittens.delete_instance() # he had a great life
# Returns: 1
```

 `delete_instance()`的返回值是从数据库中删除的行数。



## 检索数据

### 获取单个记录

使用`Select.get()`:

```python
grandma = Person.select().where(Person.name == 'Grandma L.').get()
```

也可以使用 `Model.get()`:

```python
grandma = Person.get(Person.name == 'Grandma L.')
```

### 获取记录列表

让我们列出数据库中的所有人员：

```python
for person in Person.select():
    print(person.name)

# prints:
# Bob
# Grandma L.
# Herb
```

让我们列出所有的猫和它们的主人的名字：

```python
query = Pet.select().where(Pet.animal_type == 'cat')
for pet in query:
    print(pet.name, pet.owner.name)

# prints:
# Kitty Bob
# Mittens Jr Herb
```

 这个查询有一个大问题：因为我们正在访问 `pet.owner.name`， 我们在原始查询中没有选择这个关系，Peewee需要执行一个额外的查询来检索宠物的主人。这种行为被称为 [N+1](https://www.osgeo.cn/peewee/peewee/relationships.html#nplusone) 一般应该避免。

我们可以通过同时选择这两个选项来避免额外的查询 *Pet* 和 人, 添加一个 join

```python
query = (Pet
         .select(Pet, Person)
         .join(Person)
         .where(Pet.animal_type == 'cat'))

for pet in query:
    print(pet.name, pet.owner.name)

# prints:
# Kitty Bob
# Mittens Jr Herb
```



### 排序

`order_by()` ：

```python
for pet in Pet.select().where(Pet.owner == uncle_bob).order_by(Pet.name):
    print(pet.name)

# prints:
# Fido
# Kitty
```



### 筛选

Peewee支持任意嵌套表达式

```python
d1940 = date(1940, 1, 1)
d1960 = date(1960, 1, 1)
query = (Person
         .select()
         .where((Person.birthday < d1940) | (Person.birthday > d1960)))

for person in query:
    print(person.name, person.birthday)

# prints:
# Bob 1960-01-15
# Grandma L. 1935-03-01
```



### 聚合和预取

现在让我们列出所有人 *and* 他们有多少宠物：

```python
for person in Person.select():
    print(person.name, person.pets.count(), 'pets')

# prints:
# Bob 2 pets
# Grandma L. 0 pets
# Herb 1 pets
```

这又是一个n+1的例子，我们可以通过执行 *JOIN* 并使用SQL函数聚合结果避免

```python
query = (Person
         .select(Person, fn.COUNT(Pet.id).alias('pet_count'))
         .join(Pet, JOIN.LEFT_OUTER)  # include people without pets.
         .group_by(Person)
         .order_by(Person.name))

for person in query:
    # "pet_count" becomes an attribute on the returned model instances.
    print(person.name, person.pet_count, 'pets')

# prints:
# Bob 2 pets
# Grandma L. 0 pets
# Herb 1 pets
```

Peewee提供了一个神奇的助手 [`fn()`](https://www.osgeo.cn/peewee/peewee/api.html#fn) ，可用于调用任何SQL函数



### SQL函数

使用SQL函数查找名称以G大写或g小写开头的所有人员

```python
expression = fn.Lower(fn.Substr(Person.name, 1, 1)) == 'g'
for person in Person.select().where(expression):
    print(person.name)

# prints:
# Grandma L.
```

更复杂的查询请参考后面查询章节



## 数据库

数据处理完毕，让我们关闭连接：

```python
db.close()
```

在实际的应用程序中，有一些已建立的模式用于管理数据库连接生存期。例如，Web应用程序通常会在请求开始时打开连接，并在生成响应后关闭连接。数据库连接池能消除一些启动消耗的延迟。





# 第三章 数据库

Peewee [`Database`](https://www.osgeo.cn/peewee/peewee/api.html#Database) 对象表示到数据库的连接。这个 `Database`类是用打开到数据库的连接所需的所有信息实例化的，然后可以用于：

- 打开和关闭连接。
- 执行查询。
- 管理事务（和保存点）。
- 自省表、列、索引和约束。

Peewee支持sqlite、mysql和postgres。每个数据库类都提供一些基本的、特定于数据库的配置选项。

```python
from peewee import *

# SQLite database using WAL journal mode and 64MB cache.
sqlite_db = SqliteDatabase('/path/to/app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})

# Connect to a MySQL database on network.
mysql_db = MySQLDatabase('my_app', user='app', password='db_password',
                         host='10.1.0.8', port=3306)

# Connect to a Postgres database.
pg_db = PostgresqlDatabase('my_app', user='postgres', password='secret',
                           host='10.1.0.9', port=5432)
```

Peewee通过特定于数据库的扩展模块为SQLite、 MySQL 和Postgres提供高级支持。要使用扩展功能，请导入相应的特定于数据库的模块并使用提供的数据库类：

```python
from peewee import *

# SQLite database using WAL journal mode and 64MB cache.
sqlite_db = SqliteDatabase('/path/to/app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})

# Connect to a MySQL database on network.
mysql_db = MySQLDatabase('my_app', user='app', password='db_password',
                         host='10.1.0.8', port=3306)

# Connect to a Postgres database.
pg_db = PostgresqlDatabase('my_app', user='postgres', password='secret',
                           host='10.1.0.9', port=5432)
```



## 初始化数据库

这个 [`Database`](https://www.osgeo.cn/peewee/peewee/api.html#Database) 初始化方法要求将数据库的名称作为第一个参数，在建立连接时，后续的关键字参数将传递给基础数据库驱动程序。

例如，对于PostgreSQL，创建连接时通常需要指定 `host` ， `user` 和 `password` 。这些不是标准的 Peewee `Database`参数，因此 创建连接时它们将直接传递回 `psycopg2`：

```python
db = PostgresqlDatabase(
    'database_name',  # Required by Peewee.
    user='postgres',  # Will be passed directly to psycopg2.
    password='secret',  # Ditto.
    host='db.mysite.com')  # Ditto.
```

如mysql设置 `charset` 参数，也不是标准的 Peewee `Database`参数

```python
db = MySQLDatabase('database_name', user='www-data', charset='utf8mb4')
```



## 使用 Postgresql

要连接到PostgreSQL数据库，我们将使用 [`PostgresqlDatabase`](https://www.osgeo.cn/peewee/peewee/api.html#PostgresqlDatabase) . 第一个参数始终是数据库的名称，之后可以指定任意 psycopg2 参数

```python
psql_db = PostgresqlDatabase('my_database', user='postgres')

class BaseModel(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = psql_db

class User(BaseModel):
    username = CharField()
```

 `Playhouse`是peewee的扩展，包含 Postgresql扩展模块，提供了postgres-specific的特性，如

- [Arrays](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pgarrays)
- [HStore](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#hstore)
- [JSON](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pgjson)
- [Server-side cursors](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#server-side-cursors)
- And more!

如果您想使用这些出色的功能，请使用`playhouse.postgres_ext` 的 `PostgresqlExtDatabase`模块：

```python
from playhouse.postgres_ext import PostgresqlExtDatabase

psql_db = PostgresqlExtDatabase('my_database', user='postgres')
```



### 隔离级别

```python
from psycopg2.extensions import ISOLATION_LEVEL_SERIALIZABLE

db = PostgresqlDatabase('my_app', user='postgres', host='db-host',
                        isolation_level=ISOLATION_LEVEL_SERIALIZABLE)
```



## 使用 SQLite

要连接到sqlite数据库，我们将使用 [`SqliteDatabase`](https://www.osgeo.cn/peewee/peewee/api.html#SqliteDatabase) ，第一个参数是包含数据库的文件名或字符串 ，在数据库文件名之后，可以指定一个列表或pragma或任何其他任意的 sqlite3 参数。

```python
sqlite_db = SqliteDatabase('my_app.db', pragmas={'journal_mode': 'wal'})

class BaseModel(Model):
    """A base model that will use our Sqlite database."""
    class Meta:
        database = sqlite_db

class User(BaseModel):
    username = TextField()
    # etc, etc
```

 peewee提供了SQLite extension ，提供了 SQLite特定的一些功能，比如[full-text search](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html#sqlite-fts), [json extension support](http://docs.peewee-orm.com/en/latest/peewee/sqlite_ext.html#sqlite-json1)

```python
from playhouse.sqlite_ext import SqliteExtDatabase

sqlite_db = SqliteExtDatabase('my_app.db', pragmas={
    'journal_mode': 'wal',  # WAL-mode.
    'cache_size': -64 * 1000,  # 64MB cache.
    'synchronous': 0})  # Let the OS manage syncing.
```



### PRAGMA语句

sqlite允许通过`PRAGMA` 语句设置运行时的配置参数，这些语句通常在创建新的数据库连接时运行。可以将其指定为字典或包含pragma名称和值的2个元组的列表：

```python
db = SqliteDatabase('my_app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': 10000,  # 10000 pages, or ~40MB
    'foreign_keys': 1,  # Enforce foreign-key constraints
})
```

PRAGMAs 也可以使用 `pragma()`方法动态设置或加载 `SqliteDatabase`对象的属性上

```python
# Set cache size to 64MB for *current connection*.
db.pragma('cache_size', -1024 * 64)

# Same as above.
db.cache_size = -1024 * 64

# Read the value of several pragmas:
print('cache_size:', db.cache_size)
print('foreign_keys:', db.foreign_keys)
print('journal_mode:', db.journal_mode)
print('page_size:', db.page_size)

# Set foreign_keys pragma on current connection *AND* on all
# connections opened subsequently.
db.pragma('foreign_keys', 1, permanent=True)
```

使用pragma()方法创建的PRAGMAs在连接关闭后就不存在了，要将pragma配置为在每次打开连接时运行，请指定 `permanent=True` 。



### 推荐设置

以下设置是在典型Web应用程序数据库中与SQLite一起使用的设置：

| pragma                   | 推荐设置          | 解释                            |
| ------------------------ | ----------------- | ------------------------------- |
| journal_mode             | wal               | 允许读写同时存在                |
| cache_size               | -1 * data_size_kb | 设置缓存大小                    |
| foreign_keys             | 1                 | 强制外键约束                    |
| ignore_check_constraints | 0                 | 强制检查约束                    |
| synchronous              | 0                 | 让操作系统处理 fsync (小心使用) |

使用上述设置的示例数据库

```python
db = SqliteDatabase('my_app.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0})
```



### 用户定义的函数

可以使用用户定义的python代码扩展sqlite。这个 [`SqliteDatabase`](https://www.osgeo.cn/peewee/peewee/api.html#SqliteDatabase) 类支持三种类型的用户定义扩展：

- 函数-获取任意数量的参数并返回单个值。
- 聚合-从多行聚合参数并返回单个值。
- 排序规则-描述如何对某个值排序。



```python
db = SqliteDatabase('analytics.db')

from urllib.parse import urlparse

@db.func('hostname')
def hostname(url):
    if url is not None:
        return urlparse(url).netloc

# Call this function in our code:
# The following finds the most common hostnames of referrers by count:
query = (PageView
         .select(fn.hostname(PageView.referrer), fn.COUNT(PageView.id))
         .group_by(fn.hostname(PageView.referrer))
         .order_by(fn.COUNT(PageView.id).desc()))
```

用户定义聚合示例：

```python
from hashlib import md5

@db.aggregate('md5')
class MD5Checksum(object):
    def __init__(self):
        self.checksum = md5()

    def step(self, value):
        self.checksum.update(value.encode('utf-8'))

    def finalize(self):
        return self.checksum.hexdigest()

# Usage:
# The following computes an aggregate MD5 checksum for files broken
# up into chunks and stored in the database.
query = (FileChunk
         .select(FileChunk.filename, fn.MD5(FileChunk.data))
         .group_by(FileChunk.filename)
         .order_by(FileChunk.filename, FileChunk.sequence))
```

排序规则示例：

```python
@db.collation('ireverse')
def collate_reverse(s1, s2):
    # Case-insensitive reverse.
    s1, s2 = s1.lower(), s2.lower()
    return (s1 < s2) - (s1 > s2)  # Equivalent to -cmp(s1, s2)

# To use this collation to sort books in reverse order...
Book.select().order_by(collate_reverse.collation(Book.title))

# Or...
Book.select().order_by(Book.title.asc(collation='reverse'))
```

用户定义的表函数示例：

```python
from playhouse.sqlite_ext import TableFunction

db = SqliteDatabase('my_app.db')

@db.table_function('series')
class Series(TableFunction):
    columns = ['value']
    params = ['start', 'stop', 'step']

    def initialize(self, start=0, stop=None, step=1):
        """
        Table-functions declare an initialize() method, which is
        called with whatever arguments the user has called the
        function with.
        """
        self.start = self.current = start
        self.stop = stop or float('Inf')
        self.step = step

    def iterate(self, idx):
        """
        Iterate is called repeatedly by the SQLite database engine
        until the required number of rows has been read **or** the
        function raises a `StopIteration` signalling no more rows
        are available.
        """
        if self.current > self.stop:
            raise StopIteration

        ret, self.current = self.current, self.current + self.step
        return (ret,)

# Usage:
cursor = db.execute_sql('SELECT * FROM series(?, ?, ?)', (0, 5, 2))
for value, in cursor:
    print(value)

# Prints:
# 0
# 2
# 4
```

有关详细信息，请参阅：

- [`SqliteDatabase.func()`](https://www.osgeo.cn/peewee/peewee/api.html#SqliteDatabase.func)
- [`SqliteDatabase.aggregate()`](https://www.osgeo.cn/peewee/peewee/api.html#SqliteDatabase.aggregate)
- [`SqliteDatabase.collation()`](https://www.osgeo.cn/peewee/peewee/api.html#SqliteDatabase.collation)
- [`SqliteDatabase.table_function()`](https://www.osgeo.cn/peewee/peewee/api.html#SqliteDatabase.table_function)



### 设置事务的锁定模式

可以以三种不同的模式打开SQLite事务：

- *Deferred* (**default**)：仅在执行读或写时获取锁。第一个读操作创建一个共享锁[shared lock](https://sqlite.org/lockingv3.html#locking) ，第一写操作创建一个保留锁[reserved lock](https://sqlite.org/lockingv3.html#locking)。由于锁的获取被延迟到实际需要时，另一个线程或进程可能在当前线程上的begin执行之后，会创建一个单独的事务并写入数据库。
- *Immediate* ：一个保留锁会立马创建。在此模式下，其他数据库不能写入数据库或打开 *immediate* 或*exclusive*事务。其他进程可以继续从数据库中读取数据。
- *Exclusive* ：exclusive lock在当前事务完成之前禁止其他进程连接数据库。

指定锁定模式的示例：

```python
db = SqliteDatabase('app.db')

with db.atomic('EXCLUSIVE'):
    do_something()


@db.atomic('IMMEDIATE')
def some_other_function():
    # This function is wrapped in an "IMMEDIATE" transaction.
    do_something_else()
```



### 高级sqlite驱动程序apsw

Peewee还附带了一个备用的sqlite数据库，该数据库使用 [高级sqlite驱动程序apsw](https://www.osgeo.cn/peewee/peewee/playhouse.html#apsw) 高级python sqlite驱动程序。有关APSW的更多信息，请访问 [APSW project website](https://code.google.com/p/apsw/) . APSW提供以下特殊功能：

- 虚拟表、虚拟文件系统、Blob I/O、备份和文件控制。
- 连接可以跨线程共享，而无需任何附加锁定。
- 事务由代码显式管理。
- 处理Unicode 正确地.
- APSW比标准库sqlite3模块更快。
- 向您的python应用程序公开几乎所有的sqlite c API。

如果要使用APSW，请使用 [`APSWDatabase`](https://www.osgeo.cn/peewee/peewee/playhouse.html#APSWDatabase) 从 apsw_ext 模块：

```
from playhouse.apsw_ext import APSWDatabase

apsw_db = APSWDatabase('my_app.db')
```



## 使用MySQL

要连接到MySQL数据库，我们将使用 [`MySQLDatabase`](https://www.osgeo.cn/peewee/peewee/api.html#MySQLDatabase) ：

```python
mysql_db = MySQLDatabase('my_database')

class BaseModel(Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = mysql_db

class User(BaseModel):
    username = CharField()
    # etc, etc
```



### 错误2006:MySQL服务器已断开

当MySQL终止一个空闲的数据库连接时，可能会发生这个特定的错误。这通常发生在不显式管理数据库连接的Web应用程序上。发生的情况是应用程序启动，连接打开以处理执行的第一个查询，并且，由于该连接从未关闭，它将保持打开状态，等待更多查询。

要解决此问题，请确保在需要执行查询时显式连接到数据库，并在完成后关闭连接。在Web应用程序中，这通常意味着您将在请求进入时打开连接，并在返回响应时关闭连接。

有关配置通用Web框架以管理数据库连接的示例的部分见 [Framework Integration](http://docs.peewee-orm.com/en/latest/peewee/database.html#framework-integration) 



## 使用数据库URL连接

playhouse模块的[Database URL](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#db-url) 提供了一个 [`connect()`](https://www.osgeo.cn/peewee/peewee/playhouse.html#connect) 接受数据库URL并返回 [`Database`](https://www.osgeo.cn/peewee/peewee/api.html#Database) 实例

```python
import os

from peewee import *
from playhouse.db_url import connect

# Connect to the database URL defined in the environment, falling
# back to a local Sqlite database if no database URL is specified.
db = connect(os.environ.get('DATABASE') or 'sqlite:///default.db')

class BaseModel(Model):
    class Meta:
        database = db
```

数据库URL示例：

- `sqlite:///my_database.db` 将在当前地址给文件 `my_database.db` 创建一个 [`SqliteDatabase`](https://www.osgeo.cn/peewee/peewee/api.html#SqliteDatabase) 实例 。
- `sqlite:///:memory:` 将在内存中创建 [`SqliteDatabase`](https://www.osgeo.cn/peewee/peewee/api.html#SqliteDatabase) 实例。
- `postgresql://postgres:my_password@localhost:5432/my_database` 将创建一个 [`PostgresqlDatabase`](https://www.osgeo.cn/peewee/peewee/api.html#PostgresqlDatabase) 实例。提供用户名和密码，以及要连接的主机和端口。
- `mysql://user:passwd@ip:port/my_db` 将创建一个 [`MySQLDatabase`](https://www.osgeo.cn/peewee/peewee/api.html#MySQLDatabase) 本地mysql数据库实例 my_db.
- 更多例子见[db_url documentation](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#db-url).



## 运行时数据库配置

有时数据库连接设置直到运行时才知道，此时可以从配置文件或环境加载这些值。在这种情况下，可以通过指定None作为数据库名来初始化数据库。

```python
database = PostgresqlDatabase(None)  # Un-initialized database.

class SomeModel(Model):
    class Meta:
        database = database
```

果在数据库未初始化时尝试连接或发出任何查询，将出现异常：

```python
>>> database.connect()
Exception: Error, database not properly initialized before opening connection
```

要初始化数据库，请调用 [`init()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.init) 具有数据库名称和任何其他关键字参数的方法：

```python
database_name = input('What is the name of the db? ')
database.init(database_name, host='localhost', user='postgres')
```



## 动态定义数据库

关于更多控制数据库如何定义和初始化，可以使用 [`DatabaseProxy`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DatabaseProxy)

 [`DatabaseProxy`](https://www.osgeo.cn/peewee/peewee/api.html#DatabaseProxy) 对象充当占位符，然后在运行时可以将其替换为其他对象。在下面的示例中，我们将根据应用程序的配置方式交换数据库：

```python
database_proxy = DatabaseProxy()  # Create a proxy for our db.

class BaseModel(Model):
    class Meta:
        database = database_proxy  # Use proxy for our DB.

class User(BaseModel):
    username = CharField()

# Based on configuration, use a different database.
if app.config['DEBUG']:
    database = SqliteDatabase('local.db')
elif app.config['TESTING']:
    database = SqliteDatabase(':memory:')
else:
    database = PostgresqlDatabase('mega_production_db')

# Configure our proxy to use the db we specified in config.
database_proxy.initialize(database)
```

 只有当实际的数据库驱动程序在运行时发生变化时才使用此方法。例如，如果测试和本地开发环境在sqlite上运行，但部署的应用程序使用PostgreSQL，则可以使用 [`DatabaseProxy`](https://www.osgeo.cn/peewee/peewee/api.html#DatabaseProxy) 在运行时更换数据库引擎。

可能更容易避免使用 [`DatabaseProxy`](https://www.osgeo.cn/peewee/peewee/api.html#DatabaseProxy) 而是使用 [`Database.bind()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.bind) 以及设置或更改数据库的相关方法。参见下节内容



## 在运行时设置数据库

我们已经看到了三种使用peewee配置数据库的方法：

```python
# The usual way:
db = SqliteDatabase('my_app.db', pragmas={'journal_mode': 'wal'})


# Specify the details at run-time:
db = SqliteDatabase(None)
...
db.init(db_filename, pragmas={'journal_mode': 'wal'})


# Or use a placeholder:
db = DatabaseProxy()
...
db.initialize(SqliteDatabase('my_app.db', pragmas={'journal_mode': 'wal'}))
```

Peewee还可以为模型类设置或更改数据库。

有两套互补的方法：

- [`Database.bind()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.bind) 和 [`Model.bind()`](https://www.osgeo.cn/peewee/peewee/api.html#Model.bind) -将一个或多个模型绑定到数据库。
- [`Database.bind_ctx()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.bind_ctx) 和 [`Model.bind_ctx()`](https://www.osgeo.cn/peewee/peewee/api.html#Model.bind_ctx) -和他们的 `bind()`一样， 但返回一个上下文管理器，并且在临时更改数据库时非常有用。

例如，我们将声明两个模型 **没有** 指定任何数据库：

```python
class User(Model):
    username = TextField()

class Tweet(Model):
    user = ForeignKeyField(User, backref='tweets')
    content = TextField()
    timestamp = TimestampField()
```

在运行时将模型绑定到数据库：

```python
postgres_db = PostgresqlDatabase('my_app', user='postgres')
sqlite_db = SqliteDatabase('my_app.db')

# At this point, the User and Tweet models are NOT bound to any database.

# Let's bind them to the Postgres database:
postgres_db.bind([User, Tweet])

# Now we will temporarily bind them to the sqlite database:
with sqlite_db.bind_ctx([User, Tweet]):
    # User and Tweet are now bound to the sqlite database.
    assert User._meta.database is sqlite_db

# User and Tweet are once again bound to the Postgres database.
assert User._meta.database is postgres_db
```

这个 [`Model.bind()`](https://www.osgeo.cn/peewee/peewee/api.html#Model.bind) 和 [`Model.bind_ctx()`](https://www.osgeo.cn/peewee/peewee/api.html#Model.bind_ctx) 方法对绑定给定模型类的作用相同：

```python
# Bind the user model to the sqlite db. By default, Peewee will also
# bind any models that are related to User via foreign-key as well.
User.bind(sqlite_db)

assert User._meta.database is sqlite_db
assert Tweet._meta.database is sqlite_db  # Related models bound too.

# Here we will temporarily bind *just* the User model to the postgres db.
with User.bind_ctx(postgres_db, bind_backrefs=False):
    assert User._meta.database is postgres_db
    assert Tweet._meta.database is sqlite_db  # Has not changed.

# And now User is back to being bound to the sqlite_db.
assert User._meta.database is sqlite_db
```



## 线程安全

如果你想在一个多线程运行程序中在运行时更改数据库，在线程锁中存储模型的数据库会阻止

条件竞争。可以使用一个定制模型Metadata完成

```python
from peewee import *
from playhouse.shortcuts import ThreadSafeDatabaseMetadata

class BaseModel(Model):
    class Meta:
        # Instruct peewee to use our thread-safe metadata implementation.
        model_metadata_class = ThreadSafeDatabaseMetadata
```

这样数据库就可以使用熟悉的[`Database.bind()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.bind) or [`Database.bind_ctx()`](http://docs.peewee-orm.com/en/latest/peewee/api.html#Database.bind_ctx)方法在不同线程环境安全的切换。



## 连接管理

要打开到数据库的连接，请使用 [`Database.connect()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.connect) 方法：

要打开到数据库的连接，请使用 [`Database.connect()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.connect) 方法：

```python
>>> db = SqliteDatabase(':memory:')  # In-memory SQLite database.
>>> db.connect()
True
```

如果我们试着调用 `connect()` 在一个已经打开的数据库中，我们得到一个 `OperationalError` ：

```python
>>> db.connect()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/charles/pypath/peewee.py", line 2390, in connect
    raise OperationalError('Connection already opened.')
peewee.OperationalError: Connection already opened.
```

为了防止引发此异常，我们可以调用 `connect()` 再加上一个断点， `reuse_if_open` ：

```python
>>> db.close()  # Close connection.
True
>>> db.connect()
True
>>> db.connect(reuse_if_open=True)
False
```

注意，如果数据库连接已打开，调用 `connect()` 返回`False` 。

要关闭连接，请使用 [`Database.close()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.close) 方法：

```python
>>> db.close()
True
```

调用 `close()` 在已关闭的连接上，不会导致异常，但会返回 `False` 

可以使用 [`Database.is_closed()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.is_closed) 方法判断是否已经关闭：

```python
>>> db.is_closed()
True
```



### 使用自动连接

如果数据库初始化为 `autoconnect=True`(默认)，则在使用之前不会明确连接数据库。明确的管理数据库连接是比较推荐的，因此最好禁用 autoconnect。

明确您的连接生命周期是非常有帮助的，例如，如果连接失败，则在打开连接时将捕获异常，而不是在执行查询后的某个任意时间。

为确保正确性，请禁用 `autoconnect` ：

```python
db = PostgresqlDatabase('my_app', user='postgres', autoconnect=False)
```



### 线程安全

peewee使用线程锁存储跟踪连接状态，使peewee [`Database`](https://www.osgeo.cn/peewee/peewee/api.html#Database) 对象可以安全地与多个线程一起使用。每个线程都有自己的连接，因此任何给定的线程在给定的时间只能有一个打开的连接。



### 上下文管理器

数据库对象本身可以用作上下文管理器，它在打包的代码块期间打开连接。此外，事务在包装块的开头打开，并在连接关闭之前提交（除非发生错误，在这种情况下事务将回滚）。

```python
>>> db.is_closed()
True
>>> with db:
...     print(db.is_closed())  # db is open inside context manager.
...
False
>>> db.is_closed()  # db is closed.
True
```

如果要单独管理事务，可以使用 [`Database.connection_context()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.connection_context) 上下文管理器：

```python
>>> with db.connection_context():
...     # db connection is open.
...     pass
...
>>> db.is_closed()  # db connection is closed.
True
```

这个 `connection_context()` 方法也可以用作修饰器：

```python
@db.connection_context()
def prepare_database():
    # DB connection will be managed by the decorator, which opens
    # a connection, calls function, and closes upon returning.
    db.create_tables(MODELS)  # Create schema.
    load_fixture_data(db
```



## 连接池

连接池由 [playhouse](https://www.osgeo.cn/peewee/peewee/playhouse.html#playhouse) 扩展库的 [pool module](https://www.osgeo.cn/peewee/peewee/playhouse.html#pool) 提供，pool支具有以下功能：

- 超时后将回收连接。
- 打开的连接数的上限。

```python
from playhouse.pool import PooledPostgresqlExtDatabase

db = PooledPostgresqlExtDatabase(
    'my_database',
    max_connections=8,
    stale_timeout=300,
    user='postgres')

class BaseModel(Model):
    class Meta:
        database = db
```

有以下连接池的数据库类可用：

- [`PooledPostgresqlDatabase`](https://www.osgeo.cn/peewee/peewee/playhouse.html#PooledPostgresqlDatabase)
- [`PooledPostgresqlExtDatabase`](https://www.osgeo.cn/peewee/peewee/playhouse.html#PooledPostgresqlExtDatabase)
- [`PooledMySQLDatabase`](https://www.osgeo.cn/peewee/peewee/playhouse.html#PooledMySQLDatabase)
- [`PooledSqliteDatabase`](https://www.osgeo.cn/peewee/peewee/playhouse.html#PooledSqliteDatabase)
- [`PooledSqliteExtDatabase`](https://www.osgeo.cn/peewee/peewee/playhouse.html#PooledSqliteExtDatabase)

有关Peewee连接池的深入讨论，请参见 [playhouse](https://www.osgeo.cn/peewee/peewee/playhouse.html#playhouse) 的 [连接池](https://www.osgeo.cn/peewee/peewee/playhouse.html#pool)文档。



## 框架集成

### Flask

Flask提供两个钩子，我们将使用它们来打开和关闭DB连接。我们将在收到请求时打开连接，然后在返回响应时关闭连接：

```python
from flask import Flask
from peewee import *

database = SqliteDatabase('my_app.db')
app = Flask(__name__)

# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.before_request
def _db_connect():
    database.connect()

# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not database.is_closed():
        database.close()
```



### Django

虽然Peewee和Django一起使用不太常见，但实际上很容易使用这两者。为了管理与Django的Peewee数据库连接，我认为最简单的方法是向应用程序添加中间件。中间件应该是中间件列表中的第一个，以确保它在处理请求时首先运行，在返回响应时最后运行。

如果你有一个叫 *my_blog* 的Django项目，且Peewee数据库定义在 模块中`my_blog.db` ，您可以添加以下中间件类：

```python
# middleware.py
from my_blog.db import database  # Import the peewee database instance.


def PeeweeConnectionMiddleware(get_response):
    def middleware(request):
        database.connect()
        try:
            response = get_response(request)
        finally:
            if not database.is_closed():
                database.close()
        return response
    return middleware


# Older Django < 1.10 middleware.
class PeeweeConnectionMiddleware(object):
    def process_request(self, request):
        database.connect()

    def process_response(self, request, response):
        if not database.is_closed():
            database.close()
        return response
```

为了确保中间件得到执行，请将其添加到 `settings` 模块：

```python
# settings.py
MIDDLEWARE_CLASSES = (
    # Our custom middleware appears first in the list.
    'my_blog.middleware.PeeweeConnectionMiddleware',

    # These are the default Django 1.7 middlewares. Yours may differ,
    # but the important this is that our Peewee middleware comes first.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# ... other Django settings ...
```



### Tornado

Tornado的 `RequestHandler` 类可以执行两个钩子，当处理请求时可以打开和关闭数据库连接：

```python
from tornado.web import RequestHandler

db = SqliteDatabase('my_db.db')

class PeeweeRequestHandler(RequestHandler):
    def prepare(self):
        db.connect()
        return super(PeeweeRequestHandler, self).prepare()

    def on_finish(self):
        if not db.is_closed():
            db.close()
        return super(PeeweeRequestHandler, self).on_finish()
```



### Sanic

在Sanic中，连接处理代码可以放在请求和响应中间件 [sanic middleware](http://sanic.readthedocs.io/en/latest/sanic/middleware.html) 中：

```python
# app.py
@app.middleware('request')
async def handle_request(request):
    db.connect()

@app.middleware('response')
async def handle_response(request, response):
    if not db.is_closed():
        db.close()
```



## 直接执行查询

希望直接执行SQL的情况，可以使用 [`Database.execute_sql()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.execute_sql) 方法：

```python
db = SqliteDatabase('my_app.db')
db.connect()

# Example of executing a simple query and ignoring the results.
db.execute_sql("ATTACH DATABASE ':memory:' AS cache;")

# Example of iterating over the results of a query using the cursor.
cursor = db.execute_sql('SELECT * FROM users WHERE status = ?', (ACTIVE,))
for row in cursor.fetchall():
    # Do something with row, which is a tuple containing column data.
    pass
```



## 管理事务

Peewee提供了几个处理事务的接口。最普遍的是 [`Database.atomic()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.atomic) 方法，它还支持嵌套事务。 [`atomic()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.atomic) 块将在事务或保存点中运行，具体取决于嵌套的级别。

如果包装块中发生异常，则当前事务/保存点将回滚，否则，语句将在包装的语句块末尾提交。

注意：而在一块被 [`atomic()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.atomic) 上下文管理器代码中，可以通过随时调用 `Transaction.rollback()` 或 `Transaction.commit()`来回滚和提交 . 当在包装好的代码块内执行此操作时，将自动启动新事务。

```python
with db.atomic() as transaction:  # Opens new transaction.
    try:
        save_some_objects()
    except ErrorSavingData:
        # Because this block of code is wrapped with "atomic", a
        # new transaction will begin automatically after the call
        # to rollback().
        transaction.rollback()
        error_saving = True

    create_report(error_saving=error_saving)
    # Note: no need to call commit. Since this marks the end of the
    # wrapped block of code, the `atomic` context manager will
    # automatically call commit for us.
```



### 上下文管理器

使用 `atomic` 作为上下文管理器：

```python
db = SqliteDatabase(':memory:')

with db.atomic() as txn:
    # This is the outer-most level, so this block corresponds to
    # a transaction.
    User.create(username='charlie')

    with db.atomic() as nested_txn:
        # This block corresponds to a savepoint.
        User.create(username='huey')

        # This will roll back the above create() query.
        nested_txn.rollback()

    User.create(username='mickey')

# When the block ends, the transaction is committed (assuming no error
# occurs). At that point there will be two users, "charlie" and "mickey".
```

可以使用 `atomic` 执行 *get 或create*操作：

```python
try:
    with db.atomic():
        user = User.create(username=username)
    return 'Success'
except peewee.IntegrityError:
    return 'Failure: %s is already in use.' % username
```



### 装饰器

使用 `atomic` 作为装饰者：

```python
@db.atomic()
def create_user(username):
    # This statement will run in a transaction. If the caller is already
    # running in an `atomic` block, then a savepoint will be used instead.
    return User.create(username=username)

create_user('charlie')
```



### 嵌套事务

[`atomic()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.atomic) 提供事务的透明嵌套。使用时 `atomic()` ，最外部的调用将包装在事务中，并且任何嵌套调用都将使用保存点。

```python
with db.atomic() as txn:
    perform_operation()

    with db.atomic() as nested_txn:
        perform_another_operation()
```



### 显式事务

如果希望在事务中显式运行代码，可以使用 [`transaction()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.transaction) ，像 `atomic()`一样， `transaction()` 可以用作上下文管理器或装饰器。

如果包装块中发生异常，则事务将回滚。否则，语句将在包装块的末尾提交。

```python
db = SqliteDatabase(':memory:')

with db.transaction() as txn:
    # Delete the user and their associated tweets.
    user.delete_instance(recursive=True)
```

事务可以在包装的块中显式提交或回滚。发生这种情况时，将启动一个新事务。

```python
with db.transaction() as txn:
    User.create(username='mickey')
    txn.commit()  # Changes are saved and a new transaction begins.
    User.create(username='huey')

    # Roll back. "huey" will not be saved, but since "mickey" was already
    # committed, that row will remain in the database.
    txn.rollback()

with db.transaction() as txn:
    User.create(username='whiskers')
    # Roll back changes, which removes "whiskers".
    txn.rollback()

    # Create a new row for "mr. whiskers" which will be implicitly committed
    # at the end of the `with` block.
    User.create(username='mr. whiskers')
```

注意：如果尝试使用peewee嵌套事务，请使用 `transaction()`上下文管理器，只使用最外部的事务。但是，如果嵌套块中发生异常，这可能会导致不可预测的行为，因此强烈建议您使用 `atomic()`



### 显式保存点

正如可以显式创建事务一样，也可以使用 [`savepoint()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.savepoint) 方法。保存点必须出现在事务中，但可以任意深度嵌套。

```python
with db.transaction() as txn:
    with db.savepoint() as sp:
        User.create(username='mickey')

    with db.savepoint() as sp2:
        User.create(username='zaizee')
        sp2.rollback()  # "zaizee" will not be saved, but "mickey" will be.
```

注意L如果你手动提交或回滚一个savepoint，将不会在自动创建一个新的savepoint。这与`transaction`是不同的



### 自动提交模式

默认情况下，Peewee在 自动提交模式, 这样，在事务外部执行的任何语句都在自己的事务中运行。要将多个语句分组为一个事务，peewee提供 [`atomic()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.atomic) 上下文管理器/装饰器。这应该涵盖所有用例，但在不太可能的情况下，您希望暂时完全禁用Peewee的事务管理，您可以使用 [`Database.manual_commit()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.manual_commit) 上下文管理器/装饰器。

以下是您如何模拟 [`transaction()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.transaction) 上下文管理器：

```python
with db.manual_commit():
    db.begin()  # Have to begin transaction explicitly.
    try:
        user.delete_instance(recursive=True)
    except:
        db.rollback()  # Rollback! An error occurred.
        raise
    else:
        try:
            db.commit()  # Commit changes.
        except:
            db.rollback()
            raise
```



## 数据库错误

peewee中的常见的异常类：

- `DatabaseError`
- `DataError`
- `IntegrityError`
- `InterfaceError`
- `InternalError`
- `NotSupportedError`
- `OperationalError`
- `ProgrammingError`

所有这些错误类都扩展 自`PeeweeException`



## 日志查询

所有查询都记录到 *peewee* 使用标准库的命名空间 `logging` 模块。查询记录使用 *DEBUG* 等级。如果您对查询感兴趣，可以简单地注册一个处理程序。

```python
# Print all queries to stderr.
import logging
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
```





# 第四章 模型和字段

Model类， Field 实例和模型实例都映射到数据库概念：

| 事件     | 对应于…        |
| :------- | :------------- |
| 模型类   | 数据库表       |
| 字段实例 | 表上的列       |
| 模型实例 | 数据库表中的行 |

下面是经典的使用方法：

```python
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
```

步骤有

1.创建一个数据库实例

```python
db = SqliteDatabase('my_app.db')
```

db对象用来管理数据库的连接

2.创建一个指定数据库的基础模型类

```python
class BaseModel(Model):
    class Meta:
        database = db
```

定义一个建立数据库连接的基础模型类，后面继承他的子类都不用再定义数据库了，模型的配置在Meta类里。

3.定义一个模型类

```python
class User(BaseModel):
    username = CharField(unique=True)
```

继承了BaseModel，所以 User 模型将继承数据库连接。

我们已经明确定义了一个 username 具有唯一约束的列。因为我们没有指定主键，Peewee将自动添加一个名为 id。



## 字段

 Field 类用于描述 Model 数据库列的属性，每个字段类型都有一个对应的SQL存储类（即varchar、int），并且可以透明地处理python数据类型和底层存储之间的转换。

### 字段类型表

| Field Type          | Sqlite        | Postgresql       | MySQL            |
| ------------------- | ------------- | ---------------- | ---------------- |
| `AutoField`         | integer       | serial           | integer          |
| `BigAutoField`      | integer       | bigserial        | bigint           |
| `IntegerField`      | integer       | integer          | integer          |
| `BigIntegerField`   | integer       | bigint           | bigint           |
| `SmallIntegerField` | integer       | smallint         | smallint         |
| `IdentityField`     | not supported | int identity     | not supported    |
| `FloatField`        | real          | real             | real             |
| `DoubleField`       | real          | double precision | double precision |
| `DecimalField`      | decimal       | numeric          | numeric          |
| `CharField`         | varchar       | varchar          | varchar          |
| `FixedCharField`    | char          | char             | char             |
| `TextField`         | text          | text             | text             |
| `BlobField`         | blob          | bytea            | blob             |
| `BitField`          | integer       | bigint           | bigint           |
| `BigBitField`       | blob          | bytea            | blob             |
| `UUIDField`         | text          | uuid             | varchar(40)      |
| `BinaryUUIDField`   | blob          | bytea            | varbinary(16)    |
| `DateTimeField`     | datetime      | timestamp        | datetime         |
| `DateField`         | date          | date             | date             |
| `TimeField`         | time          | time             | time             |
| `TimestampField`    | integer       | integer          | integer          |
| `IPField`           | integer       | bigint           | bigint           |
| `BooleanField`      | integer       | boolean          | bool             |
| `BareField`         | untyped       | not supported    | not supported    |
| `ForeignKeyField`   | integer       | integer          | integer          |



### 字段初始化参数

- null = False --允许空值
- index = False --在此列上创建索引
- unique = False --在此列上创建唯一索引
- column_name = None --在数据库中显式指定列名
- default = None --默认值
- primary_key = False --表的主键
- constraints = None - 约束，如[Check('price > 0')]
- sequence = None --序列名（如果后端支持）
- collation = None --用于排序字段/索引的排序规则
- unindexed = False --指示应取消对虚拟表上的字段的索引（sqlite only*）
- choices = None -- 可选择的包含二元数组的可迭代对象
- help_text = None --表示此字段的任何有用文本的字符串
- verbose_name = None --表示此字段的“用户友好”名称的字符串
- index_type = None --指定自定义索引类型，例如，对于Postgres，可以指定 'BRIN' 或 'GIN' 索引

注意：default和choices都可以在数据库级别实现，分别为DEFAULT 和 CHECK CONSTRAINT。但是，任何应用程序更改都需要模式更改。因此，default仅仅应用在python里，choices没有经过验证，但是目的仅是存在于元数据



### 一些字段的特殊参数

| Field type                                                   | Special Parameters                                           |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [`CharField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CharField) | `max_length`                                                 |
| [`FixedCharField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#FixedCharField) | `max_length`                                                 |
| [`DateTimeField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DateTimeField) | `formats`                                                    |
| [`DateField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DateField) | `formats`                                                    |
| [`TimeField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#TimeField) | `formats`                                                    |
| [`TimestampField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#TimestampField) | `resolution`, `utc`                                          |
| [`DecimalField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#DecimalField) | `max_digits`, `decimal_places`, `auto_round`, `rounding`     |
| [`ForeignKeyField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#ForeignKeyField) | `model`, `field`, `backref`, `on_delete`, `on_update`, `deferrable` `lazy_load` |
| [`BareField`](http://docs.peewee-orm.com/en/latest/peewee/api.html#BareField) | `adapt`                                                      |



### 默认字段值

创建对象时，peewee可以为字段提供默认值

```python
class Message(Model):
    context = TextField()
    read_count = IntegerField(default=0)
```

在某些情况下，默认值可能是动态的。一个常见的场景是使用当前日期和时间。

Peewee允许您在这些情况下指定一个函数，其返回值将在创建对象时使用。

```python
class Message(Model):
    context = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
```

注意：如果使用的字段接受可变类型（list， dict, 等），并且希望提供默认值，最好将默认值包装在一个简单函数中，这样多个模型实例就不会共享对同一基础对象的引用：

```python
def house_defaults():
    return {'beds': 0, 'baths': 0}
class House(Model):
    number = TextField()
    street = TextField()
    attributes = JSONField(default=house_defaults)
```

数据库还可以提供字段的默认值。虽然peewee没有显式地提供用于设置服务器端默认值的API，但是可以使用 constraints 用于指定服务器默认值的参数：

```python
class Message(Model):
    context = TextField()
    timestamp = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
```

注意：使用 default 参数，这些值由peewee设置，而不是作为实际表和列定义的一部分。



### 外键

允许一个模型引用另一个模型的特殊字段类型，通常，外键将包含与其相关的模型的主键（但可以通过field指定）。有一个外键来自 Tweet 到 User ，这意味着所有用户都存储在自己的表中，tweet也是如此，而从tweet到user的外键允许每个tweet指到特定的用户对象。

在peewee中，访问 ForeignKeyField 将返回整个相关对象：

```python
tweets = Tweet.select().order_by(Tweet.created_date.desc())
for tweet in tweets:
    # WARNING: an additional query will be issued for EACH tweet
    # to fetch the associated User data.
    print(tweet.user.username, tweet.message)
```

有时，您只需要外键列中关联的主键值，在这种情况下，Peewee遵循Django建立的惯例，允许您通过追加 "_id" 到外键字段的名称：

```python
weets = Tweet.select()
for tweet in tweets:
    # Instead of "tweet.user", we will just get the raw ID value stored
    # in the column.
    print(tweet.user_id, tweet.message)
```

为了防止意外解析外键并触发其他查询， ForeignKeyField 支持初始化参数 lazy_load 当被禁用时，其行为类似于 "_id" 属性。例如：

```python
class Tweet(Model):
    # ... same fields, except we declare the user FK to have
    # lazy-load disabled:
    user = ForeignKeyField(User, backref='tweets', lazy_load=False)
for tweet in Tweet.select():
    print(tweet.user, tweet.message)
```

通过禁用lazy_load, 访问 tweet.user will 不会有额外的查询，而是直接返回user ID。



### 反向引用

ForeignKeyField 允许将反向引用属性绑定到目标模型，默认的，此属性将被命名为 classname_set，classname 是class的小写字母，但可以使用参数 backref 重写。

```python
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
```



###  DateTimeField, DateField and TimeField

用于处理日期和时间的三个字段具有特殊属性，允许访问年、月、小时等内容。

DateField具有的属性：year、month、day

TimeField具有的属性：hour、minute、second

DateTimeField具有以上两者所有属性

这些属性可以像任何其他表达式一样使用：

```python
now = datetime.datetime.now()
Event.select(Event.event_date.day.alias('day')).where(
    (Event.event_date.year == now.year) &
    (Event.event_date.month == now.month))
```



### 自定义字段

在Peewee中，很容易添加对自定义字段类型的支持。

要添加自定义字段类型，首先需要确定字段数据将存储在哪种类型的列中。比如如果你想把decimal字段加到python行为上，只要写一个继承 DecimalField的子类。另外，如果要让知道peewee知道你添加的字段，则由Field.field_type属性控制。

在这个例子中，我们将为PostgreSQL创建一个UUID字段：

```python
class UUIDField(Field):
    field_type = 'uuid'
```

因为psycopg2会把字段默认看做 string类型, 需要添加两个方法去处理:

```python
import uuid

class UUIDField(Field):

    field_type = 'uuid'

    def db_value(self, value):
        return value.hex  # convert UUID to hex string.

    def python_value(self, value):
        return uuid.UUID(value) # convert hex string to UUID
```

此步骤是可选的，默认field_type会在数据库模式里被用作列的数据类型。如果你想把这个字段用在不同数据库做不同类型，就需要让数据库知道映射关系。

在Postgres中，我们把自定义的UUIDField转为UUID类型：

```python
db = PostgresqlDatabase('my_db', field_types={'uuid': 'uuid'})
```

在Sqlite没有 UUID字段, 我们转为text类型：

```python
db = SqliteDatabase('my_db', field_types={'uuid': 'text'})
```



## 创建表

为了创建表，必须先打开到数据库的连接再创建表。Peewee将运行必要的 CREATE TABLE 查询，另外创建任何约束和索引。

```python
# Connect to our database.
from models import db_mysql, User, Tweet

db_mysql.connect()
# Create the tables.
db_mysql.create_tables([User, Tweet])
```

默认情况下，peewee创建表时使用包括 IF NOT EXISTS。如果要禁用此功能，请指定 safe=False。

如果要更改模型，可参考 schema migrations 的细节。



## 模型选项和metadata

为了不污染模型的命名空间，模型特定的配置被放在 Meta类里：

```python
from peewee import *

contacts_db = SqliteDatabase('contacts.db')

class Person(Model):
    name = CharField()

    class Meta:
        database = contacts_db
```

一旦定义了类，就不应该访问 ModelClass.Meta ，而是使用 ModelClass._meta：

```python
print(Person._meta)  # <peewee.Metadata object at 0x0000028716A2BB00>
```

 ModelOptions 类实现了几种可能用于检索模型元数据的方法（例如字段列表、外键关系等）：

```python
print(Person._meta.fields)
print(Person._meta.primary_key)
print(Person._meta.database)
```

下面有一些meta属性选项，大部分都是可继承的：

| Option               | Meaning                                                      | Inheritable? |
| -------------------- | ------------------------------------------------------------ | ------------ |
| `database`           | database for model                                           | yes          |
| `table_name`         | name of the table to store data                              | no           |
| `table_function`     | function to generate table name dynamically                  | yes          |
| `indexes`            | a list of fields to index                                    | yes          |
| `primary_key`        | a [`CompositeKey`](http://docs.peewee-orm.com/en/latest/peewee/api.html#CompositeKey) instance | yes          |
| `constraints`        | a list of table constraints                                  | yes          |
| `schema`             | the database schema for the model                            | yes          |
| `only_save_dirty`    | when calling model.save(), only save dirty fields            | yes          |
| `options`            | dictionary of options for create table extensions            | yes          |
| `table_settings`     | list of setting strings to go after close parentheses        | yes          |
| `temporary`          | indicate temporary table                                     | yes          |
| `legacy_table_names` | use legacy table name generation (enabled by default)        | yes          |
| `depends_on`         | indicate this table depends on another for creation          | no           |
| `without_rowid`      | indicate table should not have rowid (SQLite only)           | no           |
| `strict_tables`      | indicate strict data-types (SQLite only, 3.37+)              | yes          |

下面是一个显示可继承属性与不可继承属性：

```python
db = SqliteDatabase(':memory:')
class ModelOne(Model):
    class Meta:
        database = db
        table_name = 'model_one_tbl'
class ModelTwo(ModelOne):
    pass
print( ModelOne._meta.database is ModelTwo._meta.database)  # True
print(ModelOne._meta.table_name == ModelTwo._meta.table_name)  # False
```



### meta主键

这个 Meta.primary_key 属性用于指定 CompositeKey 或者表示模无主键，要指示模型不应具有主键，请设置 primary_key = False

```python
class Blog(Model):
    pass
class Tag(Model):
    pass

class BlogToTag(Model):
    """A simple "through" table for many-to-many relationship."""
    blog = ForeignKeyField(Blog)
    tag = ForeignKeyField(Tag)
    class Meta:
        primary_key = CompositeKey('blog', 'tag')

class NoPrimaryKey(Model):
    data = IntegerField()
    class Meta:
        primary_key = False
```



### 表名

默认情况下，peewee将根据模型类的名称自动生成表名。表名的生成方式取决于 Meta.legacy_table_names。默认情况下， legacy_table_names=True 以避免破坏向后兼容性。但是，如果希望使用新的和改进的表名生成，可以指定 legacy_table_names=False。

注意：为了保持向后兼容性，当前版本（peewee 3.x）默认情况下legacy_table_names=True。在下一个主要版本（Peewee 4.0）中， legacy_table_names 将具有默认值 False。

要显式指定模型类的表名，请使用 table_name meta选项。

```python
class UserProfile(Model):
    class Meta:
        table_name = 'user_profile_tbl'
```

如果希望实现自己的命名约定，可以指定 table_function meta选项。此函数将与模型类一起调用，并应以字符串形式返回所需的表名。

假设我们公司指定表名的大小写应为小写，并以“_tbl”结尾，我们可以将其作为表函数来实现：

```python
def make_table_name(model_class):
    model_name = model_class.__name__
    return model_name.lower() + '_tbl'
class BaseModel(Model):
    class Meta:
        table_function = make_table_name
class User(BaseModel):
    pass
    # table_name will be "user_tbl".
class UserProfile(BaseModel):
    pass
    # table_name will be "userprofile_tbl".
```



### 索引和约束

Peewee可以在单个或多个列上创建索引，也可以选择包括 UNIQUE 约束。Peewee还支持对模型和字段的用户定义约束。

1.单列索引和约束

用字段初始化参数定义单列索引：

```python
class User(Model):
    username = CharField(unique=True)
    email = CharField(index=True)
```

添加用户自定义约束，可以使用constraints参数：

```python
class Product(Model):
    name = CharField(unique=True)
    price = DecimalField(constraints=[Check('price < 10000')])
    created = DateTimeField(
        constraints=[SQL("DEFAULT (datetime('now'))")])
```



2.多列索引

多列索引使用嵌套元组定义为 Meta的属性，每个数据库索引都是一个2元组，第一部分是字段名称的元组，第二部分是指示索引是否应唯一的布尔值。

```python
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
```



3.高级索引创建

Peewee支持更结构化的API，使用Model.add_index()或直接使用ModelIndex辅助类：

```python
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
```



4.表约束

Peewee允许给model添加任意的表约束，当模式创建的时候将成为表的定义的一部分。

现在有个Person类，有个复合主键，'first'和 'last'，如果想另一个表关联Person这个表，因此需要一个外键约束：

```python
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
```

也可以在表级里定义CHECK约束：

```python
class Product(Model):
    name = CharField(unique=True)
    price = DecimalField()

    class Meta:
        constraints = [Check('price < 10000')]
```



### 主键和复合主键

1.自增长主键

AutoField 用于标识自动递增的整数主键。如果不指定主键，peewee将自动创建一个名为“id”的自动递增主键。要使用其他字段名指定自动递增的ID，可以写入：

```python
class Event(Model):
    event_id = AutoField()  # Event.event_id will be auto-incrementing PK.
    name = CharField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    metadata = BlobField()
```

如果定义一个其他字段作为主键，将不会自动创建主键'id'。

复合主键可以使用 CompositeKey 。请注意，这样做可能会导致 ForeignKeyField 因为Peewee不支持“复合外键”的概念。

因此，只有在少数情况下使用复合主键才是明智的，例如琐碎的多对多连接表：

```python
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
```

极少数情况下不想要主键，可以设置meta属性为primary_key = False。



2.非整数主键

如果要使用非整数主键（我通常不建议使用），可以创建字段时指定 primary_key=True 。

注意当使用非自动增量主键为模型创建一个新实例时，需要确保 save() 并指定 force_insert=True。

```python
class UUIDModel(Model):
    id = UUIDField(primary_key=True)
```

自增长ID，向数据库中插入新行时，会自动生成自动递增的ID，当调用save()时，peewee会根据主键的值决定执行insert还是update。

但是如上面UUIDModel的例子，没有自增长id，我们需要手动的明确指出，第一次调用save()，需要force_insert = True：

```python
# This works because .create() will specify `force_insert=True`.
obj1 = UUIDModel.create(id=uuid.uuid4())
# This will not work, however. Peewee will attempt to do an update:
obj2 = UUIDModel(id=uuid.uuid4())
obj2.save() # WRONG
obj2.save(force_insert=True) # CORRECT
# Once the object has been created, you can call save() normally.
obj2.save()
```



3.复合主键

使用组合键，必须设置 primary_key 模型选项的属性 CompositeKey 实例：

```python
class Blog(Model):
    pass
class BlogToTag(Model):
    """A simple "through" table for many-to-many relationship."""
    blog = ForeignKeyField(Blog)
    tag = ForeignKeyField(Tag)

    class Meta:
        primary_key = CompositeKey('blog', 'tag')
```



4.手动指定主键

有时，您不希望数据库自动为主键生成值，例如在批量加载关系数据时。在一次性的基础上处理这个请求，你可以在导入过程中简单地告诉Peewee关掉 auto_increment ：

```python
data = load_user_csv() # load up a bunch of data

User._meta.auto_increment = False # turn off auto incrementing IDs
with db.atomic():
    for row in data:
        u = User(id=row[0], username=row[1])
        u.save(force_insert=True) # <-- force peewee to insert row

User._meta.auto_increment = True
```



5.无主键模型

如果要创建没有主键的模型，可以指定 primary_key = False

```python
class MyData(BaseModel):
    timestamp = DateTimeField()
    value = IntegerField()

    class Meta:
        primary_key = False
```

对于没有主键的模型，某些模型API可能无法正常工作，如 save() 和 delete_instance()。可以使用insert(), update() and delete())代替。



# 第五章 查询

这一部分将包含基础增删改查操作

## 增

### 单条插入

模型如下

```python
from peewee import *


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
```



1.Model.create()

```python
User.create(username='Charlie')
```

2. call save()

```python
user = User(username='Charlie')
user.save()

huey = User()
huey.username = "huey"
huey.save()
print(huey.id)
```

```python
# 创建外键
# 1.直接使用对象
huey = User.select().where(User.id==3).first()
tweet = Tweet.create(user=huey, message='Hello!')
# 2.使用id
tweet = Tweet.create(user=2, message='Hello again!')
```

3.Model.insert()

```python
User.insert(username='Mickey').execute()
```

执行完成会返回记录的主键



### 批量插入

1.Model.create() in a loop

```python
data_source = [
    {'field1': 'val1-1', 'field2': 'val1-2'},
    {'field1': 'val2-1', 'field2': 'val2-2'},
]
for data_dict in data_source:
    MyModel.create(**data_dict)
```

这个方法会很慢，因为：

1.如果不在事务中包装循环，则每次调用 create() 发生在它自己的事务中。那真是太慢了
2.上述代码有相当多的python逻辑，并且 InsertQuery 必须生成并解析为SQL
3.我们正在检索 上次插入ID, 这会导致在某些情况下执行额外的查询。



2. 将其包装在事务中 atomic()

```python
with db.atomic():
    for data_dict in data_source:
        MyModel.create(**data_dict)
```

比循环快一点，但是仍然受2,3影响



3.使用insert_many()

```python
MyModel.insert_many(data_source).execute()
```

这个 insert_many() 方法还接受行元组列表，前提是还指定了相应的字段:

```python
data = [('val1-1', 'val1-2'),
        ('val2-1', 'val2-2'),
        ('val3-1', 'val3-2')]
# But we need to indicate which fields the values correspond to.
MyModel.insert_many(data, fields=[MyModel.field1, MyModel.field2]).execute()
```

在事务中使用insert_many:

```python
with db.atomic():
    MyModel.insert_many(data, fields=[MyModel.field1, MyModel.field2]).execute()
```



4.chunked大批量插入

```python
# Insert rows 100 at a time.
from peewee import chunked
with db.atomic():
    for batch in chunked(data_source, 100):
        MyModel.insert_many(batch).execute()
```



5.Model.bulk_create()

```python
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
```

```python
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
```



6.从另一个表的查询记录插入新数据

```python
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
```



## 删

 1.delete_instance()

```python
user = User2.get(User2.id == 4)
user.delete_instance()
```

2.Model.delete_instance()

```python
# 删除满足条件的多个实例
query = Tweet.delete().where(Tweet.id > 3)
query.execute() # 返回删除的行数
```



## 改

### 1.model.update()

```python
query = Tweet.update(is_published=True).where(Tweet.creation_date <  datetime.today())
query.execute()

#  atomic updates
query = Stat.update(counter=Stat.counter + 1).where(Stat.url == request.url)
query.execute()

#
query = Employee.update(bonus=(Employee.bonus + (Employee.salary * .1)))
query.execute()  # Give everyone a bonus!

#
subquery = Tweet.select(fn.COUNT(Tweet.id)).where(Tweet.user == User.id)
update = User.update(num_tweets=subquery)
update.execute()
```



### 2.upsert()

1.replace和on_conflict_replace

插入或更新user,主键冲突就更新，否则插入

```python
user_id = User2.replace(username="the-user", last_login=datetime.now()).execute()
```

下面这个也是等价的

```python
user_id = User2.insert(id=4, username='the-user', last_login=datetime.now())\
    .on_conflict_replace().execute()
```

2.on_conflict_ignore()

有主键冲突就忽略，不进行插入操作

```python
user_id = User2.insert(id=4, username='the-user4', last_login=datetime.now())\
     .on_conflict_ignore().execute()
```

3.on_conflict()

提供插入时如何解决冲突，参数如下：

- conflict_target：构成约束的列(Postgresql and SQLite 支持)
- preserve，冲突时，更新值为insert语句里的值，如insert里last_login=now，则冲突last_login就更新为now
- update：冲突时，字段的更精细的控制

```python
User2.create(username='huey', login_count=0)
now = datetime.now()
rowid = (User2
         .insert(id=6, username='huey', last_login=now, login_count=1)
         .on_conflict(
             preserve=[User2.last_login],  # Use the value we would have inserted.
             update={User2.login_count: User2.login_count + 1})
         .execute())
```



## 查

### 获取单个记录

```python
# 1.Model.get()
user = User.get(User.id == 1)
print(user.username)


# 2.Model.get_by_id()
# 主键查找
user = User.get_by_id(1)
print(user.username)
```



### 创建或获取

Model.get_or_create()，尝试检索匹配的行，如果失败，将创建一个新行。参数如下：

defaults：create时字段的值

defaults之外的为get查询时的条件

```python
person, created = Person.get_or_create(
    first_name="Bob",
    defaults={'birthday': datetime.date(1940, 10, 9)})
```



### 查询多条

1.Model.select()

返回多行记录，支持迭代、索引、切片

```python
query = User.select()
print([user.username for user in query])

print( query[1])
print(query[1].username)
print(query[:2])
```



2.查询外键

```python
user = User.get(User.id == 2)
tweet = Tweet.get_by_id(3)
for user in tweet.user:
	print(tweet.user.username)
```



3.查询结果转为字典等其他格式

有dicts()、namedtuples()、tuples()

```python
query = User.select().dicts()
for row in query:
    print(row)
```



扩展内容：性能提升

4.iterator()

peewee 默认缓存查询结果，如果数据量很大，不想缓存，则使用iterator()。

```python
# Let's assume we've got 10 million stat objects to dump to a csv file.
stats = Stat.select()
# Our imaginary serializer class
serializer = CSVSerializer()
# Loop over all the stats and serialize.
for stat in stats.iterator():
    serializer.serialize_object(stat)
```



5.query.objects()

当遍历包含多个表中的列的大量行时，Peewee将为返回的每一行重建模型图，此操作可能很慢。例如，如果我们选择一个tweet列表以及tweet作者的用户名和化身，那么peewee必须为每行创建两个对象（tweet和一个用户）。objects() 它将以模型实例的形式返回行，但不会尝试解析模型图。

```python
query = (Tweet
         .select(Tweet, User)  # Select tweet and user data.
         .join(User))
# Note that the user columns are stored in a separate User instance
# accessible at tweet.user:
for tweet in query:
    print(tweet.user.username, tweet.content)
# Using ".objects()" will not create the tweet.user object and assigns all
# user attributes to the tweet instance:
for tweet in query.objects():
    print(tweet.username, tweet.content)
```



6.Database.execute()

为了获得最大的性能，可以执行查询，然后使用底层数据库光标迭代结果，光标将返回原始行元组。

```python
query = Tweet.select(Tweet.content, User.username).join(User)
cursor = db_mysql.execute(query)
for (content, username) in cursor:
    print(username, '->', content)
```



### 筛选

1.get(筛选条件)

```python
user = User.get(User.username == 'Charlie')
print(user)
```

2.select().where()

```python
for tweet in Tweet.select().where(Tweet.user == user, Tweet.is_published == True):
     print(tweet.user.username, '->', tweet.message)
```

3.跨表筛选

```python
for tweet in Tweet.select().join(User).where(User.username == 'Charlie'):
     print(tweet.message)
```

4.多条件查询

```python
Tweet.select().join(User).where((User.username == 'Charlie') | (User.username == 'Peewee Herman'))
# &：和 
# |：或
```



### 排序

1.order_by()

```python
for t in Tweet.select().order_by(Tweet.creation_date):
     print(t.creation_date)
for t in Tweet.select().order_by(Tweet.creation_date.desc())
:
     print(t.creation_date)
# 也可以使用+和-控制排序顺序
Tweet.select().order_by(-Tweet.creation_date)
```



### 随机获取

```python
# 1.Postgresql and Sqlite use the Random function:
# Pick 5 lucky winners:
LotteryNumber.select().order_by(fn.Random()).limit(5)


# 2.MySQL uses Rand:
LotteryNumber.select().order_by(fn.Rand()).limit(5)
```



### 分页

```python
# 1.paginate(page, paginate_by )
# 参数：page：页数，从1开始；paginate_by：每页记录数
for tweet in Tweet.select().order_by(Tweet.id).paginate(1, 10):
    print(tweet.message)
```

也可以使用 limit() and offset()



### 计数

```python
count = Tweet.select().where(Tweet.id < 50).count()
print(count)
```



### 聚合

1.group_by

```python
query = (User
         .select(User, fn.Count(Tweet.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User))

for q in query:
    print(q.username, " -> ", q.count)
```

2.having

```python
query = (User
         .select(User, fn.Count(Tweet.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User)
         .having(fn.Count(Tweet.id)>0))

for q in query:
    print(q.username, " -> ", q.count)
```



### 找查询结果标量

```python
# Query.scalar()
# 参考官方文档示例
PageView.select(fn.Count(fn.Distinct(PageView.url))).scalar()
# 多个标量使用as_tuple=True
Employee.select(fn.Min(Employee.salary), fn.Max(Employee.salary)).scalar(as_tuple=True)
```



### 窗口函数

窗口函数在滑动窗口数据上和是和聚合函数结合，作为select过程的一部分。

窗口函数功能：

  1.对结果集的子集执行聚合
  2.计算运行总数
  3.排序结果
  4.比较行与行的值

可以通过调用 Function.over() 并传入分区或排序参数



1.Ordered Windows

1.1计算累计和

根据Sample.counter排序，计算Sample.value累计和

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(order_by=[Sample.counter]).alias('total'))
for sample in query:
    print(sample.counter, sample.value, sample.total)
```

1.2计算前后差值

按照Sample.id排序，计算前后Sample.value的差值

```python
# fn.LAG取前n行
difference = Sample.value - fn.LAG(Sample.value, 1).over(order_by=[Sample.id])
query = Sample.select(
    Sample.counter,
    Sample.value,
    difference.alias('diff'))
for sample in query:
    print(sample.counter, sample.value, sample.diff)
```



2.Partitioned Windows

2.1 以counter分组计算value平均值

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.AVG(Sample.value).over(partition_by=[Sample.counter]).alias('cavg'))
for sample in query:
    print(sample.counter, sample.value, sample.cavg)
```

2.2 在窗口内结合使用order_by

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.RANK().over(
        order_by=[Sample.value],
        partition_by=[Sample.counter]).alias('rank'))
for sample in query:
    print(sample.counter, sample.value, sample.rank)
```



3.Bounded windows 

有界窗口

默认窗口是从第一行到最后一行，可以使用有界窗口约束窗口边界
  1.Window.CURRENT_ROW - 引用当前行的属性
  2.Window.preceding() - 指定前面的行数，忽略表示前面所有
  3.Window.following() - 指定后面的行数，忽略表示前面所有

3.1 前面两行到当前行

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.id],
        start=Window.preceding(2),
        end=Window.CURRENT_ROW).alias('rsum'))
for sample in query:
    print(sample.counter, sample.value, sample.rsum)
#  end=Window.CURRENT不需要特别说明，是默认值
```

3.2 计算当前行到最后一行的和

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.id],
        start=Window.CURRENT_ROW,
        end=Window.following()).alias('rsum'))
for sample in query:
    print(sample.counter, sample.value, sample.rsum)
```



4.Filtered Aggregates

只适用于(Postgres and Sqlite 3.25+）,filter()要在 over()之前

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).filter(Sample.counter != 2).over(
        order_by=[Sample.id]).alias('csum'))
for sample in query:
    print(sample.counter, sample.value, sample.csum)
# 1    10.    10.
# 1    20.    30.
# 2     1.    30.
# 2     3.    30.
# 3   100    130.
# 累加的时候跳过counter为2的
```



5.Reusing Window Definitions

定义窗口再使用

```python
# 提前定义一个窗口，多次使用
win = Window(order_by=[Sample.id])
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.LEAD(Sample.value).over(win),
    fn.LAG(Sample.value).over(win),
    fn.SUM(Sample.value).over(win)
    ).window(win)
for row in query.tuples():
    print(row)
```



 6.Multiple window definitions

 要确保每个窗口有唯一的alias

6.1 多个定义窗口

```python
w1 = Window(order_by=[Sample.id]).alias('w1')
w2 = Window(partition_by=[Sample.counter]).alias('w2')
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(w1).alias('rsum'),  # Running total.
    fn.AVG(Sample.value).over(w2).alias('cavg')   # Avg per category.
).window(w1, w2)  # Include our window definitions.
for sample in query:
    print(sample.counter, sample.value, sample.rsum, sample.cavg)
```

6.2扩展窗口

```python
w1 = Window(partition_by=[Sample.counter]).alias('w1')
w2 = Window(extends=w1, order_by=[Sample.value.desc()]).alias('w2')
query = (Sample
         .select(Sample.counter, Sample.value,
                 fn.SUM(Sample.value).over(w1).alias('group_sum'),
                 fn.RANK().over(w2).alias('revrank'))
         .window(w1, w2)
         .order_by(Sample.id))
for sample in query:
    print(sample.counter, sample.value, sample.group_sum, sample.revrank)
```



7.Frame types参数

 Window.RANGE：如果有重复项，会把所有重复项一起聚合
 Window.ROWS：如果有重复项，会把所有重复项分开为每行聚合
 Window.GROUPS：mysql不支持

```
# 现在数据如下：
# id   counter    value
# 1        1      10.0
# 2        1      20.0
# 3        2      1.0
# 4        2      3.0
# 5        3      100.0
# 6        1      20.0
# 7        2      1.0
```

7.1 Window.RANGE

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.counter, Sample.value],
        frame_type=Window.RANGE).alias('rsum'))
for sample in query.order_by(Sample.counter, Sample.value):
    print(sample.counter, sample.value, sample.rsum)
# counter为20的有两个，所以计算累加时，两个同时全部加上
```

7.2 Window.ROWS

```python
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.counter, Sample.value],
        frame_type=Window.ROWS).alias('rsum'))
for sample in query.order_by(Sample.counter, Sample.value):
    print(sample.counter, sample.value, sample.rsum)
# counter为20的有两个，计算累加时，分别计算
```

7.3 Window.GROUPS

```python
query = (Sample
         .select(Sample.counter, Sample.value,
                 fn.SUM(Sample.value).over(
                    order_by=[Sample.counter, Sample.value],
                    frame_type=Window.GROUPS,
                    start=Window.preceding(1)).alias('gsum'))
         .order_by(Sample.counter, Sample.value))
for sample in query:
    print(sample.counter, sample.value, sample.gsum)
# 如果如下：
# 1     10.0    10.0
# 1     20.0    30.0
# 1     20.0    40.0
# 2     1.0     21.0
# 2     1.0     2.0
# 2     3.0     4.0
# 3     100.0   103.0
# Window.GROUPS，则以Sample.counter, Sample.value分组，相同的分为一组，
# 组合值为组内行值之和，一组为单位，求当前组和前一组相加的和
```

使用规则：
  1.如果指定了frame_type的类型，则就使用frame_type
  2.如果start and/or end 边界被定义， Peewee默认使用ROWS
  3.如果没有定义start and/or end，则使用默认的RANGE



### 返回的数据格式

有时不需要创建模型实例的开销，只需要遍历行数据，不需要model提供的所有api，可调整返回格式
  dicts()、namedtuples()、tuples()、objects()

1.tuples()

每行记录为一个元组格式

```python
stats = (Sample
         .select(Sample.counter, fn.Count(Sample.value))
         .group_by(Sample.counter)
         .tuples())
# iterate over a list of 2-tuples containing the url and count
for counter, value in stats:
    print(counter, value)
```

2.dicts()

每行记录为一个字典格式

```python
stats = (Sample
         .select(Sample.counter, fn.Count(Sample.value).alias("vc"))
         .group_by(Sample.counter)
         .dicts())
# iterate over a list of 2-tuples containing the url and count
for stat in stats:
    print(stat["counter"], stat["vc"])
```



### 返回子句

在执行UPDATE，INSERT和DELETE查询时，会返回不同的值

- INSERT：自动递增新插入行的主键值。如果不使用自动递增的主键，Postgres将返回新行的主键，但SQLite和MySQL将不返回
- UPDATE：修改的行数
- DELETE：删除的行数

当使用返回子句时，就会返回一个可迭代的游标对象。

1.UPDATE

修改不激活的用户为激活状态，并发送邮件，使用返回子句，就不用update之后再去查询有哪些用户了

```python
query = (User
         .update(is_active=False)
         .where(User.registration_expired == True)
         .returning(User))
def send_deactivation_email(email):
    pass
# Send an email to every user that was deactivated.
for deactivated_user in query.execute():
    send_deactivation_email(deactivated_user.email)
```

2.INSERT

创建一个新用户之后，要打印日志，可以使用返回子句，避免再查询

```python
query = (User
         .insert(email='foo@bar.com', created=fn.now())
         .returning(User))  # Shorthand for all columns on User.
# When using RETURNING, execute() returns a cursor.
cursor = query.execute()
# Get the user object we just inserted and log the data:
user = cursor[0]
logger.info('Created user %s (id=%s) at %s', user.email, user.id, user.created)
```

3.返回不同的行类型

```python
# 默认返回一个model实例，如下，可以返回字典类型的行
data = [{'name': 'charlie'}, {'name': 'huey'}, {'name': 'mickey'}]
query = (User
         .insert_many(data)
         .returning(User.id, User.username)
         .dicts())
for new_user in query.execute():
    print('Added user "%s", id=%s' % (new_user['username'], new_user['id']))
```





# 第六章 查询操作符

Peewee支持一下操作符

| Comparison | Meaning                                 |
| ---------- | --------------------------------------- |
| `==`       | x equals y                              |
| `<`        | x is less than y                        |
| `<=`       | x is less than or equal to y            |
| `>`        | x is greater than y                     |
| `>=`       | x is greater than or equal to y         |
| `!=`       | x is not equal to y                     |
| `<<`       | x IN y, where y is a list or query      |
| `>>`       | x IS y, where y is None/NULL            |
| `%`        | x LIKE y where y may contain wildcards  |
| `**`       | x ILIKE y where y may contain wildcards |
| `^`        | x XOR y                                 |
| `~`        | Unary negation (e.g., NOT x)            |

其他可用查询运算方法

| Method                | Meaning                                         |
| --------------------- | ----------------------------------------------- |
| `.in_(value)`         | IN lookup (identical to `<<`).                  |
| `.not_in(value)`      | NOT IN lookup.                                  |
| `.is_null(is_null)`   | IS NULL or IS NOT NULL. Accepts boolean param.  |
| `.contains(substr)`   | Wild-card search for substring.                 |
| `.startswith(prefix)` | Search for values beginning with `prefix`.      |
| `.endswith(suffix)`   | Search for values ending with `suffix`.         |
| `.between(low, high)` | Search for values between `low` and `high`.     |
| `.regexp(exp)`        | Regular expression match (case-sensitive).      |
| `.iregexp(exp)`       | Regular expression match (case-insensitive).    |
| `.bin_and(value)`     | Binary AND.                                     |
| `.bin_or(value)`      | Binary OR.                                      |
| `.concat(other)`      | Concatenate two strings or objects using `||`.  |
| `.distinct()`         | Mark column for DISTINCT selection.             |
| `.collate(collation)` | Specify column with the given collation.        |
| `.cast(type)`         | Cast the value of the column to the given type. |

逻辑运算符

| Operator   | Meaning              | Example                                              |
| ---------- | -------------------- | ---------------------------------------------------- |
| `&`        | AND                  | `(User.is_active == True) & (User.is_admin == True)` |
| `|` (pipe) | OR                   | `(User.is_admin) | (User.is_superuser)`              |
| `~`        | NOT (unary negation) | `~(User.username.contains('admin'))`                 |

下面是使用同的一些例子

```python
# 1.基本操作运算符示例
user = User.select().where(User.username == 'Charlie')
for u in user:
    print(u.username)

user = User.select().where(User.username.in_(['charlie', 'huey', 'mickey']))
for u in user:
    print(u.username)

sample = Sample.select().where(Sample.value.between(10, 100))
for s in sample:
    print(s.value)

user = User.select().where(User.username.startswith('C'))
for u in user:
    print(u.username)

user = User.select().where(User.username.contains('ar'))
for u in user:
    print(u.username)


# 2.逻辑运算符示例
user = User2.select().where(
  (User2.username == "huey") &
  (User2.login_count > 0))
for u in user:
    print(u.username)

user = User2.select().where(
  (User2.username == "huey") |
  (User2.login_count > 0))
for u in user:
    print(u.username)

active_user = User2.select().where(User2.login_count > 0)
non_active_user = User2.select().where(User2.id.not_in(active_user))
for u in non_active_user:
    print(u.username)
```



## 三值逻辑

1. IS NULL和IN

```python
# Get all User objects whose last login is NULL.
User.select().where(User.last_login >> None)
# Get users whose username is in the given list.
usernames = ['charlie', 'huey', 'mickey']
User.select().where(User.username << usernames)

# 如果不使用重载运算符，也可以使用字段方法
User.select().where(User.last_login.is_null(True))
User.select().where(User.username.in_(usernames))
```

2. IS NOT NULL 和 NOT IN

```python
# Get all User objects whose last login is *NOT* NULL.
User.select().where(User.last_login.is_null(False))
# Using unary negation instead.
User.select().where(~(User.last_login >> None))
# Get users whose username is *NOT* in the given list.
User.select().where(User.username.not_in(usernames))
# Using unary negation instead.
User.select().where(~(User.username << usernames))
```



## 表达式

有两种类型的对象可以创建表达式：

```
1.Field instances
2.SQL聚合和函数使用 fn
```

```python
class User(Model):
    username = CharField()
    is_admin = BooleanField()
    is_active = BooleanField()
    last_login = DateTimeField()
    login_count = IntegerField()
    failed_logins = IntegerField()
```

1.基本使用

```python
# username is equal to 'charlie'
User.username == 'charlie'
# user has logged in less than 5 times
User.login_count < 5
```

2.与and和or使用

比较可以嵌套到任意深度：

```python
# User is both and admin and has logged in today
(User.is_admin == True) & (User.last_login >= today)
# User's username is either charlie or charles
(User.username == 'charlie') | (User.username == 'charles')
```

 3.与函数fn和其他算数表达式使用

```python
# user's username starts with a 'g' or a 'G':
fn.Lower(fn.Substr(User.username, 1, 1)) == 'g'
(User.failed_logins > (User.login_count * .5)) & (User.login_count > 10)
User.update(login_count=User.login_count + 1).where(User.id == user_id)
```

4.行值 Tuple()

类似python的元组，通常用来再一个表达式中比较自已子查询的多个列的值

```python
class EventLog(Model):
    event_type = TextField()
    source = TextField()
    data = TextField()
    timestamp = TimestampField()

class IncidentLog(Model):
    incident_type = TextField()
    source = TextField()
    traceback = TextField()
    timestamp = TimestampField()

# Get a list of all the incident types and sources that have occured today.
incidents = (IncidentLog
             .select(IncidentLog.incident_type, IncidentLog.source)
             .where(IncidentLog.timestamp >= datetime.date.today()))

# Find all events that correlate with the type and source of the
# incidents that occured today.
events = (EventLog
          .select()
          .where(Tuple(EventLog.event_type, EventLog.source).in_(incidents))
          .order_by(EventLog.timestamp))
# 实现这个功能的另一个方法是子查询
```



## SQL函数

sql里的函数，可以使用fn()帮手实现，如COUNT() or SUM()

```python
query = (User
         .select(User, fn.COUNT(Tweet.id).alias('tweet_count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User)
         .order_by(fn.COUNT(Tweet.id).desc()))
for user in query:
    print('%s -- %s tweets' % (user.username, user.tweet_count))
```

嵌套使用

```python
# Select the user's id, username and the first letter of their username, lower-cased
first_letter = fn.LOWER(fn.SUBSTR(User.username, 1, 1))
query = User.select(User, first_letter.alias('first_letter'))
# Alternatively we could select only users whose username begins with 'a'
a_users = User.select().where(first_letter == 'a')
for user in a_users:
   print(user.username)
```



## 原生sql语句

```python
query = (User
         .select(User, fn.Count(Tweet.id).alias('ct'))
         .join(Tweet)
         .group_by(User))

# Now we will order by the count, which was aliased to "ct"
query = query.order_by(SQL('ct'))
# You could, of course, also write this as:
query = query.order_by(fn.COUNT(Tweet.id))
```

有两种方式去使用手工sql
1. Database.execute_sql()，执行任意类型的语句
2. RawQuery， 执行SELECT语句并返回model instances.



## sql注入

peewee默认会把查询参数化，不要把不信任的数据直接放入sql里，而应该作为参数

```python
user_data = "somedata"
# Bad! DO NOT DO THIS!
query = MyModel.raw('SELECT * FROM my_table WHERE data = %s' % (user_data,))

# Good. `user_data` will be treated as a parameter to the query.
query = MyModel.raw('SELECT * FROM my_table WHERE data = %s', user_data)

# Bad! DO NOT DO THIS!
query = MyModel.select().where(SQL('Some SQL expression %s' % user_data))

# Good. `user_data` will be treated as a parameter.
query = MyModel.select().where(SQL('Some SQL expression %s', user_data))
```





# 第七章 关系和连接

首先定义本章的模型和数据

```python
import datetime
from peewee import *


db = MySQLDatabase(host='127.0.0.1', port=3306, user='root', passwd='root', database="peewee_join")

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = TextField()

class Tweet(BaseModel):
    content = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User, backref='tweets')

class Favorite(BaseModel):
    user = ForeignKeyField(User, backref='favorites')
    tweet = ForeignKeyField(Tweet, backref='favorites')


def populate_test_data():
    db.create_tables([User, Tweet, Favorite])

    data = (
        ('huey', ('meow', 'hiss', 'purr')),
        ('mickey', ('woof', 'whine')),
        ('zaizee', ()))
    for username, tweets in data:
        user = User.create(username=username)
        for tweet in tweets:
            Tweet.create(user=user, content=tweet)

    # Populate a few favorites for our users, such that:
    favorite_data = (
        ('huey', ['whine']),
        ('mickey', ['purr']),
        ('zaizee', ['meow', 'purr']))
    for username, favorites in favorite_data:
        user = User.get(User.username == username)
        for content in favorites:
            tweet = Tweet.get(Tweet.content == content)
            Favorite.create(user=user, tweet=tweet)

# 注意点
#1.使用如下方法可以把执行查询语句都打印出来
# import logging
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

#2.SQLite默认不使用外键，如下方法开启外键
# db = SqliteDatabase('my_app.db', pragmas={'foreign_keys': 1})

if __name__ == "__main__":
    populate_test_data()
```



## 简单连表

查询tweet里，名字为huey的user的发布的内容

```python
query = Tweet.select().join(User).where(User.username == 'huey')
for tweet in query:
    print(tweet.content)
```

我们不用显式的指定on，因为peewee从模型中推断，当我们从tweet加入到用户时，我们正在加入 Tweet.user 外键。

以下查询是等价的

```
query = (Tweet
         .select()
         .join(User, on=(Tweet.user == User.id))
         .where(User.username == 'huey'))
```

查询名字为huey的user对象的所关联的所有tweet的内容

```python
huey = User.get(User.username == 'huey')
for tweet in huey.tweets:
    print(tweet.content)

# 仔细看看 huey.tweets 我们可以看到它只是一个简单的预过滤 SELECT 查询：
print(huey.tweets)
print(huey.tweets.sql())
```



## 连接多表

peewee有个连接上下文（join contexts）的概念，就是每当我们调用 join() 方法，我们将隐式地联接先前联接的模型（或者，如果这是第一个调用，则是select的模型）。

1.连接两个表

如下查询：查询每个用户发布的受关注的推特的数量，包含哪些美发部推特和推特没收关注的用户，将连两次表，先从user到tweet，再到favorite，sql如下：

```sql
SELECT user.username, COUNT(favorite.id)
FROM user
LEFT OUTER JOIN tweet ON tweet.user_id = user.id
LEFT OUTER JOIN favorite ON favorite.tweet_id = tweet.id
GROUP BY user.username
```

查询如下

```python
query = (User
         .select(User.username, fn.COUNT(Favorite.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)  # Joins user -> tweet.
         .join(Favorite, JOIN.LEFT_OUTER)  # Joins tweet -> favorite.
         .group_by(User.username))
for user in query:
     print(user.username, user.count)
```

2，连接多个表，切换连接上下文

查询Huey的tweets和它们favorited的次数

```sql
SELECT tweet.content, COUNT(favorite.id)
FROM tweet
INNER JOIN user ON tweet.user_id = user.id
LEFT OUTER JOIN favorite ON favorite.tweet_id = tweet.id
WHERE user.username = 'huey'
GROUP BY tweet.content;
```

```python
query = (Tweet
         .select(Tweet.content, fn.COUNT(Favorite.id).alias('count'))
         .join(User)  # Join from tweet -> user.
         .switch(Tweet)  # Move "join context" back to tweet.
         .join(Favorite, JOIN.LEFT_OUTER)  # Join from tweet -> favorite.
         .where(User.username == 'huey')
         .group_by(Tweet.content))
# 使用switch的作用就是switch后面的join，不会和User连接，而是和继续Tweet连接
```

也可使用join_from()，效果与上面相同

```python
query = (Tweet
         .select(Tweet.content, fn.COUNT(Favorite.id).alias('count'))
         .join_from(Tweet, User)  # Join tweet -> user.
         .join_from(Tweet, Favorite, JOIN.LEFT_OUTER)  # Join tweet -> favorite.
         .where(User.username == 'huey')
         .group_by(Tweet.content))

for tweet in query:
     print('%s favorited %d times' % (tweet.content, tweet.count))
```



## 多表查询

 select字段来源多个表

如查询所有tweet以及作者的用户名

```python
for tweet in Tweet.select():
    print(tweet.user.username, '->', tweet.content)
```

上面的循环存在一个大问题：它对每个tweet执行一个额外的查询来查找 tweet.user 外键。对于我们的小表，性能损失并不明显，但是我们会发现延迟随着行数的增加而增加。

避免此问题，可使用如下方法：

 1.连表查询

```python
for row in Tweet.select(Tweet.content, User.username).join(User).dicts():
    print(row)
```

2.返回joined的模型实例的数据

如果不使用.dicts()方法，结果将返回Tweet对象，那么username的值是分配给tweet.user.username而不是tweet.username。

```python
for tweet in Tweet.select(Tweet.content, User.username).join(User):
     print(tweet.user.username, '->', tweet.content)
```

3.attr参数

如果希望控制把连接的User实例放到哪里，可以在join方法中使用attr参数

```python
query = Tweet.select(Tweet.content, User.username).join(User, attr='author')
for tweet in query:
    print(tweet.author.username, '->', tweet.content)
```

4.objects()

把查询的所有的结果都放到Tweet实例属性里

```python
for tweet in query.objects():
     print(tweet.username, '->', tweet.content)
```



## 子查询

Peewee允许连接任何类似于表的对象，包括子查询或公共表表达式（CTE）

查询所有用户和他们最新的推特

sql如下

```sql
SELECT tweet.*, user.*
FROM tweet
INNER JOIN (
    SELECT latest.user_id, MAX(latest.timestamp) AS max_ts
    FROM tweet AS latest
    GROUP BY latest.user_id) AS latest_query
ON ((tweet.user_id = latest_query.user_id) AND (tweet.timestamp = latest_query.max_ts))
INNER JOIN user ON (tweet.user_id = user.id)
```

peewee如下

因为需要在外层直接从Tweet查询数据，所以我们需要给Tweet取个别名

```python
Latest = Tweet.alias()
latest_query = (Latest
                .select(Latest.user, fn.MAX(Latest.timestamp).alias('max_ts'))
                .group_by(Latest.user)
                .alias('latest_query'))
predicate = ((Tweet.user == latest_query.c.user_id) &
             (Tweet.timestamp == latest_query.c.max_ts))
query = (Tweet
         .select(Tweet, User)  # Select all columns from tweet and user.
         .join(latest_query, on=predicate)  # Join tweet -> subquery.
         .join_from(Tweet, User))  # Join from tweet -> user.
#  .join_from(Tweet, User) ，相当于 .switch(Tweet).join(User)
#  latest_query.c.max_ts 中的 .c 用于动态创建列引用
for tweet in query:
     print(tweet.user.username, '->', tweet.content)
```



2.使用Common-table Expressions

```sql
WITH latest AS (
    SELECT user_id, MAX(timestamp) AS max_ts
    FROM tweet
    GROUP BY user_id)
SELECT tweet.*, user.*
FROM tweet
INNER JOIN latest
    ON ((latest.user_id = tweet.user_id) AND (latest.max_ts = tweet.timestamp))
INNER JOIN user
    ON (tweet.user_id = user.id)
```

```python
Latest = Tweet.alias()
cte = (Latest
       .select(Latest.user, fn.MAX(Latest.timestamp).alias('max_ts'))
       .group_by(Latest.user)
       .cte('latest'))
# Our join predicate will ensure that we match tweets based on their
# timestamp *and* user_id.
predicate = ((Tweet.user == cte.c.user_id) &
             (Tweet.timestamp == cte.c.max_ts))
# We put it all together, querying from tweet and joining on the CTE
# using the above predicate.
query = (Tweet
         .select(Tweet, User)  # Select all columns from tweet and user.
         .join(cte, on=predicate)  # Join tweet -> CTE.
         .join_from(Tweet, User)  # Join from tweet -> user.
         .with_cte(cte))
for tweet in query:
     print(tweet.user.username, '->', tweet.content)
```



## 多外键

当同一模型有多个外键时，最好显式指定要join的字段

```python
class Relationship(BaseModel):
    from_user = ForeignKeyField(User, backref='relationships')
    to_user = ForeignKeyField(User, backref='related_to')

    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('from_user', 'to_user'), True),
        )
```

查询我关注了哪些用户

```python
charlie = User.select().where(User.username == "charlie")
(User
 .select()
 .join(Relationship, on=Relationship.to_user)
 .where(Relationship.from_user == charlie))
```

查询谁关注了我

```python
(User
 .select()
 .join(Relationship, on=Relationship.from_user)
 .where(Relationship.to_user == charlie))
```



## 联接任意字段

如果两个表之间不存在外键，则仍可以执行联接，但必须手动指定联接谓词

```python
class ActivityLog(BaseModel):
    object_id = IntegerField()
    activity_type = CharField()

user_log = (User
            .select(User, ActivityLog)
            .join(ActivityLog, on=(User.id == ActivityLog.object_id), attr='log')
            .where(
                (ActivityLog.activity_type == 'user_activity') &
                (User.username == 'charlie')))

for user in user_log:
    print(user.username, user.log.description)

#### Print something like ####
# charlie logged in
# charlie posted a tweet
# charlie retweeted
# charlie posted a tweet
# charlie logged out
```

注意：join里参数attr的使用，把join的模型ActivityLog分配给了joined对象的属性，可以直接访问连接的模型ActivityLog，而不用产生额外的查询



## 自连接

```python
class Category(Model):
    name = CharField()
    parent = ForeignKeyField('self', backref='children')
```

1.使用模型别名

```python
Parent = Category.alias()
query = (Category
         .select()
         .join(Parent, on=(Category.parent == Parent.id))
         .where(Parent.name == 'Electronics'))
```

2.使用子查询

```python
Parent = Category.alias()
join_query = Parent.select().where(Parent.name == 'Electronics')

# Subqueries used as JOINs need to have an alias.
join_query = join_query.alias('jq')

query = (Category
         .select()
         .join(join_query, on=(Category.parent == join_query.c.id)))
```



## 多对多

Peewee提供了一个表示多对多关系的字段，就像Django一样。这个特性是由于用户的许多请求而添加的，但强

烈建议不要使用它，因为它将字段的概念与连接表和隐藏连接混为一谈。

1.新建一个关联关系表实现多对多

```python
class Student(Model):
    name = CharField()

class Course(Model):
    name = CharField()

class StudentCourse(Model):
    student = ForeignKeyField(Student)
    course = ForeignKeyField(Course)

# 假设我们要查找进入数学班的学生：
query = (Student
         .select()
         .join(StudentCourse)
         .join(Course)
         .where(Course.name == 'math'))
for student in query:
    print(student.name)
# 查询给定学生注册的课程：
courses = (Course
           .select()
           .join(StudentCourse)
           .join(Student)
           .where(Student.name == 'da vinci'))
for course in courses:
    print(course.name)
# 列出所有学生及其各自的课程
query = (StudentCourse
         .select(StudentCourse, Student, Course)
         .join(Course)
         .switch(StudentCourse)
         .join(Student)
         .order_by(Student.name))
for student_course in query:
    print(student_course.student.name, '->', student_course.course.name)
```

2.使用ManyToManyField

如果模型非常简单，并且查询需求也不是很复杂， 可以使用ManyToManyField。

```python
class Student(BaseModel):
    name = CharField()

class Course(BaseModel):
    name = CharField()
    students = ManyToManyField(Student, backref='courses')

StudentCourse = Course.students.get_through_model()

db.create_tables([
    Student,
    Course,
    StudentCourse])

# Get all classes that "huey" is enrolled in:
huey = Student.get(Student.name == 'Huey')
for course in huey.courses.order_by(Course.name):
    print(course.name)

# Get all students in "English 101":
engl_101 = Course.get(Course.name == 'English 101')
for student in engl_101.students:
    print(student.name)

# When adding objects to a many-to-many relationship, we can pass
# in either a single model instance, a list of models, or even a
# query of models:
huey.courses.add(Course.select().where(Course.name.contains('English')))

engl_101.students.add(Student.get(Student.name == 'Mickey'))
engl_101.students.add([
    Student.get(Student.name == 'Charlie'),
    Student.get(Student.name == 'Zaizee')])

# The same rules apply for removing items from a many-to-many:
huey.courses.remove(Course.select().where(Course.name.startswith('CS')))

engl_101.students.remove(huey)

# Calling .clear() will remove all associated objects:
cs_150.students.clear()

# 不建议使用ManyToManyField
```



## N + 1 问题

指执行查询的时候，对于结果集的每一行，都至少执行了一个其他查询（将其概念化的另一种方法是作为嵌套循

环）在大多数情况下可以使用join或子查询避免。数据库本身可能或做一个嵌套循环，但是相比于在程序代码里做

n次查询循环性能更好，因为查询可能会涉及与数据库连接的网略延迟，且当join或子查询时，可能没有用到数据

库提供的索引。

1.使用join

查询最近的10条tweet的content和它们的作者username，n + 1 的场景是

  1.获取最近的10条tweet

  2.对于每条tweet，查询它们的作者

如果使用join，如下：

```python
query = (Tweet
         .select(Tweet, User)  # Note that we are selecting both models.
         .join(User)  # Use an INNER join because every tweet has an author.
         .order_by(Tweet.id.desc())  # Get the most recent tweets.
         .limit(10))
for tweet in query:
    print(tweet.user.username, '-', tweet.message)
```

如果没有join，需要查询tweet.user.username的时候，触发查询外键tweet.user 并检索关联的user。

 2.prefetch()

查询几个用户和他们所有的推特，N + 1场景如下：

​	1.获取几个user

​	2.对于每个user，获取他们的tweet

这个场景和上个类似，但是又不太一样，当我们获取tweet时，可以关联到一个用户，所以可以直接使用外键。但

是反过来，一个user可能又多个tweet，peewee提供了一种方法避免 O(n)查询：获取user，然后获取和这些user

关联的所有tweet，一旦获取足够大的tweet列表，就会把它们分配出去这种方法通常比较快，但是会分别查询两

张表。使用prefetch，会只用子查询提前加载user相关的tweet，这就使原来的n行n次查询变为k表k次查询。

```python
week_ago = datetime.date.today() - datetime.timedelta(days=7)
users = User.select()
tweets = (Tweet
          .select()
          .where(Tweet.timestamp >= week_ago))

# This will perform two queries.
users_with_tweets = prefetch(users, tweets)

for user in users_with_tweets:
    print(user.username)
    for tweet in user.tweets:
        print('  ', tweet.message)
```

prefetch可以用在查询任意数量的表





# 第八章 扩展内容

## 模型迁移

使用` playhouse.migrate` 进行模型迁移操作

### 示例用法

```python
from playhouse.migrate import *

# Postgres example:
my_db = PostgresqlDatabase(...)
migrator = PostgresqlMigrator(my_db)

# SQLite example:
my_db = SqliteDatabase('my_database.db')
migrator = SqliteMigrator(my_db)

```

使用 migrate() 要执行一个或多个操作：

```python
title_field = CharField(default='')
status_field = IntegerField(null=True)

migrate(
    migrator.add_column('some_table', 'title', title_field),
    migrator.add_column('some_table', 'status', status_field),
    migrator.drop_column('some_table', 'old_column'),
)
```

 迁移不在事务内部运行。如果希望在事务中运行迁移，则需要将调用包装到 migrate 在一个 [`atomic()`](https://www.osgeo.cn/peewee/peewee/api.html#Database.atomic) 上下文管理器，例如

``` python
with my_db.atomic():
    migrate(...)
```



### 支持的操作

将新字段添加到现有模型：

```python
# Create your field instances. For non-null fields you must specify a
# default value.
pubdate_field = DateTimeField(null=True)
comment_field = TextField(default='')

# Run the migration, specifying the database table, field name and field.
migrate(
    migrator.add_column('comment_tbl', 'pub_date', pubdate_field),
    migrator.add_column('comment_tbl', 'comment', comment_field),
)
```

重命名字段：

```python
# Specify the table, original name of the column, and its new name.
migrate(
    migrator.rename_column('story', 'pub_date', 'publish_date'),
    migrator.rename_column('story', 'mod_date', 'modified_date'),
)
```

删除字段：

```python
migrate(
    migrator.drop_column('story', 'some_old_field'),
)
```

使字段可以为空或不可以为空：

```python
# Note that when making a field not null that field must not have any
# NULL values present.
migrate(
    # Make `pub_date` allow NULL values.
    migrator.drop_not_null('story', 'pub_date'),

    # Prevent `modified_date` from containing NULL values.
    migrator.add_not_null('story', 'modified_date'),
)
```

更改字段的数据类型：

```python
# Change a VARCHAR(50) field to a TEXT field.
migrate(
    migrator.alter_column_type('person', 'email', TextField())
)
```

重命名表：

```python
migrate(
    migrator.rename_table('story', 'stories_tbl'),
)
```

添加索引：

```python
# Specify the table, column names, and whether the index should be
# UNIQUE or not.
migrate(
    # Create an index on the `pub_date` column.
    migrator.add_index('story', ('pub_date',), False),

    # Create a multi-column index on the `pub_date` and `status` fields.
    migrator.add_index('story', ('pub_date', 'status'), False),

    # Create a unique index on the category and title fields.
    migrator.add_index('story', ('category_id', 'title'), True),
)
```

删除索引：

```python
# Specify the index name.
migrate(migrator.drop_index('story', 'story_pub_date_status'))
```

添加或删除表约束：

```python
# Add a CHECK() constraint to enforce the price cannot be negative.
migrate(migrator.add_constraint(
    'products',
    'price_check',
    Check('price >= 0')))

# Remove the price check constraint.
migrate(migrator.drop_constraint('products', 'price_check'))

# Add a UNIQUE constraint on the first and last names.
migrate(migrator.add_unique('person', 'first_name', 'last_name'))
```



## 自省

反射模块包含用于自省现有数据库的帮助程序。该模块由`playhouse`的其他几个模块内部使用，包括 `DataSet`and `pwiz`, a model generator.

1.`generate_models`(*database*[, *schema=None*[, ***options*]])

参数

- **database** ([*Database*](https://www.osgeo.cn/peewee/peewee/api.html#Database)) -- 要自省的数据库实例。
- **schema** (*str*) -- 自省的可选模式。
- **options** -- 任意选项，请参见 [`Introspector.generate_models()`](https://www.osgeo.cn/peewee/peewee/playhouse.html#Introspector.generate_models) 有关详细信息。

返回

- 一 `dict` 将表名映射到模型类。

为给定数据库中的表生成模型。有关如何使用此函数的示例，请参见 交互使用peewee .

例子：

```python
>>> from peewee import *
>>> from playhouse.reflection import generate_models
>>> db = PostgresqlDatabase('my_app')
>>> models = generate_models(db)
>>> list(models.keys())
['account', 'customer', 'order', 'orderitem', 'product']

>>> globals().update(models)  # Inject models into namespace.
>>> for cust in customer.select():  # Query using generated model.
...     print(cust.name)
...

Huey Kitty
Mickey Dog
```



2.`print_model`(*model*)

参数

- **model** ([*Model*](https://www.osgeo.cn/peewee/peewee/api.html#Model)) -- 要打印的模型类

返回

- 无返回值

打印模型类的用户友好描述，用于调试或交互使用。当前，这将打印表名以及所有字段及其数据类型。这个 [交互使用peewee](https://www.osgeo.cn/peewee/peewee/interactive.html#interactive) 部分包含一个示例。

实例输出：

```python
>>> from playhouse.reflection import print_model
>>> print_model(User)
user
  id AUTO PK
  email TEXT
  name TEXT
  dob DATE

index(es)
  email UNIQUE

>>> print_model(Tweet)
tweet
  id AUTO PK
  user INT FK: User.id
  title TEXT
  content TEXT
  timestamp DATETIME
  is_published BOOL

index(es)
  user_id
  is_published, timestamp
```



3. `print_table_sql`(*model*)

参数

- **model** ([*Model*](https://www.osgeo.cn/peewee/peewee/api.html#Model)) -- 打印模型

返回

- 无返回值

打印对于给定的模型类的SQL `CREATE TABLE` ，这对于调试或交互使用可能很有用。见 [交互使用peewee](https://www.osgeo.cn/peewee/peewee/interactive.html#interactive) 例如用法部分。注意，这个函数的输出中不包括索引和约束。

```python
>>> from playhouse.reflection import print_table_sql
>>> print_table_sql(User)
CREATE TABLE IF NOT EXISTS "user" (
  "id" INTEGER NOT NULL PRIMARY KEY,
  "email" TEXT NOT NULL,
  "name" TEXT NOT NULL,
  "dob" DATE NOT NULL
)

>>> print_table_sql(Tweet)
CREATE TABLE IF NOT EXISTS "tweet" (
  "id" INTEGER NOT NULL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "title" TEXT NOT NULL,
  "content" TEXT NOT NULL,
  "timestamp" DATETIME NOT NULL,
  "is_published" INTEGER NOT NULL,
  FOREIGN KEY ("user_id") REFERENCES "user" ("id")
)
```



4. *class*`Introspector`**(***metadata***[****,** *schema=None***]****)

metadata可以通过实例化 Introspector 中得到.。与其直接实例化此类 ，更推荐使用工厂方法from_database() .

4.1 *classmethod* `from_database`(*database*[, *schema=None*])

参数

- **database** -- 一 [`Database`](https://www.osgeo.cn/peewee/peewee/api.html#Database) 实例。
- **schema** (*str*) -- 可选模式（某些数据库支持）。

创建一个 [`Introspector`](https://www.osgeo.cn/peewee/peewee/playhouse.html#Introspector) 适用于给定数据库的实例。

```python
db = SqliteDatabase('my_app.db')
introspector = Introspector.from_database(db)
models = introspector.generate_models()

# User and Tweet (assumed to exist in the database) are
# peewee Model classes generated from the database schema.
User = models['user']
Tweet = models['tweet']
```

4.2 `generate_models`([*skip_invalid=False*[, *table_names=None*[, *literal_column_names=False*[, *bare_fields=False*[, *include_views=False*]]]]])

参数

- **skip_invalid** (*bool*) -- 跳过名称为无效python标识符的表。
- **table_names** (*list*) -- 要生成的表名列表。如果未指定，则为所有表生成模型。
- **literal_column_names** (*bool*) -- 按原样使用列名。默认情况下，列名称是“python-ized”，即混合大小写变为小写。
- **bare_fields** -- 仅SQLite. 不要为自省的列指定数据类型。
- **include_views** -- 也为视图生成模型。

返回

- 将表名映射到模型类的字典。

内省数据库，读取表、列和外键约束，然后生成一个字典，将每个数据库表映射到动态生成的 [`Model`](https://www.osgeo.cn/peewee/peewee/api.html#Model) 类。



## 连接池

这个 pool 模块包含多个 Database 为PostgreSQL、MySQL和SQLite数据库提供连接池的类。池通过重写 Database 类打开和关闭与后端的连接。池可以指定一个超时，在该超时之后将回收连接，以及打开连接数的上限。

在多线程应用程序中，最多 max_connections 将被打开。每个线程（或者，如果使用gevent，greenlet）将有自己的连接。

在单线程应用程序中，只创建一个连接。它将被持续回收，直到超过过时超时或显式关闭（使用.manual_close()）

默认情况下，您的应用程序所需要做的就是确保连接在使用完后关闭，并将它们返回到池中。对于Web应用程序，这通常意味着在请求开始时，您将打开一个连接，当您返回响应时，您将关闭该连接。

简单Postgres池示例代码：

```python
# Use the special postgresql extensions.
from playhouse.pool import PooledPostgresqlExtDatabase

db = PooledPostgresqlExtDatabase(
    'my_app',
    max_connections=32,
    stale_timeout=300,  # 5 minutes.
    user='postgres')

class BaseModel(Model):
    class Meta:
        database = db
```

就这样！如果希望对连接池进行更细粒度的控制，请参阅[Connection Management](http://docs.peewee-orm.com/en/latest/peewee/database.html#connection-management) 部分。



### Pool APIs

*class* `PooledDatabase`(*database*[, *max_connections=20*[, *stale_timeout=None*[, *timeout=None*[, ***kwargs*]]]])

参数

- **database** (*str*) -- 数据库或数据库文件的名称。
- **max_connections** (*int*) -- 最大连接数。 `None` 不限制。
- **stale_timeout** (*int*) -- 允许使用连接的秒数。
- **timeout** (*int*) -- 池满时要阻止的秒数。默认情况下，当池满时，peewee不会阻塞，但只会抛出一个异常。要无限期阻止，请将此值设置为 `0` .
- **kwargs** -- 传递给数据库类的任意关键字参数。

Mixin类用于子类 [`Database`](https://www.osgeo.cn/peewee/peewee/api.html#Database) .

注意：当超过 stale_timeout，连接并不会精确地关闭，旧连接只有当新的连接请求来才会关闭。

如果打开的连接数超过 max_connections, 会抛出ValueError。

方法有：

1. `manual_close`()

关闭当前打开的连接而不将其返回池。

2. `close_idle`()

关闭所有空闲连接。这不包括当前正在使用的任何连接——只包括以前创建但后来返回池的连接

3. `lose_stale`([*age=600*])

参数

- **age** (*int*) -- 连接过时时间。

返回

- 关闭的连接数。

会关闭使用中但超过给定age连接。**调用此方法时请小心！**

4. `close_all`()

   关闭所有连接。这包括当时可能使用的任何连接。**调用此方法时请小心！**



常见数据库连接池对象：

1. *class*`PooledPostgresqlDatabase`

混合在[`PooledDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledDatabase)中的 [`PostgresqlDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#PostgresqlDatabase) 的子类。

2. *class*`PooledPostgresqlExtDatabase`

混合在[`PooledDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledDatabase)中的f [`PostgresqlExtDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PostgresqlExtDatabase)  的子类。

3. *class*`PooledMySQLDatabase`

混合在[` PooledDatabase`](http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#PooledDatabase)中的 [`MySQLDatabase`](http://docs.peewee-orm.com/en/latest/peewee/api.html#MySQLDatabase)的子类。

4. *class*`PooledSqliteDatabase`

5. *class*`PooledSqliteExtDatabase`

