# 模型选项和metadata
# 为了不污染模型的命名空间，模型特定的配置被放在 Meta类里

from peewee import *

contacts_db = SqliteDatabase('contacts.db')

class Person(Model):
    name = CharField()

    class Meta:
        database = contacts_db

# 一旦定义了类，就不应该访问 ModelClass.Meta ，而是使用 ModelClass._meta
print(Person._meta)  # <peewee.Metadata object at 0x0000028716A2BB00>

# 这个 ModelOptions 类实现了几种可能用于检索模型元数据的方法（例如字段列表、外键关系等）
print(Person._meta.fields)
print(Person._meta.primary_key)
print(Person._meta.database)


# 下面有一些作为meta属性选项，大部分都是可继承的
# Option	        Meaning	                                        Inheritable?
# database	        database for model	                            yes
# table_name	    name of the table to store data	                no
# table_function	function to generate table name dynamically	    yes
# indexes	        a list of fields to index	                    yes
# primary_key	    a CompositeKey instance	                        yes
# constraints	    a list of table constraints	                    yes
# schema	        the database schema for the model	            yes
# only_save_dirty	when calling model.save(), only save dirty fields	yes
# options	        dictionary of options for create table extensions	yes
# table_settings	list of setting strings to go after close parentheses	yes
# temporary	indicate temporary table	                            yes
# legacy_table_names	use legacy table name generation (enabled by default)	yes
# depends_on	    indicate this table depends on another for creation	no
# without_rowid	    indicate table should not have rowid (SQLite only)	no
# strict_tables	i   ndicate strict data-types (SQLite only, 3.37+)	    yes
# 下面是一个显示可继承属性与不可继承属性
db = SqliteDatabase(':memory:')
class ModelOne(Model):
    class Meta:
        database = db
        table_name = 'model_one_tbl'
class ModelTwo(ModelOne):
    pass
print( ModelOne._meta.database is ModelTwo._meta.database)  # True
print(ModelOne._meta.table_name == ModelTwo._meta.table_name)  # False


# Meta.primary_key
# 这个 Meta.primary_key 属性用于指定 CompositeKey 或者表示模无主键
# 若要指示模型不应具有主键，请设置 primary_key = False
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


# Table Names
# 默认情况下，peewee将根据模型类的名称自动生成表名。表名的生成方式取决于 Meta.legacy_table_names .
# 默认情况下， legacy_table_names=True 以避免破坏向后兼容性。
# 但是，如果希望使用新的和改进的表名生成，可以指定 legacy_table_names=False
# 注意：为了保持向后兼容性，当前版本（peewee 3.x）默认情况下legacy_table_names=True。在下一个主要版本（Peewee 4.0）中， legacy_table_names 将具有默认值 False .
# 要显式指定模型类的表名，请使用 table_name meta选项
class UserProfile(Model):
    class Meta:
        table_name = 'user_profile_tbl'
# 如果希望实现自己的命名约定，可以指定 table_function meta选项
# 此函数将与模型类一起调用，并应以字符串形式返回所需的表名。
# 假设我们公司指定表名的大小写应为小写，并以“_tbl”结尾，我们可以将其作为表函数来实现：
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