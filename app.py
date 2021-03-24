import threading
from functools import wraps
from flask import request, Response, jsonify, Flask

from config import Verdict
from handler import judge_handler
from handler import reject_with_traceback, cache

flask_app = Flask(__name__)


@flask_app.route('/ping')
def ping():
    return Response("pong22")


def check_auth(username, password):
    return username == 'qust_judge' and password == 'naive'


def authorization_failed():
    return jsonify({'status': 'reject', 'message': 'authorization failed'})


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authorization_failed()
        return f(*args, **kwargs)

    return decorated


def response_ok(**kwargs):
    kwargs.update(status='received')
    return jsonify(kwargs)


def with_traceback_on_err(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            return jsonify(reject_with_traceback())

    return decorated


@flask_app.route('/judge', methods=['POST'])
@auth_required
@with_traceback_on_err
def judge():
    data = request.get_json()
    print(data)
    fingerprint = data['fingerprint']
    cache.set(fingerprint, {'verdict': Verdict.WAITING.value}, timeout=3600)
    args = (fingerprint, data['code'], data['checker'], data['cases'], data['table'], data['problem_type'])
    threading.Thread(target=judge_handler, args=args).start()
    return response_ok()


@flask_app.route('/query', methods=['GET'])
@auth_required
@with_traceback_on_err
def query():
    data = request.get_json()
    fingerprint = data['fingerprint']
    status = cache.get(fingerprint)
    status.setdefault('status', 'received')
    print(status)
    return jsonify(status)


if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5000)
