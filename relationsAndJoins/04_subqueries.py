from relationsAndJoins.model_and_data import User, Tweet
from peewee import *


# 子查询
# Peewee允许连接任何类似于表的对象，包括子查询或公共表表达式（CTE）

# 1.子查询
# 查询所有用户和他们最新的推特
"""
SELECT tweet.*, user.*
FROM tweet
INNER JOIN (
    SELECT latest.user_id, MAX(latest.timestamp) AS max_ts
    FROM tweet AS latest
    GROUP BY latest.user_id) AS latest_query
ON ((tweet.user_id = latest_query.user_id) AND (tweet.timestamp = latest_query.max_ts))
INNER JOIN user ON (tweet.user_id = user.id)
"""
# 因为需要在外层直接从Tweet查询数据，所以我们需要给Tweet取个别名
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

# 2.使用Common-table Expressions
# Here is the SQL:
"""
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
"""
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