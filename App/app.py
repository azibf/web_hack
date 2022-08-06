import flask
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from wtforms.validators import ValidationError
import random
from data import db_session

data = {
    'Person': {
        'name': 'Alexey Ovchinnikov',
        'work': "Programmer",
        'avatar': "../../static/admin/img/avatar-6.2821b67d.jpg"
    },
    'messages': {
        'all': 15,
        "new": 2,
        'msg': {
            1: {
                'from': "User 1",
                'text': "HELLO",
                'time': '12:15',
                'avatar': "../../static/admin/img/avatar-3.d23ced61.jpg",
                'status': "warning",
            },
            2: {
                'from': "User 2",
                'text': "HELLO ALLELLEO",
                'time': '12:25',
                'avatar': "../../static/admin/img/avatar-3.d23ced61.jpg",
                'status': "success",
            }
        }
    },
    "Tasks": {
        'all': 2,
        1: {
            'name': "Доделать админку",
            'percent': '34',
            'status': '3'
        },
        2: {
            'name': "Доделать бекенд",
            'percent': '10',
            'status': '1'
        }
    },
    'PageData': {
        'Users': {
            'purpose': 1000,
            'total': 666,
            'percent': (666 / 1000) * 100,
        },
        'NewUsers': {
            'purpose': 1000,
            'total': 14,
            'percent': (14 / 1000) * 100,
        },
        'NewPosts': {
            'purpose': 1000,
            'total': 89,
            'percent': (89 / 1000) * 100,
        },
        'Posts': {
            'purpose': 1000,
            'total': 798,
            'percent': (798 / 1000) * 100,
        },
        'Likes': {
            'all': {
                'up': True,
                "total": 2500
            },
            'today': {
                "up": True,
                'total': 333,
            }
        },
        'Comments': {
            'all': {
                'up': True,
                "total": 4534
            },
            'today': {
                "up": True,
                'total': 666,
            }
        },
        'Requests': {
            'total': 29834,
            "popular": {
                1: {
                    'name': 'Новости',
                    'total': 3445,
                },
                2: {
                    'name': 'Музыка',
                    'total': 632,
                }
            }
        },
        'Files': {
            'all': 9480,
            'today': 234,
            "size": str(435) + 'Mb',
        },
        'MostPopularUsers': {
            'count': 3,
            1: {
                'name': 'User 1',
                'id': "@user_1",
                'subscribes': 100,
                'likes': 300,
                'comments': 150,
                'posts': 10,
                'avatar': '../../static/admin/img/avatar-1.ce912d90.jpg'
            },
            2: {
                'name': 'User 2',
                'id': "@user_2",
                'subscribes': 80,
                'likes': 200,
                'comments': 140,
                'posts': 10,
                'avatar': '../../static/admin/img/avatar-1.ce912d90.jpg'
            },
            3: {
                'name': 'User 3',
                'id': "@user_3",
                'subscribes': 55,
                'likes': 100,
                'comments': 50,
                'posts': 4,
                'avatar': '../../static/admin/img/avatar-1.ce912d90.jpg'
            },
        }
    }
}

app = flask.Flask(__name__)
SQLAlchemyDB = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Login'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///static/databases/database.db'
app.config['SECRET_KEY'] = "IESBaofWPIfhohw398fheIUFEWGF(W3fsdbOU#F(WFGEJDSBIUW#"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['APPLICATION_ROOT'] = '/'
app.config['MAX_COOKIE_SIZE'] = 8 * 1024


def GenerateToken(lenght=50):
    sumbols = list("qwertyuiopasdfghjklzxcvbnm1234567890")
    token = ''
    for i in range(lenght):
        token += random.choice(sumbols)

    return token


class User(SQLAlchemyDB.Model, UserMixin):
    id = SQLAlchemyDB.Column(SQLAlchemyDB.Integer, primary_key=True)
    username = SQLAlchemyDB.Column(SQLAlchemyDB.String(20), nullable=False, unique=True)
    password = SQLAlchemyDB.Column(SQLAlchemyDB.String(80), nullable=False)
    admin = SQLAlchemyDB.Column(SQLAlchemyDB.Boolean, nullable=False, default=False)
    token = SQLAlchemyDB.Column(SQLAlchemyDB.String(255), nullable=False)

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


SQLAlchemyDB.create_all()


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
                return flask.redirect(f'/dashboard')
            else:
                return "В ДОСТУПЕ ОТКАЗАННО"
        else:
            return "В ДОСТУПЕ ОТКАЗАННО"

    return flask.render_template('user/login.html')


@app.route('/')
@login_required
def test():
    return "hello"


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return flask.render_template('user/dashboard.html', data=data, usr=current_user)


if __name__ == '__main__':
    db_session.global_init("db/task_manager.sqlite")
    #app.run(debug=True)
    app.run()
