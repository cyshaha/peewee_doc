from models import User, Tweet
from peewee import *

# sql函数
# sql里的函数，可以使用fn()帮手实现
# 如COUNT() or SUM()


query = (User
         .select(User, fn.COUNT(Tweet.id).alias('tweet_count'))
         .join(Tweet, JOIN.LEFT_OUTER)
         .group_by(User)
         .order_by(fn.COUNT(Tweet.id).desc()))
for user in query:
    print('%s -- %s tweets' % (user.username, user.tweet_count))


# 2.嵌套使用
# Select the user's id, username and the first letter of their username, lower-cased
first_letter = fn.LOWER(fn.SUBSTR(User.username, 1, 1))
query = User.select(User, first_letter.alias('first_letter'))
# Alternatively we could select only users whose username begins with 'a'
a_users = User.select().where(first_letter == 'a')
for user in a_users:
   print(user.username)