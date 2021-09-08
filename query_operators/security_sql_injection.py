from models import MyModel
from peewee import *

# 安全和sql注入
# peewee默认会把查询参数化，不要把不信任的数据直接放入sql里，而应该作为参数

user_data = "somedata"
# Bad! DO NOT DO THIS!
query = MyModel.raw('SELECT * FROM my_table WHERE data = %s' % (user_data,))

# Good. `user_data` will be treated as a parameter to the query.
query = MyModel.raw('SELECT * FROM my_table WHERE data = %s', user_data)

# Bad! DO NOT DO THIS!
query = MyModel.select().where(SQL('Some SQL expression %s' % user_data))

# Good. `user_data` will be treated as a parameter.
query = MyModel.select().where(SQL('Some SQL expression %s', user_data))