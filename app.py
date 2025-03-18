from flask import Flask, render_template, request, redirect, session,flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import config
from models import db, Users
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL   # адрес базы данных
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False   # отключаем отслеживание изменений в базе данных
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")   # устанавливаем секретный ключ

db.init_app(app)

# декоратор для проверки входа
def login_required(f):
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__ # сохраняет оригинальное имя функции
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template("index.html")

@app.route('/stretching')
@login_required
def stretching():
    return render_template('stretching.html')

@app.route('/strength')
@login_required
def strength():
    return render_template('strength.html')

@app.route('/mfr')
@login_required
def mfr():
    return render_template('mfr.html')

@app.route('/meditation')
@login_required
def meditation():
    return render_template('meditation.html')

# обработчик страницы регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = Users.query.filter_by(username=username).first() # проверяем, есть ли уже такой пользователь
        if existing_user:
            flash("Такой пользователь уже существует", "danger")
            return redirect(url_for('register'))


        hashed_password = generate_password_hash(password)  #  хешируем пароль перед сохранением

        new_user = Users(username=username, password=hashed_password)  # создаем объект пользователя
        db.session.add(new_user)
        db.session.commit()

        flash("Регистрация успешна! Теперь войдите в аккаунт.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# обработчик страницы входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # сохраняем пользователя в сессию
            return redirect(url_for('index'))
        else:
            flash("Неправильный логин или пароль", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
