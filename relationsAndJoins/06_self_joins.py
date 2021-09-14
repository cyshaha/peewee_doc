from peewee import *


# 自连接

class Category(Model):
    name = CharField()
    parent = ForeignKeyField('self', backref='children')

# 1.使用模型别名
Parent = Category.alias()
query = (Category
         .select()
         .join(Parent, on=(Category.parent == Parent.id))
         .where(Parent.name == 'Electronics'))


# 2.使用子查询
Parent = Category.alias()
join_query = Parent.select().where(Parent.name == 'Electronics')

# Subqueries used as JOINs need to have an alias.
join_query = join_query.alias('jq')

query = (Category
         .select()
         .join(join_query, on=(Category.parent == join_query.c.id)))