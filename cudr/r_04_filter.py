from models import User, Tweet
# 筛选


# 1.get(筛选条件)
user = User.get(User.username == 'Charlie')
print(user)


# 2.select().where()
for tweet in Tweet.select().where(Tweet.user == user, Tweet.is_published == True):
     print(tweet.user.username, '->', tweet.message)


# 3.跨表筛选
for tweet in Tweet.select().join(User).where(User.username == 'Charlie'):
     print(tweet.message)


# 4.多条件查询
Tweet.select().join(User).where((User.username == 'Charlie') | (User.username == 'Peewee Herman'))
# &：和 ；|：或
# 更多参考后章操作符
