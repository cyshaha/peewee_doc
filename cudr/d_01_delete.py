from models import User2, Tweet
import datetime
# 删除

# 1.delete_instance()
# 删除一个实例
user = User2.get(User2.id == 4)
user.delete_instance()


# 2.Model.delete_instance()
# 删除满足条件的多个实例
query = Tweet.delete().where(Tweet.id > 3)
query.execute() # 返回删除的行数