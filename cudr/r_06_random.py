from peewee import fn
# ιζΊθ·ε


# 1.Postgresql and Sqlite use the Random function:
# Pick 5 lucky winners:
LotteryNumber.select().order_by(fn.Random()).limit(5)


# 2.MySQL uses Rand:
LotteryNumber.select().order_by(fn.Rand()).limit(5)
