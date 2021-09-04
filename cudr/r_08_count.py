from models import Tweet

# 计数


# 1.count()
count = Tweet.select().where(Tweet.id < 50).count()
print(count)