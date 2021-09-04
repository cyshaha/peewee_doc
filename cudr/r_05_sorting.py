from models import Tweet

# 排序

# 1.order_by()
for t in Tweet.select().order_by(Tweet.creation_date):
     print(t.creation_date)
for t in Tweet.select().order_by(Tweet.creation_date.desc()):
     print(t.creation_date)
# 也可以使用+和-控制排序顺序
Tweet.select().order_by(-Tweet.creation_date)
