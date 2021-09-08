from relationsAndJoins.model_and_data import User, Tweet
# 简单练习


# 1，查询tweet里，名字为huey的user的发布的内容
query = Tweet.select().join(User).where(User.username == 'huey')
for tweet in query:
    print(tweet.content)

print("=================")
# 我们不用显式的指定on，因为peewee从模型中推断，当我们从tweet加入到用户时，我们正在加入 Tweet.user 外键
# 以下查询时等价的
query = (Tweet
         .select()
         .join(User, on=(Tweet.user == User.id))
         .where(User.username == 'huey'))

# 2.查询名字为huey的user对象的所关联的所有tweet的内容
huey = User.get(User.username == 'huey')
for tweet in huey.tweets:
    print(tweet.content)

# 仔细看看 huey.tweets 我们可以看到它只是一个简单的预过滤 SELECT 查询：
print(huey.tweets)
print(huey.tweets.sql())