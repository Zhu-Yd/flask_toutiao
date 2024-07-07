import functools
from flask import g
from app import db


# 需要登录 装饰器
def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not g.userInfo:
            return {"message": "token is not valid"}, 401
        else:
            return func(*args, **kwargs)

    return wrapper


# 设置db为写用数据库
def set_wirte_db(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: 设置写用数据库
        db.session().set_to_write()
        return func(*args, **kwargs)

    return wrapper


# 设置db为读用数据库
def set_read_db(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # TODO: 设置读用数据库
        db.session().set_to_read()
        return func(*args, **kwargs)

    return wrapper
