from flask import redirect, render_template, Flask
from flask_login import login_user, LoginManager, logout_user, login_required, current_user

from data_db import db_session
from data_db.user import User
from forms.RegisterForm import RegisterForm
from forms.LoginForm import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwwqrwqrg44t5gfdgfd'
login_manager = LoginManager()
login_manager.init_app(app)
question_ids = []
correct_answers_count = 0
users_data = {}

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
