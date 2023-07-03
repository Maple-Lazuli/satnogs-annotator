import json
import dataclasses
import datetime
from flask import Flask, request, Response
from flask_cors import CORS
import random
import hashlib

from db_interactions import DBInteractions

app = Flask(__name__)
CORS(app)
interactor = DBInteractions()

from enum import Enum


class Status(int, Enum):
    SUCCESS = 0
    USERNAME_TAKEN = 1
    ACCOUNT_LOCKED = 2
    AUTHENTICATION_FAILURE = 3
    PERMISSION_DENIED = 4


class JSONEncoder(json.JSONEncoder):
    def default(self, object):
        if dataclasses.is_dataclass(object):
            data_dict = dataclasses.asdict(object)
            for key in data_dict.keys():
                if isinstance(data_dict[key], datetime.date):
                    data_dict[key] = str(data_dict[key])
            return data_dict
        return super().default(object)


def create_hash(clear_text, salt):
    hasher = hashlib.sha512()
    hasher.update(f"{clear_text}-{salt}".encode())
    return hasher.hexdigest()


def verify_hash(clear_text, salt, stored_hash):
    generated_hash = create_hash(clear_text, salt)

    return generated_hash == stored_hash


def valid_session(session):
    if session is None:
        return False
    if session.end_date < datetime.datetime.now():
        return False
    return True


def sanitize_account(account):
    account.salt = 0
    account.locked = "Unknown"
    account.log_in_attempts = 0
    account.first_name = "Sanitized"
    account.last_name = "Sanitized"
    return account


@app.route('/account', methods=['GET'])
def get_account():
    args = request.args
    username = args['username']
    account = interactor.get_account_by_username(username)
    account = sanitize_account(account)
    return Response(json.dumps(account, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/accounts', methods=['GET'])
def get_accounts():
    accounts = interactor.get_accounts()
    accounts = [sanitize_account(a) for a in accounts]
    return Response(json.dumps(accounts, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/account', methods=['POST'])
def create_account():
    role_name = request.json['role_name']
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    username = request.json['username'].strip().replace(" ", "")

    password_not_hashed = request.json['password']
    salt = random.randint(1, 100000)

    password = create_hash(password_not_hashed, salt)

    role = interactor.get_role_by_name(role_name)

    if role is None:
        interactor.create_new_role(role_name=role_name)
        print("Created Role")

    role = interactor.get_role_by_name(role_name)

    status = interactor.create_account(role_id=role.role_id, first_name=first_name, last_name=last_name,
                                       user_name=username, password=password, salt=salt)

    return Response(json.dumps({'created': status}), status=200, mimetype='application/json')


@app.route('/account', methods=['PUT'])
def update_account():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    username = request.json['username']
    password_not_hashed = request.json['password']

    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = interactor.get_account_by_username(current_user)

    session = interactor.get_session(session_code, current_user_account.account_id)

    if valid_session(session):
        new_password = create_hash(clear_text=password_not_hashed, salt=current_user_account.salt)
        interactor.update_account(account_id=current_user_account.account_id, first_name=first_name,
                                  last_name=last_name, user_name=username, password=new_password)

        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')

    else:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')


@app.route('/account', methods=['DELETE'])
def delete_account():
    pass


@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password_not_hashed = request.json['password']

    account = interactor.get_account_by_username(username)

    if account is None:
        return Response(json.dumps({"code": "", "status": Status.AUTHENTICATION_FAILURE}), status=200,
                        mimetype='application/json')

    if account.log_in_attempts >= 15:
        interactor.set_account_lock(account_id=account.account_id, locked=True)
        return Response(json.dumps({"code": "", "status": Status.ACCOUNT_LOCKED}), status=200,
                        mimetype='application/json')

    if account.locked:
        return Response(json.dumps({"code": "", "status": Status.ACCOUNT_LOCKED}, cls=JSONEncoder), status=200,
                        mimetype='text')

    if verify_hash(clear_text=password_not_hashed, salt=account.salt, stored_hash=account.password):
        code = interactor.add_session(account_id=account.account_id)
        interactor.reset_log_in_attempt(account_id=account.account_id)
        return Response(json.dumps({"code": code, "status": Status.SUCCESS, 'account_id': account.account_id}),
                        status=200, mimetype='text')
    else:
        interactor.increment_log_in_attempt(account_id=account.account_id)
        return Response(json.dumps({"code": "", "status": Status.AUTHENTICATION_FAILURE}), status=200,
                        mimetype='application/json')


@app.route('/items', methods=['GET'])
def get_items():
    items = interactor.get_items()
    return Response(json.dumps(items, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/itemsMapped', methods=['GET'])
def get_items_mapped():
    items = interactor.get_items()
    accounts = interactor.get_accounts()

    for idx in range(len(items)):
        item = items[idx]
        item.account_id = [a.user_name for a in accounts if a.account_id == item.account_id][0]
        items[idx] = item

    return Response(json.dumps(items, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/item', methods=['GET'])
def get_item():
    args = request.args
    item_id = args['item_id']
    item = interactor.get_item(item_id=item_id)
    return Response(json.dumps(item, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/item', methods=['POST'])
def create_item():
    name = request.json['name']
    description = request.json['description']
    quantity = request.json['quantity']
    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = interactor.get_account_by_username(current_user)
    session = interactor.get_session(session_code, current_user_account.account_id)

    if valid_session(session):
        interactor.add_item(account_id=current_user_account.account_id, name=name,
                            description=description, quantity=quantity)
        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')


@app.route('/item', methods=['PUT'])
def update_item():
    item_id = request.json['item_id']
    name = request.json['name']
    description = request.json['description']
    quantity = request.json['quantity']

    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = interactor.get_account_by_username(current_user)
    session = interactor.get_session(session_code, current_user_account.account_id)

    item = interactor.get_item(item_id=item_id)
    if item.account_id != current_user_account.account_id:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')

    if valid_session(session):
        interactor.update_item(item_id=item_id, name=name, description=description, quantity=quantity)
        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')


@app.route('/item', methods=['DELETE'])
def delete_item():
    item_id = request.args['item_id']
    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = interactor.get_account_by_username(current_user)
    session = interactor.get_session(session_code, current_user_account.account_id)

    item = interactor.get_item(item_id=item_id)

    if item.account_id != current_user_account.account_id:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')

    if valid_session(session):
        interactor.delete_item(item_id=item_id)
        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.AUTHENTICATION_FAILURE}), status=200, mimetype='application/json')


@app.route('/')
def home():
    return Response("Operational", status=200, mimetype='application/json')


def main():
    app.run(host='0.0.0.0', port=5001, debug=True)
    print("running")


if __name__ == "__main__":
    main()
