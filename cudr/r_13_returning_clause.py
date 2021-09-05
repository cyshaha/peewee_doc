from peewee import logger
from models import User
from peewee import *


# 返回子句
# 在执行UPDATE，INSERT和DELETE查询时，会返回不同的值
#   1.INSERT：自动递增新插入行的主键值。如果不使用自动递增的主键，Postgres将返回新行的主键，但SQLite和MySQL将不返回。
#   2.UPDATE：修改的行数
#   3.DELETE：删除的行数
# 当使用返回子句时，就会返回一个可迭代的游标对象


# 参考官方文档示例
# 1.UPDATE
# 修改不激活的用户为激活状态，并发送邮件，使用返回子句，就不用update之后再去查询有哪些用户了
query = (User
         .update(is_active=False)
         .where(User.registration_expired == True)
         .returning(User))
def send_deactivation_email(email):
    pass
# Send an email to every user that was deactivated.
for deactivated_user in query.execute():
    send_deactivation_email(deactivated_user.email)


# 2.INSERT
# 创建一个新用户之后，要打印日志，可以使用返回子句，避免再查询
query = (User
         .insert(email='foo@bar.com', created=fn.now())
         .returning(User))  # Shorthand for all columns on User.
# When using RETURNING, execute() returns a cursor.
cursor = query.execute()
# Get the user object we just inserted and log the data:
user = cursor[0]
logger.info('Created user %s (id=%s) at %s', user.email, user.id, user.created)


# 3.返回不同的行类型
# 默认返回一个model实例，如下，可以返回字典类型的行
data = [{'name': 'charlie'}, {'name': 'huey'}, {'name': 'mickey'}]
query = (User
         .insert_many(data)
         .returning(User.id, User.username)
         .dicts())
for new_user in query.execute():
    print('Added user "%s", id=%s' % (new_user['username'], new_user['id']))
