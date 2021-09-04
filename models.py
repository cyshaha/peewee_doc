# 本文档使用的模型
from peewee import *


db_mysql = MySQLDatabase(host='127.0.0.1', port=3306, user='root', passwd='root', database="peewee_doc")
db_mysql.connect()


class Person(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db_mysql # This model uses the "people.db" database.


class Pet(Model):
    owner = ForeignKeyField(Person, backref='pets')
    name = CharField()
    animal_type = CharField()

    class Meta:
        database = db_mysql


class User(Model):
    id = AutoField()
    username = CharField()

    class Meta:
        database = db_mysql


class Tweet(Model):
    id = AutoField()
    message = CharField()
    user = ForeignKeyField(User, backref='user')
    is_published = BooleanField(default='')
    creation_date = DateField(null=True)

    class Meta:
        database = db_mysql


class User2(Model):
    username = CharField(unique=True)
    last_login = DateTimeField(null=True)
    login_count = IntegerField(null=True)

    class Meta:
        database = db_mysql


class KV(Model):
    key = CharField(unique=True)
    value = IntegerField()

    class Meta:
        database = db_mysql

db_mysql.create_tables([Person, Pet, User, Tweet, User2, KV])