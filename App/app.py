import flask
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import ValidationError
import random
from data import db_session
from data.users import *

data = {
    'tasks': {
        'count': 2,
        1: {
            'name': 'Task 1',
            'description': "lorem lorem lorem lorem lorem lorem",
            'status': 0,
            'subtasks': {
                'count': 2,
                1: {
                    'text': 'ha ha ha ha',
                    'status': 1
                },
                2: {
                    'text': 'ha ha ha ha',
                    'status': 0
                }
            }
        },
        2: {
            'name': 'Task 2',
            'description': "lorem lorem lorem lorem lorem lorem",
            'status': 0,
            'subtasks': {
                'count': 2,
                1: {
                    'text': 'ha ha ha ha',
                    'status': 0
                },
                2: {
                    'text': 'ha ha ha ha',
                    'status': 0
                }
            }
        }
    }
}

app = flask.Flask(__name__)
SQLAlchemyDB = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'LoginUser'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///static/databases/database.db'
app.config['SECRET_KEY'] = "IESBaofWPIfhohw398fheIUFEWGF(W3fsdbOU#F(WFGEJDSBIUW#"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['APPLICATION_ROOT'] = '/'
app.config['MAX_COOKIE_SIZE'] = 8 * 1024


@login_manager.user_loader
def load_user(user_id):
    # print(Admin.query.get(int(user_id)))
    return User.query.get(int(user_id))


@app.route('/login', methods=['POST', 'GET'])
def LoginUser():
    if flask.request.method == 'POST':
        nick = flask.request.form['nick']
        password = flask.request.form['password']
        user = User.query.filter_by(username=nick).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return flask.redirect('/dashboard')
            else:
                return "В ДОСТУПЕ ОТКАЗАННО"
        else:
            return "В ДОСТУПЕ ОТКАЗАННО"

    return flask.render_template('user/login.html')


@app.route('/register', methods=['POST', 'GET'])
def RegUser():
    if flask.request.method == 'POST':
        session = db_session.create_session()
        nick = flask.request.form['nick']
        password = flask.request.form['password']
        user = User(nick=nick,
                    hashed_password=User.set_password(password),
                    is_team_lead=False)
        session.add(user)
        session.commit()
        session.close()
        return flask.redirect('/login')

    return flask.render_template('user/register.html')


@app.route('/')
@login_required
def test():
    return "hello"

@app.route('/add_subtask',  methods=['GET', 'POST'])
@login_required
def subtask_add():
    if flask.form.validate_on_submit():
        session = db_session.create_session()
        task = Task()
        task.team = flask.request.form['team']
        task.status = flask.request.form['status']
        task.description = flask.request.form['description']
        current_user.task(task)
        session.merge(current_user)
        session.commit()
        return flask.render_template('/dashboard')
    return flask.render_template('/dashboard')


@app.route('/add',  methods=['GET', 'POST'])
@login_required
def task_add():
    if flask.form.validate_on_submit():
        session = db_session.create_session()
        task = Task()
        task.team = flask.request.form['team']
        task.status = flask.request.form['status']
        task.description = flask.request.form['description']
        current_user.task(task)
        session.merge(current_user)
        session.commit()
        return flask.render_template('/dashboard')
    return flask.render_template('/dashboard')


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def task_delete(id):
    session = db_session.create_session()
    task = session.query(Task).filter(Task.id == id, Task.user_id == current_user.id).first()
    session.delete(task)
    session.commit()
    session.close()
    return flask.redirect('/dashboard')


@app.route('/commit/<int:id>', methods=['GET', 'POST'])
@login_required
def task_commit(id):
    session = db_session.create_session()
    task = session.query(Task).filter(Task.id == id, Task.user_id == current_user.id).first()
    task.status = True
    session.commit()
    session.close()
    return flask.redirect('/dashboard')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return flask.render_template('user/dashboard.html', data=data, usr=current_user)


@app.route('/api/forBot')
def apiBot():
    # статус
    # тим-лид(имя)
    # участники группы и номер группы
    # дата дедлайна
    pass

if __name__ == '__main__':
    db_session.global_init("db/task_manager.sqlite")
    app.run(debug=True)
    #app.run()
