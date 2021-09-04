from models import Tweet, MyModel

# 分页


# 1.paginate(page, paginate_by )
# 参数：page：页数，从1开始；paginate_by：每页记录数
for tweet in Tweet.select().order_by(Tweet.id).paginate(1, 10):
    print(tweet.message)
# 也可以使用 limit() and offset().