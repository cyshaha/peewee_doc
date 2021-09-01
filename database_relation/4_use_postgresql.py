# 2使用postgresql

from peewee import *

psql_db = PostgresqlDatabase("peewee_test",
                             user='postgres')

class BaseModel(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = psql_db

class User(BaseModel):
    username = CharField()


