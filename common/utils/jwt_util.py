import datetime

import jwt
from flask import current_app


def generate_jwt(payload, expiry=None, secret=None):
    """
    生成jwt
    :param payload: dict 载荷
    :param expiry: datetime 有效期 时间戳 默认10h
    :param secret: 密钥
    :return: jwt
    """
    _payload = {'exp': expiry if expiry else datetime.datetime.utcnow() + datetime.timedelta(hours=10)}
    _payload.update(payload)

    if not secret:
        secret = current_app.config['SECRET_KEY']

    token = jwt.encode(_payload, secret, algorithm='HS256')
    return token


def verify_jwt(token, secret=None):
    """
    检验jwt
    :param token: jwt
    :param secret: 密钥
    :return: dict: payload
    """
    if not secret:
        secret = current_app.config['SECRET_KEY']

    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.PyJWTError :
        payload = None

    return payload
