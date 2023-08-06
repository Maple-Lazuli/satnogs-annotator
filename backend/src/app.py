import json
import dataclasses
import datetime
import os.path

from flask import Flask, request, Response, send_file
from flask_cors import CORS
import random
import hashlib
import tempfile
import numpy as np
from matplotlib import cm
from PIL import Image

from account_interactions import AccountInteractor
from annotation_interactions import AnnotationInteractor
from observation_interactions import ObservationInteractor
from permission_interactions import PermissionInteractor
from role_interactions import RoleInteractor
from session_interactions import SessionInteractor
from task_interactions import TaskInteractor
import satnogs_interactions as si
import tarfile

app = Flask(__name__)
CORS(app)

account_actor = AccountInteractor()
annotation_actor = AnnotationInteractor()
observation_actor = ObservationInteractor()
permission_actor = PermissionInteractor()
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
    MISSING = 5


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


def verify_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


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


def get_image_from_bytes(bytes, shape, save_dir, color_map="", save_name=None):
    if save_name is None:
        save_name = create_hash(str(datetime.datetime.now()), random.randint(1, 1000000))
    bytes_name = os.path.join(save_dir, save_name+".dat")
    with open(bytes_name, "wb") as file_out:
        file_out.write(bytes)

    spectrogram = np.fromfile(bytes_name, dtype=np.uint8).reshape(shape[0], shape[1])

    if color_map == "viridis":
        im = Image.fromarray(np.uint8(cm.viridis(spectrogram) * 255)).convert("RGB")
    elif color_map == "threshold":
        im = Image.fromarray(np.uint8(cm.viridis(spectrogram) * 255)).convert("RGB")
    else:
        im = Image.fromarray(spectrogram * 255).convert('L').convert("RGB")

    save_name = os.path.join(save_dir, save_name) + ".jpg"

    im.save(save_name)

    return save_name


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
    items = AnnotationInteractor().get_annotations()
    return Response(json.dumps(items, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/annotationsMapped', methods=['GET'])
def get_annotations_mapped():
    annotations = AnnotationInteractor().get_annotations()
    accounts = account_actor.get_accounts()

    for idx in range(len(annotations)):
        annotation = annotations[idx]
        # convert the username from the account id
        annotation.account_id = [a.user_name for a in accounts if a.account_id == annotation.account_id][0]
        annotations[idx] = annotation

    return Response(json.dumps(annotations, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/annotationsByUsername', methods=['GET'])
def get_annotation_by_username():
    args = request.args
    username = args['username']
    account = account_actor.get_account_by_username(user_name=username)
    annotations = AnnotationInteractor().get_annotations_by_account_id(account_id=account.account_id)
    return Response(json.dumps(annotations, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/annotationsBySatnogsID', methods=['GET'])
def get_annotation_by_satnogs():
    args = request.args
    satnogs_id = args['satnogs_id']
    observation = ObservationInteractor().get_observation_by_satnogs_id(satnogs_id)
    annotations = AnnotationInteractor().get_annotations_by_observation_id(observation_id=observation.observation_id)
    return Response(json.dumps(annotations, cls=JSONEncoder), status=200, mimetype='application/json')


@app.route('/annotation', methods=['POST'])
def create_item():
    satnogs_id = request.json['observation_id']
    x0 = request.json['x0']
    y0 = request.json['y0']
    x1 = request.json['x1']
    y1 = request.json['y1']
    image_width = request.json['image_width']
    image_height = request.json['image_height']
    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]
    current_user_account = account_actor.get_account_by_username(current_user)
    session = session_actor.get_session(session_code, current_user_account.account_id)

    if valid_session(session):
        observation = ObservationInteractor().get_observation_by_satnogs_id(satnogs_id)
        AnnotationInteractor().add_annotation(account_id=current_user_account.account_id,
                                              observation_id=observation.observation_id,
                                              x0=x0, y0=y0, x1=x1, y1=y1, image_height=image_height,
                                              image_width=image_width)
        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')


@app.route('/annotation', methods=['PUT'])
def update_annotation():
    annotation_id = request.json['annotation_id']
    x0 = request.json['x0']
    y0 = request.json['y0']
    x1 = request.json['x1']
    y1 = request.json['y1']
    image_width = request.json['image_width']
    image_height = request.json['image_height']
    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = account_actor.get_account_by_username(current_user)
    session = session_actor.get_session(session_code, current_user_account.account_id)

    annotation = AnnotationInteractor().get_annotation(annotation_id=annotation_id)
    if annotation.account_id != current_user_account.account_id:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')

    if valid_session(session):
        AnnotationInteractor().update_annotation(annotation_id=annotation_id, x0=x0, y0=y0, x1=x1, y1=y1,
                                                 image_height=image_height, image_width=image_width)
        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')


@app.route('/annotation', methods=['DELETE'])
def delete_annotation():
    annotation_id = request.args['annotation_id']
    session_code = request.headers.get('Authorization').split(" ")[1]
    current_user = request.headers.get('Authorization').split(" ")[0]

    current_user_account = account_actor.get_account_by_username(current_user)
    session = session_actor.get_session(session_code, current_user_account.account_id)

    annotation = AnnotationInteractor().get_annotation(annotation_id=annotation_id)

    if annotation.account_id != current_user_account.account_id:
        return Response(json.dumps({"status": Status.PERMISSION_DENIED}), status=200, mimetype='application/json')

    if valid_session(session):
        AnnotationInteractor().delete_annotation(annotation_id=annotation_id)
        return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.AUTHENTICATION_FAILURE}), status=200, mimetype='application/json')


@app.route('/pullSatnogs', methods=['POST'])
def pull_satnogs():
    satnogs_id = request.json['satnogs_id']
    ObservationInteractor().add_observation(*si.fetch_satnogs(satnogs_id))
    return Response(json.dumps({"status": Status.SUCCESS}), status=200, mimetype='application/json')


@app.route('/observation', methods=['GET'])
def get_observation():
    args = request.args
    satnogs_id = args['satnogs_id']
    observation = ObservationInteractor().get_observation_by_satnogs_id(satnogs_id=satnogs_id)

    if observation is not None:
        rtn_dict = {
            'satnogs_id': observation.satnogs_id,
            'status': Status.SUCCESS,
            'width': observation.waterfall_width,
            'length': observation.waterfall_length
        }
        return Response(json.dumps(rtn_dict), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"status": Status.MISSING}), status=200, mimetype='application/json')


