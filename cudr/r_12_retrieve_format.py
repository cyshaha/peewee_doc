from models import Sample
from peewee import *


# 不同返回的数据格式
# 有时不需要创建模型实例的开销，只需要遍历行数据，不需要model提供的所有api，可调整返回格式
#   dicts()
#   namedtuples()
#   tuples()
#   objects()


# 1.tuples()
# 每行记录为一个元组格式
stats = (Sample
         .select(Sample.counter, fn.Count(Sample.value))
         .group_by(Sample.counter)
         .tuples())
# iterate over a list of 2-tuples containing the url and count
for counter, value in stats:
    print(counter, value)


# 2.dicts()
# 每行记录为一个字典格式
stats = (Sample
         .select(Sample.counter, fn.Count(Sample.value).alias("vc"))
         .group_by(Sample.counter)
         .dicts())
# iterate over a list of 2-tuples containing the url and count
for stat in stats:
    print(stat["counter"], stat["vc"])