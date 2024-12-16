import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm, Column, ForeignKey

from data_db.db_session import SqlAlchemyBase

# Привязка класса к таблице questions
class Question(SqlAlchemyBase, UserMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    answers = orm.relationship('Answer', back_populates='question')

    topic = orm.relationship('Topic')
    topic_id = Column(sqlalchemy.Integer, ForeignKey('topic.id'))


    def is_radio(self):
        return self.type == 'radio'
