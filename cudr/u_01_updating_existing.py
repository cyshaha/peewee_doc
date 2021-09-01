# 查询
from datetime import datetime
from cudr.c_01_insert import Tweet
# print(datetime.today())

query = Tweet.update(is_published=True).where(Tweet.creation_date <  datetime.today())
query.execute()


#  atomic updates
query = Stat.update(counter=Stat.counter + 1).where(Stat.url == request.url)
query.execute()

#
query = Employee.update(bonus=(Employee.bonus + (Employee.salary * .1)))
query.execute()  # Give everyone a bonus!


#
subquery = Tweet.select(fn.COUNT(Tweet.id)).where(Tweet.user == User.id)
update = User.update(num_tweets=subquery)
update.execute()