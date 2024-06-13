import functools
from flask import g

# 需要登录 装饰器
def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not g.userInfo:
            return {"message": "token is not valid"}, 401
        else:
            return func(*args, **kwargs)

    return wrapper
