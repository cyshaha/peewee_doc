from peewee import *
from relationsAndJoins.model_and_data import BaseModel, db

# 实现多对多
# Peewee提供了一个表示多对多关系的字段，就像Django一样。
# 这个特性是由于用户的许多请求而添加的，但我强烈建议不要使用它，因为它将字段的概念与连接表和隐藏连接混为一谈。

# 1.新建一个关联关系表实现多对多
# 新建一个关联关系表，如下


class Student(Model):
    name = CharField()

class Course(Model):
    name = CharField()

class StudentCourse(Model):
    student = ForeignKeyField(Student)
    course = ForeignKeyField(Course)

# 假设我们要查找进入数学班的学生：
query = (Student
         .select()
         .join(StudentCourse)
         .join(Course)
         .where(Course.name == 'math'))
for student in query:
    print(student.name)

# 查询给定学生注册的课程：
courses = (Course
           .select()
           .join(StudentCourse)
           .join(Student)
           .where(Student.name == 'da vinci'))
for course in courses:
    print(course.name)

# 列出所有学生及其各自的课程
query = (StudentCourse
         .select(StudentCourse, Student, Course)
         .join(Course)
         .switch(StudentCourse)
         .join(Student)
         .order_by(Student.name))
for student_course in query:
    print(student_course.student.name, '->', student_course.course.name)


# 2.使用ManyToManyField
# 如果模型非常简单，并且查询需求也不是很复杂， 可以使用ManyToManyField。
class Student(BaseModel):
    name = CharField()

class Course(BaseModel):
    name = CharField()
    students = ManyToManyField(Student, backref='courses')

StudentCourse = Course.students.get_through_model()

db.create_tables([
    Student,
    Course,
    StudentCourse])

# Get all classes that "huey" is enrolled in:
huey = Student.get(Student.name == 'Huey')
for course in huey.courses.order_by(Course.name):
    print(course.name)

# Get all students in "English 101":
engl_101 = Course.get(Course.name == 'English 101')
for student in engl_101.students:
    print(student.name)

# When adding objects to a many-to-many relationship, we can pass
# in either a single model instance, a list of models, or even a
# query of models:
huey.courses.add(Course.select().where(Course.name.contains('English')))

engl_101.students.add(Student.get(Student.name == 'Mickey'))
engl_101.students.add([
    Student.get(Student.name == 'Charlie'),
    Student.get(Student.name == 'Zaizee')])

# The same rules apply for removing items from a many-to-many:
huey.courses.remove(Course.select().where(Course.name.startswith('CS')))

engl_101.students.remove(huey)

# Calling .clear() will remove all associated objects:
cs_150.students.clear()

# 不建议使用ManyToManyField