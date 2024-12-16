from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, SelectMultipleField, widgets
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class QuestionForm(FlaskForm):
    radioAnswers = RadioField('Выберите верный ответ', choices=[], coerce=int, validators=[DataRequired()])
    checkAnswers = MultiCheckboxField('Выберите верные ответы', choices=[], coerce=int)
    submit = SubmitField('Ответить')

