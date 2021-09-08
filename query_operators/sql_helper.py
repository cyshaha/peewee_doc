from models import User, Tweet
from peewee import *

# 使用原生sql语句

query = (User
         .select(User, fn.Count(Tweet.id).alias('ct'))
         .join(Tweet)
         .group_by(User))

# Now we will order by the count, which was aliased to "ct"
query = query.order_by(SQL('ct'))
# You could, of course, also write this as:
query = query.order_by(fn.COUNT(Tweet.id))

# 有两种方式去使用手工sql
# 1. Database.execute_sql()，执行任意类型的语句
# 2. RawQuery， 执行SELECT语句并返回model instances.
