from relationsAndJoins.model_and_data import Favorite, User, Tweet


# select字段来源多个表


# 1.查询所有tweet以及作者的用户名
for tweet in Tweet.select():
    print(tweet.user.username, '->', tweet.content)
# 上面的循环存在一个大问题：它对每个tweet执行一个额外的查询来查找 tweet.user 外键。
# 对于我们的小表，性能损失并不明显，但是我们会发现延迟随着行数的增加而增加


# 2.连表查询
# 如下sql
"""
SELECT tweet.content, user.username
FROM tweet
INNER JOIN user ON tweet.user_id = user.id;
"""
for row in Tweet.select(Tweet.content, User.username).join(User).dicts():
    print(row)


# 3.返回joined的模型实例的数据
# 如果不使用.dicts()方法，结果将返回Tweet对象
# 那么username的值是分配给tweet.user.username而不是tweet.username
for tweet in Tweet.select(Tweet.content, User.username).join(User):
     print(tweet.user.username, '->', tweet.content)


# 4.attr参数
# 如果希望控制把连接的User实例放到哪里，可以在join方法中使用attr参数
query = Tweet.select(Tweet.content, User.username).join(User, attr='author')
for tweet in query:
    print(tweet.author.username, '->', tweet.content)


# 5.objects()
# 把查询的所有的结果都放到Tweet实例属性里
for tweet in query.objects():
     print(tweet.username, '->', tweet.content)