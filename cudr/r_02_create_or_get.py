from datetime import datetime

from models import Person
# 创建或获取

# 1.Model.get_or_create()
# 尝试检索匹配的行，如果失败，将创建一个新行。
#   defaults：create时字段的值
#   defaults之外的为get查询时的条件
person, created = Person.get_or_create(
    first_name="Bob",
    defaults={'birthday': datetime.date(1940, 10, 9)})
