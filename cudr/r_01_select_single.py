from models import User
# 查询单个记录


# 1.Model.get()
user = User.get(User.id == 1)
print(user.username)


# 2.Model.get_by_id()
# 主键查找
user = User.get_by_id(1)
print(user.username)


