import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, Column, ForeignKey

from data_db.db_session import SqlAlchemyBase

# Привязка класса к таблице results
class Result(SqlAlchemyBase, UserMixin):
    __tablename__ = 'results'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    total_answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    correct_answers = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    topic = orm.relationship('Topic')
    topic_id = Column(sqlalchemy.Integer, ForeignKey('topic.id'))

    user = orm.relationship('User')
    user_id = Column(sqlalchemy.Integer, ForeignKey('users.id'))
