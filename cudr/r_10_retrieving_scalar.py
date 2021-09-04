# 找查询结果标量


# Query.scalar()
# 参考官方文档示例
PageView.select(fn.Count(fn.Distinct(PageView.url))).scalar()
# 多个标量使用as_tuple=True
Employee.select(fn.Min(Employee.salary), fn.Max(Employee.salary)).scalar(as_tuple=True)
