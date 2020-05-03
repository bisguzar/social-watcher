import json
import time
import os
from peewee import *

database = SqliteDatabase("sqlite.db", field_types={"json": "text"})


class JSONField(Field):
    field_type = "json"

    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        return json.loads(value)


class BaseModel(Model):
    class Meta:
        database = database


class Instagram(BaseModel):
    username = CharField()
    timestamp = IntegerField(default=lambda: int(time.time()))
    data = JSONField()


class Twitter(BaseModel):
    username = CharField()
    timestamp = IntegerField(default=lambda: int(time.time()))
    data = JSONField()


if not os.path.exists("./sqlite.db"):
    print("Initializind db...")
    with database:
        database.create_tables([Instagram, Twitter])
