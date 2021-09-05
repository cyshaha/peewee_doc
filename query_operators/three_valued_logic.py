from models import User


# 三值逻辑
# IS NULL
# IS NOT NULL
# IN
# NOT IN


# 1. IS NULL和IN
# Get all User objects whose last login is NULL.
User.select().where(User.last_login >> None)
# Get users whose username is in the given list.
usernames = ['charlie', 'huey', 'mickey']
User.select().where(User.username << usernames)

# 如果不使用重载运算符，也可以使用字段方法
User.select().where(User.last_login.is_null(True))
User.select().where(User.username.in_(usernames))


# 2. IS NOT NULL 和 NOT IN
# Get all User objects whose last login is *NOT* NULL.
User.select().where(User.last_login.is_null(False))
# Using unary negation instead.
User.select().where(~(User.last_login >> None))
# Get users whose username is *NOT* in the given list.
User.select().where(User.username.not_in(usernames))
# Using unary negation instead.
User.select().where(~(User.username << usernames))