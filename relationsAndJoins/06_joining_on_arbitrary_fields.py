from relationsAndJoins.model_and_data import User, BaseModel
from peewee import *

# 在任意字段上联接
# 如果两个表之间不存在外键，则仍可以执行联接，但必须手动指定联接谓词
# 见官方文档示例

class ActivityLog(BaseModel):
    object_id = IntegerField()
    activity_type = CharField()

user_log = (User
            .select(User, ActivityLog)
            .join(ActivityLog, on=(User.id == ActivityLog.object_id), attr='log')
            .where(
                (ActivityLog.activity_type == 'user_activity') &
                (User.username == 'charlie')))

for user in user_log:
    print(user.username, user.log.description)

#### Print something like ####
# charlie logged in
# charlie posted a tweet
# charlie retweeted
# charlie posted a tweet
# charlie logged out

# 注意：join里参数attr的使用，把join的模型ActivityLog分配给了joined对象的属性
# 可以直接访问连接的模型ActivityLog，而不用产生额外的查询