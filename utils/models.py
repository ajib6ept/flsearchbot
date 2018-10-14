
from peewee import (SqliteDatabase, Model, IntegerField, CharField,
                    BooleanField, ForeignKeyField, DateTimeField)

db = SqliteDatabase('fl_search_app.db')


class BaseModel(Model):

    class Meta:
        database = db


class User(BaseModel):
    telegram_id = IntegerField(primary_key=True)
    username = CharField()
    firstname = CharField(null=True)
    lastname = CharField(null=True)
    is_active = BooleanField(default=True)


class FLKey(BaseModel):
    user = ForeignKeyField(User, backref='flkeys')
    name = CharField()


class FLProject(BaseModel):
    project_url = CharField()
    project_title = CharField()
    project_body = CharField()
    project_added = DateTimeField()


def create_tables():
    with db:
        db.create_tables([User, FLKey, FLProject])


if __name__ == '__main__':
    create_tables()
