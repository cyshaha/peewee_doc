import datetime
from peewee import *


# 表达式
# 有两张类型的对象可以创建表达式
#   1.Field instances
#   2.SQL聚合和函数使用 fn


class User(Model):
    username = CharField()
    is_admin = BooleanField()
    is_active = BooleanField()
    last_login = DateTimeField()
    login_count = IntegerField()
    failed_logins = IntegerField()


# 1.基本使用
# username is equal to 'charlie'
User.username == 'charlie'
# user has logged in less than 5 times
User.login_count < 5


# 2.与and和or使用
# 比较可以嵌套到任意深度：
# User is both and admin and has logged in today
(User.is_admin == True) & (User.last_login >= today)
# User's username is either charlie or charles
(User.username == 'charlie') | (User.username == 'charles')


# 3.与函数fn和其他算数表达式使用
# user's username starts with a 'g' or a 'G':
fn.Lower(fn.Substr(User.username, 1, 1)) == 'g'
(User.failed_logins > (User.login_count * .5)) & (User.login_count > 10)
User.update(login_count=User.login_count + 1).where(User.id == user_id)



# 4.行值 Tuple()
# 类似python的元组，通常用来再一个表达式中比较自已子查询的多个列的值
# 参考官方文档案例
class EventLog(Model):
    event_type = TextField()
    source = TextField()
    data = TextField()
    timestamp = TimestampField()

class IncidentLog(Model):
    incident_type = TextField()
    source = TextField()
    traceback = TextField()
    timestamp = TimestampField()

# Get a list of all the incident types and sources that have occured today.
incidents = (IncidentLog
             .select(IncidentLog.incident_type, IncidentLog.source)
             .where(IncidentLog.timestamp >= datetime.date.today()))

# Find all events that correlate with the type and source of the
# incidents that occured today.
events = (EventLog
          .select()
          .where(Tuple(EventLog.event_type, EventLog.source).in_(incidents))
          .order_by(EventLog.timestamp))
# 实现这个功能的另一个方法是子查询