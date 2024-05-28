import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from data.users import User
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Status_recommendation(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Status_recommendations'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    chat_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
    rec_status_1 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_2 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_3 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_4 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_5 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_6 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_7 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_8 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_9 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_10 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_11 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_12 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_13 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_14 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_15 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_16 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_17 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_18 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_19 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_20 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_21 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_22 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_23 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_24 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_25 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_26 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_27 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_28 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_29 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')
    rec_status_30 = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0')