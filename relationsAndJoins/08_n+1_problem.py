# N + 1 问题
# 指执行查询的时候，对于结果集的每一行，都至少执行了一个其他查询（将其概念化的另一种方法是作为嵌套循环）
# 在大多数情况下可以使用join或子查询避免
# 数据库本身可能或做一个嵌套循环，但是相比于在程序代码里做n次查询循环性能更好，因为查询可能会涉及与数据库连接的网略延迟，
# 且当join或子查询时，可能没有用到数据库提供的索引
from datetime import datetime
from peewee import *
from relationsAndJoins.model_and_data import Tweet, User

# 1.使用join
# 查询最近的10条tweet的content和它们的作者username，n + 1 的场景是
#   1.获取最近的10条tweet
#   2.对于每条tweet，查询它们的作者
# 如果使用join，如下：

query = (Tweet
         .select(Tweet, User)  # Note that we are selecting both models.
         .join(User)  # Use an INNER join because every tweet has an author.
         .order_by(Tweet.id.desc())  # Get the most recent tweets.
         .limit(10))
for tweet in query:
    print(tweet.user.username, '-', tweet.message)
# 如果没有join，需要查询tweet.user.username的时候，触发查询外键tweet.user 并检索关联的user


# 2.prefetch()
# 查询几个用户和他们所有的推特，N + 1场景如下：
#   1.获取几个user
#   2.对于每个user，获取他们的tweet
# 这个场景和上个类似，但是又不太一样，当我们获取tweet时，可以关联到一个用户，所以可以直接使用外键
# 但是反过来，一个user可能又多个tweet，
# peewee提供了一种方法避免 O(n)查询：获取user，然后获取和这些user关联的所有tweet，一旦获取足够大的tweet列表，就会把它们分配出去
# 这种方法通常比较快，但是会分别查询两张表
# 使用prefetch：会只用子查询提前加载user相关的tweet，这就使原来的n行n次查询变为k表k次查询
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

# prefetch可以用在查询任意数量的表