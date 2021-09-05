from peewee import *
from models import Sample


# 窗口函数
# 窗口函数在滑动窗口数据上和是和聚合函数结合，作为select过程的一部分。
# 窗口函数功能：
#   1.对结果集的子集执行聚合
#   2.计算运行总数
#   3.排序结果
#   4.比较行与行的值
# 可以通过调用 Function.over() 并传入分区或排序参数


# 1.Ordered Windows
# 1.1计算累计和
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(order_by=[Sample.counter]).alias('total'))
for sample in query:
    print(sample.counter, sample.value, sample.total)

# 1.2计算前后差值
# fn.LAG取前n行
difference = Sample.value - fn.LAG(Sample.value, 1).over(order_by=[Sample.id])
query = Sample.select(
    Sample.counter,
    Sample.value,
    difference.alias('diff'))
for sample in query:
    print(sample.counter, sample.value, sample.diff)


# 2.Partitioned Windows
# 2.1 以counter分组计算value平均值
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.AVG(Sample.value).over(partition_by=[Sample.counter]).alias('cavg'))
for sample in query:
    print(sample.counter, sample.value, sample.cavg)

# 2.2 在窗口内使用order_by
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.RANK().over(
        order_by=[Sample.value],
        partition_by=[Sample.counter]).alias('rank'))
for sample in query:
    print(sample.counter, sample.value, sample.rank)


# 3.Bounded windows 有界窗口
# 默认窗口是从第一行到最后一行，可以使用有界窗口约束窗口边界
#   1.Window.CURRENT_ROW - 引用当前行的属性
#   2.Window.preceding() - 指定前面的行数，忽略表示前面所有
#   3.Window.following() - 指定后面的行数，忽略表示前面所有

# 3.1前面两行到当前行
#  end=Window.CURRENT不需要特别说明，是默认值
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.id],
        start=Window.preceding(2),
        end=Window.CURRENT_ROW).alias('rsum'))
for sample in query:
    print(sample.counter, sample.value, sample.rsum)

# 3.2计算当前行到最后一行的和
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.id],
        start=Window.CURRENT_ROW,
        end=Window.following()).alias('rsum'))
for sample in query:
    print(sample.counter, sample.value, sample.rsum)


# 4.Filtered Aggregates
# 只适用于(Postgres and Sqlite 3.25+
# filter()要在 over()之前
# query = Sample.select(
#     Sample.counter,
#     Sample.value,
#     fn.SUM(Sample.value).filter(Sample.counter != 2).over(
#         order_by=[Sample.id]).alias('csum'))
# for sample in query:
#     print(sample.counter, sample.value, sample.csum)
# 1    10.    10.
# 1    20.    30.
# 2     1.    30.
# 2     3.    30.
# 3   100    130.
# 累加的时候跳过counter为2的


# 5.Reusing Window Definitions定义窗口再使用
# 提前定义一个窗口，多次使用
win = Window(order_by=[Sample.id])
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.LEAD(Sample.value).over(win),
    fn.LAG(Sample.value).over(win),
    fn.SUM(Sample.value).over(win)
    ).window(win)
for row in query.tuples():
    print(row)


# 6.Multiple window definitions
# 要确保每个窗口有唯一的alias

# 6.1 多个定义窗口
w1 = Window(order_by=[Sample.id]).alias('w1')
w2 = Window(partition_by=[Sample.counter]).alias('w2')
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(w1).alias('rsum'),  # Running total.
    fn.AVG(Sample.value).over(w2).alias('cavg')   # Avg per category.
).window(w1, w2)  # Include our window definitions.
for sample in query:
    print(sample.counter, sample.value, sample.rsum, sample.cavg)

# 6.2扩展窗口
w1 = Window(partition_by=[Sample.counter]).alias('w1')
w2 = Window(extends=w1, order_by=[Sample.value.desc()]).alias('w2')
query = (Sample
         .select(Sample.counter, Sample.value,
                 fn.SUM(Sample.value).over(w1).alias('group_sum'),
                 fn.RANK().over(w2).alias('revrank'))
         .window(w1, w2)
         .order_by(Sample.id))
for sample in query:
    print(sample.counter, sample.value, sample.group_sum, sample.revrank)


# 7.Frame types参数
#  Window.RANGE：如果有重复项，会把所有重复项一起聚合
#  Window.ROWS：如果有重复项，会把所有重复项分开为每行聚合
#  Window.GROUPS：mysql不支持
# 现在数据如下：
# id	counter	value
# 1	    1	    10.0
# 2	    1	    20.0
# 3	    2	    1.0
# 4	    2	    3.0
# 5	    3	    100.0
# 6	    1	    20.0
# 7	    2	    1.0

print("+++++++++++++++++++++++++++")
# 7.1 Window.RANGE
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.counter, Sample.value],
        frame_type=Window.RANGE).alias('rsum'))
for sample in query.order_by(Sample.counter, Sample.value):
    print(sample.counter, sample.value, sample.rsum)
# counter为20的有两个，所以计算累加时，两个同时全部加上

# 7.2 Window.ROWS
query = Sample.select(
    Sample.counter,
    Sample.value,
    fn.SUM(Sample.value).over(
        order_by=[Sample.counter, Sample.value],
        frame_type=Window.ROWS).alias('rsum'))
for sample in query.order_by(Sample.counter, Sample.value):
    print(sample.counter, sample.value, sample.rsum)
# counter为20的有两个，计算累加时，分别计算

# 7.3 Window.GROUPS
query = (Sample
         .select(Sample.counter, Sample.value,
                 fn.SUM(Sample.value).over(
                    order_by=[Sample.counter, Sample.value],
                    frame_type=Window.GROUPS,
                    start=Window.preceding(1)).alias('gsum'))
         .order_by(Sample.counter, Sample.value))
for sample in query:
    print(sample.counter, sample.value, sample.gsum)
# 如果如下：
# 1     10.0    10.0
# 1     20.0    30.0
# 1     20.0    40.0
# 2     1.0     21.0
# 2     1.0     2.0
# 2     3.0     4.0
# 3     100.0   103.0
# Window.GROUPS，则以Sample.counter, Sample.value分组，相同的分为一组，
# 组合值为组内行值之和，一组为单位，求当前组和前一组相加的和

# 使用规则
#   1.如果指定了frame_type的类型，则就使用frame_type
#   2.如果start and/or end 边界被定义， Peewee默认使用ROWS.
#   3.如果没有定义start and/or end，则使用默认的RANGE
