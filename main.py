from flask import redirect, render_template, Flask
from flask_login import LoginManager, logout_user, login_required

from data_db import db_session
from data_db.user import User
from forms.RegisterForm import RegisterForm

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
def topics():    return redirect("/register")

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


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
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/data.db")
    app.run(port=8081, host='127.0.0.1')
