from models import User, User2, Sample


# 1.基本操作运算符示例
user = User.select().where(User.username == 'Charlie')
for u in user:
    print(u.username)

user = User.select().where(User.username.in_(['charlie', 'huey', 'mickey']))
for u in user:
    print(u.username)

sample = Sample.select().where(Sample.value.between(10, 100))
for s in sample:
    print(s.value)

user = User.select().where(User.username.startswith('C'))
for u in user:
    print(u.username)

user = User.select().where(User.username.contains('ar'))
for u in user:
    print(u.username)


# 2.逻辑运算符示例
user = User2.select().where(
  (User2.username == "huey") &
  (User2.login_count > 0))
for u in user:
    print(u.username)

user = User2.select().where(
  (User2.username == "huey") |
  (User2.login_count > 0))
for u in user:
    print(u.username)

active_user = User2.select().where(User2.login_count > 0)
non_active_user = User2.select().where(User2.id.not_in(active_user))
for u in non_active_user:
    print(u.username)