from flask import *
from flask_login import LoginManager
from flask_ngrok import run_with_ngrok
from database import db_session
from database.tables import *
import json

app = Flask(__name__)
run_with_ngrok(app)
login_manager = LoginManager()
login_manager.init_app(app)


def convert_to_json(inf_type, queue):
    """
    Функция для конвертации очереди из базы данных в формат json

    :param inf_type: тип информации в передаваемой очереди
    :param queue: сама очередь
    :return: json{*конвертированная очередь*}
    """
    inf = {}
    if inf_type == 'user':  # если на вход поступили пользователи
        for elem in queue:
            s = {'id': elem.id,
                 'name': elem.name,
                 'surname': elem.surname,
                 'patronymic': elem.patronymic,
                 'email': elem.email,
                 'phone': elem.phone,
                 'is_admin': elem.is_admin}
            s = json.dumps(s)
            inf[elem.id] = s
    elif inf_type == 'task':  # если на вход поступили задачи
        current_session = db_session.create_session()
        for elem in queue:
            user = current_session.query(User).filter(User.id == elem.user_id).first()
            s = {'id': elem.id,
                 'task_type': elem.task_type,
                 'user': f"{user.surname} {user.name[0]}. {user.patronymic[0]}.",
                 'is_finished': elem.is_finished,
                 'inf': elem.inf}
            s = json.dumps(s)
            inf[elem.id] = s
        current_session.close()
    else:  # если на вход поступил инвентарь
        for elem in queue:
            s = {'id': elem.id,
                 'name': elem.name,
                 'number': elem.number,
                 'place': elem.place}
            s = json.dumps(s)
            inf[elem.id] = s
    return json.dumps(inf)


@app.route('/save', methods=['GET', 'POST'])
def task_interacting_with_db():

    if request.method == 'POST':
        try:
            current_session = db_session.create_session()  # открываем соединение с БД
            task = Task(  # создаем объект задачи
                task_type=request.values.get('task_type'),
                user_id=request.values.get('user'),
                is_finished=False,
                inf=str(json.dumps(json.loads(request.values.get('inf')), ensure_ascii=False))
            )
            current_session.add(task)  # добавляем задачу в БД
            current_session.commit()
            current_session.close()  # закрываем соединение с БД
            return 'success'
        except Exception:
            return 'error'


@app.route('/task_admin', methods=['GET', 'POST'])
def task_admin():
    """
    Функция для отправки клиенту всей информации о задачах

    :return: json{*список задач*}
    """
    if request.method == 'GET':
        try:
            current_session = db_session.create_session()  # открываем соединение с БД
            task = current_session.query(Task).all()
            response = convert_to_json('task', task)  # конвертируем данные в json перед отправкой
            current_session.close()  # закрываем соединение с БД
            return jsonify(response)
        except:
            response = {'status': 'fail'}
            return jsonify(response)


@app.route('/user_admin', methods=['GET', 'POST'])
def user_admin():
    """
    Функция для отправки клиенту всей информации о пользователях

    :return: json{*список пользователей*}
    """
    if request.method == 'GET':
        try:
            current_session = db_session.create_session()  # открываем соединение с БД
            user = current_session.query(User).all()
            response = convert_to_json('user', user)  # конвертируем данные в json перед отправкой
            current_session.close()  # закрываем соединение с БД
            return jsonify(response)
        except:
            response = {'status': 'fail'}

            return jsonify(response)


@app.route('/equipment_admin', methods=['GET', 'POST'])
def equipment_admin():
    """
    Функция для отправки клиенту всей информации об инвентаре

    :return: json{*список инвентаря*}
    """
    if request.method == 'GET':
        try:
            current_session = db_session.create_session()  # открываем соединение с БД
            equipment = current_session.query(Equipment).all()
            print(equipment)
            current_session.close()  # закрываем соединение с БД
            response = convert_to_json('equipment', equipment)  # конвертируем данные в json перед отправкой
            return jsonify(response)
        except:
            response = {'status': 'fail'}
            return jsonify(response)


@app.route('/save_changes', methods=['POST'])
def save_changes():
    """
    Функция для обработки запроса на сохранение данных после работы администратора с ними

    :return: json{"status": *результат исполнения*}
    """
    if request.method == 'POST':
        try:
            current_session = db_session.create_session()  # открываем соединение с БД
            table = request.values.get('table')  # получаем название таблицы из запроса
            elem_id = request.values.get('id')
            value = True if request.values.get('value') == 'True' else False
            if table == 'users':  # если изменена таблица пользователей, присваиваем новые уровни доступа
                element = current_session.query(User).filter(User.id == elem_id).first()
                element.is_admin = value
            elif table == 'task':  # если изменена таблица задач, то сохраняем текущее состояние задачи
                element = current_session.query(Task).filter(Task.id == elem_id).first()
                element.is_finished = value
            else:  # обработка изменений в таблице инвентаря
                operation_type = request.values.get('type')
                if operation_type == 'delete':  # если тип изменения - удаление, убираем из БД соответствующий элемент
                    element = current_session.query(Equipment).filter(Equipment.id == elem_id).first()
                    current_session.delete(element)
                else:  # если тип изменения - постановка на учет, добавляем в БД новый элемент
                    element = Equipment(
                        name=request.values.get('name'),
                        number=request.values.get('number'),
                        place=request.values.get('place')
                    )
                    current_session.add(element)
            current_session.commit()
            current_session.close()
            # отправляем ответ на сторону клиента
            response = {'status': 'success'}
            return jsonify(response)
        except:
            response = {'status': 'fail'}
            return jsonify(response)


if __name__ == "__main__":
    db_session.global_init()
    #app.run(host='localhost', port=4567)
    app.run()
