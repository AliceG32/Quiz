# Подключаем необходимы библиотеки
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey
from sqlalchemy import orm

from data_db.db_session import SqlAlchemyBase

# Создание таблицы с данными: id, question_id, text, correct и question
class Answer(SqlAlchemyBase, UserMixin):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    correct = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    question = orm.relationship('Question')
    question_id = Column(sqlalchemy.Integer, ForeignKey('questions.id'))
