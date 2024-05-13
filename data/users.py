import datetime
import sqlalchemy
from flask_login import UserMixin
# from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Users'
    User_ID = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Registration_Day = sqlalchemy.Column(sqlalchemy.DateTime,
                                         default=datetime.datetime.now)
    Age_Group = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Schedule = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Sex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