@app.route('/observations', methods=['GET'])
def get_observations():
    observations = ObservationInteractor().get_observations()
    for idx in range(len(observations)):
        observation = observations[idx]
        observation.greyscale_waterfall = None
        observation.threshold_waterfall = None
        observation.original_waterfall = None
    return Response(json.dumps(observations, cls=JSONEncoder), status=200, mimetype='application/json')



@app.route("/images", methods=["GET"])
def get_image():
    temp_dir = "./temp"
    verify_directory(temp_dir)

    satnogs_id = request.args.get('satnogs_id')
    image_type = request.args.get('type').strip()
    observation = ObservationInteractor().get_observation_by_satnogs_id(satnogs_id)

    if observation is None:
        return send_file("missing.png", mimetype='image/png')

    elif image_type == 'origional':
        image_name = get_image_from_bytes(observation.greyscale_waterfall, (observation.waterfall_length,
                                                                            observation.waterfall_width),
                                          temp_dir, color_map="viridis")
        return send_file(image_name, mimetype='image/png')

    elif image_type == 'greyscale':
        image_name = get_image_from_bytes(observation.greyscale_waterfall, (observation.waterfall_length,
                                                                            observation.waterfall_width),
                                          temp_dir)
        return send_file(image_name, mimetype='image/png')

    elif image_type == 'threshold':
        image_name = get_image_from_bytes(observation.threshold_waterfall, (observation.waterfall_length,
                                                                            observation.waterfall_width),
                                          temp_dir, color_map="thshold")
        return send_file(image_name, mimetype='image/png')

    return send_file("missing.png", mimetype='image/png')


@app.route('/')
def home():
    return Response("Operational", status=200, mimetype='application/json')


@app.route("/export", methods=["GET"])
def export():
    temp_dir = "./temp"
    obervations = ObservationInteractor().get_observations()
    observations_with_annotations = [observation for observation in obervations
                                     if len(AnnotationInteractor().get_annotations_by_observation_id(
            observation.observation_id)) > 0]

    files = []
    for observation in observations_with_annotations:
        # create basename
        basename = create_hash(str(datetime.datetime.now()), random.randint(1, 100000))
        #  add the image to the list of files
        files.append(get_image_from_bytes(observation.greyscale_waterfall, (1500,
                                                                            600),
                                          temp_dir, basename))
        # get the annotations for that observation
        annotations = AnnotationInteractor().get_annotations_by_observation_id(observation.observation_id)
        # save the obsersavation annotations to the disk
        json_name = os.path.join(temp_dir, f"{basename}.json")
        with open(json_name, 'w') as file_out:
            json.dump(annotations, file_out, cls=JSONEncoder)
        files.append(json_name)
    t_file = tarfile.open(os.path.join(temp_dir, "export.tar"), "w")
    for file in files:
        t_file.add(file)
    t_file.close()

    return send_file(os.path.join(temp_dir, "export.tar"), mimetype='application/x-tar')


def main():
    app.run(host='0.0.0.0', port=5001, debug=True)
    print("running")


if __name__ == "__main__":
    main()
