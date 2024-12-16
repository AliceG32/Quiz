import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, Column, ForeignKey

from data_db.db_session import SqlAlchemyBase


class Topic(SqlAlchemyBase, UserMixin):
    __tablename__ = 'topic'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    questions = orm.relationship('Question', back_populates='topic')

    topic_links = orm.relationship('TopicLinks', back_populates='topic')

    results = orm.relationship('Result', back_populates='topic')