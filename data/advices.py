import datetime
import sqlalchemy
from flask_login import UserMixin
# from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Advices(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Advices'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    advice = sqlalchemy.Column(sqlalchemy.String, nullable=True)