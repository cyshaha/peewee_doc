from models import User, Tweet, db_mysql
# 查询多条记录

# 1.Model.select()
# 返回多行记录，支持迭代、索引、切片
query = User.select()
print([user.username for user in query])

print( query[1])
print(query[1].username)
print(query[:2])


# 2.查询外键
# user = User.get(User.id == 2)
tweet = Tweet.get_by_id(3)
# for user in tweet.user:
print(tweet.user.username)


# 3.查询结果转为字典等其他格式
#   dicts()
#   namedtuples()
#   tuples()
query = User.select().dicts()
for row in query:
    print(row)


# 扩展内容：性能提升

# 4.iterator()
# peewee 默认缓存查询结果，如果数据量很大，不想缓存，则使用iterator()
# 不实际操作了。参考官方文档示例
# Let's assume we've got 10 million stat objects to dump to a csv file.
# stats = Stat.select()
# Our imaginary serializer class
# serializer = CSVSerializer()
# Loop over all the stats and serialize.
# for stat in stats.iterator():
#     serializer.serialize_object(stat)

# 5.query.objects()
# 当遍历包含多个表中的列的大量行时，Peewee将为返回的每一行重建模型图，此操作可能很慢。
# 例如，如果我们选择一个tweet列表以及tweet作者的用户名和化身，那么peewee必须为每行创建两个对象（tweet和一个用户）
# objects() 它将以模型实例的形式返回行，但不会尝试解析模型图。
# 以下为官方示例
query = (Tweet
         .select(Tweet, User)  # Select tweet and user data.
         .join(User))
# Note that the user columns are stored in a separate User instance
# accessible at tweet.user:
for tweet in query:
    print(tweet.user.username, tweet.content)
# Using ".objects()" will not create the tweet.user object and assigns all
# user attributes to the tweet instance:
for tweet in query.objects():
    print(tweet.username, tweet.content)

# 6.Database.execute()
# 为了获得最大的性能，可以执行查询，然后使用底层数据库光标迭代结果
# 光标将返回原始行元组
# 以下为官方示例
query = Tweet.select(Tweet.content, User.username).join(User)
cursor = db_mysql.execute(query)
for (content, username) in cursor:
    print(username, '->', content)
