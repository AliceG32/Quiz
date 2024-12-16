import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, Column, ForeignKey

from data_db.db_session import SqlAlchemyBase

# Привязка класса к таблице topic_links
class TopicLinks(SqlAlchemyBase, UserMixin):
    __tablename__ = 'topic_links'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    link = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    topic = orm.relationship('Topic')
    topic_id = Column(sqlalchemy.Integer, ForeignKey('topic.id'))

