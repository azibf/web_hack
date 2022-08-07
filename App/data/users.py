import datetime
import sqlalchemy
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase
from . import db_session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from wtforms.validators import ValidationError


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    nick = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    is_team_lead = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    telegram = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    specialization = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_hours = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    task = orm.relation("Task", back_populates='user')
    team = orm.relation("Team", back_populates='team_lead')
    dashboard = orm.relation("Dashboard", back_populates='owner')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class Task(SqlAlchemyBase, UserMixin):
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    team = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    deadline = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    subtask = orm.relation("Subtask", back_populates='task')


class Subtask(SqlAlchemyBase, UserMixin):
    __tablename__ = 'subtasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"))
    task = orm.relation('Task')


class Team(SqlAlchemyBase, UserMixin):
    __tablename__ = 'teams'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    team_lead_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    team_lead = orm.relation('User')


class Dashboard(SqlAlchemyBase, UserMixin):
    __tablename__ = 'dashboards'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    key = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    owner = orm.relation('User')


class Team_Match(SqlAlchemyBase, UserMixin):
    __tablename__ = 'team_match'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    team_lead_id = sqlalchemy.Column(sqlalchemy.Integer)
    par1 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    par2 = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    par3 = sqlalchemy.Column(sqlalchemy.String, nullable=True)



