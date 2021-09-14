from relationsAndJoins.model_and_data import BaseModel, User, db
from peewee import *

# 一个模型多个标签
# 当同一模型有多个外键时，最好显式指定要join的字段



class Relationship(BaseModel):
    from_user = ForeignKeyField(User, backref='relationships')
    to_user = ForeignKeyField(User, backref='related_to')

    class Meta:
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('from_user', 'to_user'), True),
        )
# db.create_tables([Relationship,])


# 1.查询我关注了哪些用户
charlie = User.select().where(User.username == "charlie")
(User
 .select()
 .join(Relationship, on=Relationship.to_user)
 .where(Relationship.from_user == charlie))

# 2.查询谁关注了我
(User
 .select()
 .join(Relationship, on=Relationship.from_user)
 .where(Relationship.to_user == charlie))