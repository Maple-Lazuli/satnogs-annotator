import json
import dataclasses
import datetime
from flask import Flask, request, Response
from flask_cors import CORS
import random
import hashlib

from account_interactions import AccountInteractions
from annotation_interactions import AnnotationInteractor
from observation_interactions import ObservationInteractor
from permission_interactions import PermissionInteractor
from role_interactions import RoleInteractor
from session_interactions import SessionInteractor
from task_interactions import TaskInteractor


app = Flask(__name__)
CORS(app)

account_actor = AccountInteractions()
annotation_actor = AnnotationInteractor()
observation_actor =  ObservationInteractor()
permission_actor =  PermissionInteractor()
role_actor = RoleInteractor()
session_actor = SessionInteractor()
task_actor = TaskInteractor()

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
    account = account_actor.get_account_by_username(username)
    account = sanitize_account(account)
    return Response(json.dumps(account, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/accounts', methods=['GET'])
def get_accounts():
    accounts = account_actor.get_accounts()
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

    role = role_actor.get_role_by_name(role_name)

    if role is None:
        role_actor.create_new_role(role_name=role_name)
        print("Created Role")

    role = role_actor.get_role_by_name(role_name)

    status = account_actor.create_account(role_id=role.role_id, first_name=first_name, last_name=last_name,
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

    current_user_account = account_actor.get_account_by_username(current_user)

    session = session_actor.get_session(session_code, current_user_account.account_id)

    if valid_session(session):
        new_password = create_hash(clear_text=password_not_hashed, salt=current_user_account.salt)
        account_actor.update_account(account_id=current_user_account.account_id, first_name=first_name,
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

    account = account_actor.get_account_by_username(username)

    if account is None:
        return Response(json.dumps({"code": "", "status": Status.AUTHENTICATION_FAILURE}), status=200,
                        mimetype='application/json')

    if account.log_in_attempts >= 15:
        account_actor.set_account_lock(account_id=account.account_id, locked=True)
        return Response(json.dumps({"code": "", "status": Status.ACCOUNT_LOCKED}), status=200,
                        mimetype='application/json')

    if account.locked:
        return Response(json.dumps({"code": "", "status": Status.ACCOUNT_LOCKED}, cls=JSONEncoder), status=200,
                        mimetype='text')

    if verify_hash(clear_text=password_not_hashed, salt=account.salt, stored_hash=account.password):
        code = session_actor.add_session(account_id=account.account_id)
        account_actor.reset_log_in_attempt(account_id=account.account_id)
        return Response(json.dumps({"code": code, "status": Status.SUCCESS, 'account_id': account.account_id}),
                        status=200, mimetype='text')
    else:
        account_actor.increment_log_in_attempt(account_id=account.account_id)
        return Response(json.dumps({"code": "", "status": Status.AUTHENTICATION_FAILURE}), status=200,
                        mimetype='application/json')


@app.route('/annotations', methods=['GET'])
def get_annotations():
    items = annotation_actor.get_annotations()
    return Response(json.dumps(items, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/annotationsMapped', methods=['GET'])
def get_annotations_mapped():
    annotations = annotation_actor.get_annotations()
    accounts = account_actor.get_accounts()

    for idx in range(len(annotations)):
        annotation = annotations[idx]
        # convert the username from the account id
        annotation.account_id = [a.user_name for a in accounts if a.account_id == annotation.account_id][0]
        annotations[idx] = annotation

    return Response(json.dumps(annotations, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/annotation', methods=['GET'])
def get_item():
    args = request.args
    annotation_id = args['annotation_id']
    annotation = annotation_actor.get_annotation(annotation_id=annotation_id)
    return Response(json.dumps(annotation, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/annotation', methods=['POST'])
def create_item():
    observation_id = request.json['observation_id']
    upper_left = request.json['upper_left']
    lower_right = request.json['lower_right']
    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = account_actor.get_account_by_username(current_user)
    session = session_actor.get_session(session_code, current_user_account.account_id)

    if valid_session(session):
        annotation_actor.add_annotation(account_id=current_user_account.account_id, observation_id=observation_id,
                            upper_left=upper_left, lower_right=lower_right)
        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')


@app.route('/annotation', methods=['PUT'])
def update_item():
    annotation_id = request.json['annotation_id']
    upper_left = request.json['upper_left']
    lower_right = request.json['lower_right']

    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = account_actor.get_account_by_username(current_user)
    session = session_actor.get_session(session_code, current_user_account.account_id)

    annotation = annotation_actor.get_annotation(annotation_id=annotation_id)
    if annotation.account_id != current_user_account.account_id:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')

    if valid_session(session):
        annotation_actor.update_annotation(annotation_id=annotation_id, upper_left=upper_left, lower_right=lower_right)
        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')


@app.route('/annotation', methods=['DELETE'])
def delete_item():
    annotation_id = request.json['annotation_id']
    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = account_actor.get_account_by_username(current_user)
    session = session_actor.get_session(session_code, current_user_account.account_id)

    annotation = annotation_actor.get_annotation(annotation_id=annotation_id)

    if annotation.account_id != current_user_account.account_id:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')

    if valid_session(session):
        annotation_actor.delete_annotation(annotation_id=annotation_id)
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
