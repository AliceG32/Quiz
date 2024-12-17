from flask import redirect, render_template, Flask
from flask_login import login_user, LoginManager, logout_user, login_required, current_user
from sqlalchemy import and_

from data_db import db_session
from data_db.answer import Answer
from data_db.topic import Topic
from data_db.topic_links import TopicLinks
from data_db.user import User
from data_db.result import Result
from data_db.question import Question
from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm
from forms.QuestionForm import QuestionForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwwqrwqrg44t5gfdgfd'
login_manager = LoginManager()
login_manager.init_app(app)
question_ids = []
correct_answers_count = 0
users_data = {}


def generate_form(question_id):
    db_sess = db_session.create_session()
    question = db_sess.query(Question).filter(Question.id == question_id).first()
    form = QuestionForm()
    if question.is_radio():
        del form.checkAnswers
        choices = []
        for answer in question.answers:
            choices.append((answer.id, answer.text))
        form.radioAnswers.choices = choices
    else:
        del form.radioAnswers
        choices = []
        for answer in question.answers:
            choices.append((answer.id, answer.text))
        form.checkAnswers.choices = choices

    db_sess.close()
    return [form, question]


def count_correct_answers(form, question):
    result = 0
    if question.is_radio():
        for a in question.answers:
            if a.correct and a.id == form.radioAnswers.data:
                result = 1
                break
    else:
        # создание множества ответов из формы
        answers_from_form = set(map(int, form.checkAnswers.data))
        correct_answers = set()
        incorrect_answers = set()
        for a in question.answers:
            if a.correct:
                correct_answers.add(a.id)
            else:
                incorrect_answers.add(a.id)
        # ищем пересечение корректных и некорректных вопросов
        len_correct = len(correct_answers.intersection(answers_from_form))
        len_incorrect = len(incorrect_answers.intersection(answers_from_form))

        if len_correct == len(correct_answers) and len_incorrect == 0:
            result = 1

    return result


# функция считывает все вопросы в массив
def read_question_ids(topic_id: int):
    question_ids.clear()
    db_sess = db_session.create_session()
    questions = db_sess.query(Question).filter(Question.topic_id == topic_id).order_by(Question.id).all()
    for question in questions:
        question_ids.append(question.id)
    db_sess.close()


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def reset_user(user_id):
    del users_data[user_id]


@app.route("/", methods=['GET'])
def topics():
    if not current_user.is_authenticated:
        return redirect("/register")
    db_sess = db_session.create_session()
    topics = db_sess.query(Topic).order_by(Topic.text).all()
    users_data[current_user.id] = {}
    return render_template("topics.html", topics=topics)


def get_topic(topic_id):
    db_sess = db_session.create_session()
    return db_sess.query(Topic).order_by(Topic.text).filter_by(id=topic_id).first()


@app.route("/topic/<topic_id>", methods=['GET'])
def set_topic(topic_id):
    if not current_user.is_authenticated:
        return redirect("/login")

    read_question_ids(topic_id)
    topic = get_topic(topic_id)

    users_data[current_user.id] = {
        'topic_id': topic_id,
        'current_question_index': 0,
        'correct_answers': 0,
        'topic_text': topic.text,
        'answers_count': len(question_ids),
        'correct_answers_count': 0,
    }

    return redirect("/questions")


def update_user_results(user_id: int, topic_id: int, total_answers: int, correct_answers: int) -> Result:
    db_sess = db_session.create_session()
    q = db_sess.query(Result)
    q = q.filter(and_(Result.user_id == user_id, Result.topic_id == topic_id))
    record = q.first()
    if record is None:
        record = Result()
        record.user_id = user_id
        record.topic_id = topic_id
        record.total_answers = total_answers
        record.correct_answers = correct_answers
        db_sess.add(record)
        db_sess.commit()
    else:
        if record.correct_answers / record.total_answers < correct_answers / total_answers:
            record.total_answers = total_answers
            record.correct_answers = correct_answers
            db_sess.commit()

    db_sess.refresh(record)
    return record


def get_rating(user_id: int, topic_id: int):
    db_sess = db_session.create_session()

    q = db_sess.query(Result)
    total = q.filter(Result.topic_id == topic_id).count()

    q = db_sess.query(Result)
    result = q.filter(and_(Result.user_id == user_id, Result.topic_id == topic_id)).first()

    q = db_sess.query(Result)
    rating = q.filter(
        and_(
            Result.correct_answers / Result.total_answers > result.correct_answers / result.total_answers,
            Result.user_id != user_id,
            Result.topic_id == topic_id,
        )
    ).count()

    if rating == 0:
        return {
            'total': total,
            'rating': 1
        }
    else:
        return {
            'total': total,
            'rating': rating + 1
        }


@app.route("/questions", methods=['GET', 'POST'])
def questions():
    if not current_user.is_authenticated:
        return redirect("/login")

    [form, question] = generate_form(question_ids[users_data[current_user.id]['current_question_index']])
    if form.validate_on_submit():
        [form, question] = generate_form(question_ids[users_data[current_user.id]['current_question_index']])
        users_data[current_user.id]['correct_answers_count'] += count_correct_answers(form, question)
        # проверка последний ли вопрос
        # если не последний, то создается новая форма
        if users_data[current_user.id]['current_question_index'] < (len(question_ids) - 1):
            users_data[current_user.id]['current_question_index'] += 1
            [form, question] = generate_form(question_ids[users_data[current_user.id]['current_question_index']])
        else:
            if users_data[current_user.id]['answers_count'] != 0:
                correct_percent = int((100 * users_data[current_user.id]['correct_answers_count'] /
                                       users_data[current_user.id]['answers_count']))
            else:
                correct_percent = 0

            db_sess = db_session.create_session()
            links = db_sess.query(TopicLinks).filter_by(topic_id=users_data[current_user.id]['topic_id']).all()
            topic_text = users_data[current_user.id]['topic_text']

            result_best = update_user_results(
                current_user.id,
                users_data[current_user.id]['topic_id'],
                users_data[current_user.id]['answers_count'],
                users_data[current_user.id]['correct_answers_count']
            )

            correct_answers_count_best = result_best.correct_answers
            answers_count_best = result_best.total_answers
            correct_percent_best = int((100 * correct_answers_count_best / answers_count_best))
            rating = get_rating(
                current_user.id,
                users_data[current_user.id]['topic_id']
            )
            return render_template("finish.html",
                                   correct_answers_count=users_data[current_user.id]['correct_answers_count'],
                                   answers_count=users_data[current_user.id]['answers_count'],
                                   correct_percent=correct_percent,

                                   correct_answers_count_best=result_best.correct_answers,
                                   answers_count_best=result_best.total_answers,
                                   correct_percent_best=correct_percent_best,

                                   links_count=len(links),
                                   links=links,
                                   topic_text=topic_text,

                                   rating_total=rating['total'],
                                   rating=rating['rating']
                                   )

    return render_template("questions.html", question=question, form=form,
                           current_question_index=users_data[current_user.id]['current_question_index'] + 1,
                           total_questions=len(question_ids),
                           topic_text=users_data[current_user.id]['topic_text']
                           )


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            users_data[current_user.id] = {}
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    app.run(port=8081, host='127.0.0.1')
