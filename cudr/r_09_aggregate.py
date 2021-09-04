from models import User, Tweet
from peewee import *
# 聚合


# 1.group_by
query = (User
         .select(User, fn.Count(Tweet.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User))

for q in query:
    print(q.username, " -> ", q.count)


# 2.having
query = (User
         .select(User, fn.Count(Tweet.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User)
         .having(fn.Count(Tweet.id)>0))

for q in query:
    print(q.username, " -> ", q.count)