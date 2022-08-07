import flask
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from ML_model import rfc
from wtforms.validators import ValidationError
import random
from data import db_session
from data.users import *



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
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['POST', 'GET'])
def LoginUser():
    if flask.request.method == 'POST':
        session = db_session.create_session()
        nick = flask.request.form['nick']
        password = flask.request.form['password']
        user = session.query(User).filter(User.nick == nick).first()
        if user:
            if user.check_password(password):
                login_user(user)
                tasks = session.query(Task).filter(Task.user == user).all()
                if not user.is_team_lead:
                    return flask.redirect('/dashboard')
                else:
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
        user = User()
        user.nick = flask.request.form['nick']
        user.name = flask.request.form['name']
        user.surname = flask.request.form['surname']
        user.set_password(flask.request.form['password'])
        user.is_team_lead = 1 if 'is_team_lead' in str(flask.request.values) else 0
        user.specialization = flask.request.form['specialization']
        user.telegram = flask.request.form['telegram']
        session.add(user)
        session.commit()
        if user.is_team_lead:
            users = session.query(User).filter(not User.is_team_lead).all()
            for elem in users:
                match = Team_Match()
                match.user_id = elem.id
                match.team_lead_id = user.id
                match.par1, match.par2, match.par3 = 0.5, 0.5, 1500
                session.add(match)
                session.commit()
        else:
            users = session.query(User).filter(User.is_team_lead).all()
            for elem in users:
                match = Team_Match()
                match.team_lead_id = elem.id
                match.user_id = user.id
                match.par1, match.par2, match.par3 = 0.5, 0.5, 1500
                session.add(match)
                session.commit()
        session.close()
        return flask.redirect('/login')
    return flask.render_template('user/register.html')


@app.route('/')
@login_required
def test():
    return "hello"


@app.route('/create_task',  methods=['GET', 'POST'])
@login_required
def task_add():
    session = db_session.create_session()
    if flask.request.method == 'POST':
        #session = db_session.create_session()
        task = Task()
        task.team = flask.request.form['team']
        task.status = flask.request.form['status']
        task.description = flask.request.form['description']
        current_user.task(task)
        session.merge(current_user)
    users = []
    for user in session.query(User).all():
        match = session.query(Team_Match).filter(Team_Match.team_lead_id == current_user.id).filter(Team_Match.user_id == user.id).first()
        users.append(tuple(user, rfc.predict([match.par1, match.par2, match.par3])))
    session.commit()
    return flask.render_template('user/create_task.html', users=users)



@app.route('/users_tasks',  methods=['GET', 'POST'])
@login_required
def merge_users_with_tasks():
    session = db_session.create_session()
    if flask.request.method == 'POST':
        #session = db_session.create_session()
        task = Task()
        task.team = flask.request.form['team']
        task.status = flask.request.form['status']
        task.description = flask.request.form['description']
        current_user.task(task)
        session.merge(current_user)
    users = []
    for user in session.query(User).all():
        match = session.query(Team_Match).filter(Team_Match.team_lead_id == current_user.id).filter(Team_Match.user_id == user.id).first()
        users.append(tuple(user, rfc.predict([match.par1, match.par2, match.par3])))
    session.commit()
    return flask.render_template('user/create_task.html', users=users)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def task_delete(id):
    session = db_session.create_session()
    task = session.query(Task).filter(Task.id == id, Task.user_id == current_user.id).first()
    session.delete(task)
    session.commit()
    session.close()
    return flask.redirect('/dashboard')


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def board_delete(id):
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
    session = db_session.create_session()
    users = session.query(User).all()
    if flask.request.method == 'POST':
        if not current_user.is_team_lead:
            title = flask.request.form['nick']
            key = flask.request.form['password']
            print(f"TITLE:{title}")
            print(f"KEY:{key}")
            board = session.query(Dashboard).filter(Dashboard.title == title).first()
            tasks = session.query(Task).filter(Task.user_id == current_user.id).all()
            if board:
                if board.key == key:
                    return flask.render_template('user/dashboard.html', data=tasks, user=current_user, auth=True)
                else:
                    return "В ДОСТУПЕ ОТКАЗАННО"
            else:
                return "В ДОСТУПЕ ОТКАЗАННО"
        else:
            board = Dashboard()
            title = flask.request.form['title']
            key = flask.request.form['key']
            current_user.merge(board)
            session.commit()
    users = [] if not current_user.is_team_lead else users
    return flask.render_template('user/dashboard.html', data=[], user=current_user, users=users)


@app.route('/team_lead_dashboard', methods=['GET', 'POST'])
@login_required
def team_lead_dashboard():
    session = db_session.create_session()
    tasks = session.query(Task).filter(Task.user == current_user).all()
    session.close()
    print(tasks)
    return flask.render_template('user/team_lead_dashboard.html', data=tasks, user=current_user)


if __name__ == '__main__':
    db_session.global_init("db/task_manager.sqlite")
    app.run()
