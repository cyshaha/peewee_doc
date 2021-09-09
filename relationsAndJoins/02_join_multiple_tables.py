from relationsAndJoins.model_and_data import Favorite, User, Tweet
from peewee import *

# 连接多个表
# peewee有个连接上下文（join contexts）的概念
# 就是每当我们调用 join() 方法，我们将隐式地联接先前联接的模型（或者，如果这是第一个调用，则是select的模型）

# 1.连接两个表
# 如下查询：查询每个用户发布的受关注的推特的数量，包含哪些美发部推特和推特没收关注的用户
# 将连两次表，先从user到tweet，再到favorite，sql如下
"""
SELECT user.username, COUNT(favorite.id)
FROM user
LEFT OUTER JOIN tweet ON tweet.user_id = user.id
LEFT OUTER JOIN favorite ON favorite.tweet_id = tweet.id
GROUP BY user.username
"""
# 查询如下
query = (User
         .select(User.username, fn.COUNT(Favorite.id).alias('count'))
         .join(Tweet, JOIN.LEFT_OUTER)  # Joins user -> tweet.
         .join(Favorite, JOIN.LEFT_OUTER)  # Joins tweet -> favorite.
         .group_by(User.username))
for user in query:
     print(user.username, user.count)


# 2，连接多个表，切换连接上下文
# 查询Huey的tweets和它们favorited的次数
"""
SELECT tweet.content, COUNT(favorite.id)
FROM tweet
INNER JOIN user ON tweet.user_id = user.id
LEFT OUTER JOIN favorite ON favorite.tweet_id = tweet.id
WHERE user.username = 'huey'
GROUP BY tweet.content;"""
query = (Tweet
         .select(Tweet.content, fn.COUNT(Favorite.id).alias('count'))
         .join(User)  # Join from tweet -> user.
         .switch(Tweet)  # Move "join context" back to tweet.
         .join(Favorite, JOIN.LEFT_OUTER)  # Join from tweet -> favorite.
         .where(User.username == 'huey')
         .group_by(Tweet.content))
# 使用switch的作用就是switch后面的join，不会和User连接，而是和继续Tweet连接

# 也可使用join_from()，效果与上面相同
query = (Tweet
         .select(Tweet.content, fn.COUNT(Favorite.id).alias('count'))
         .join_from(Tweet, User)  # Join tweet -> user.
         .join_from(Tweet, Favorite, JOIN.LEFT_OUTER)  # Join tweet -> favorite.
         .where(User.username == 'huey')
         .group_by(Tweet.content))

for tweet in query:
     print('%s favorited %d times' % (tweet.content, tweet.count))
