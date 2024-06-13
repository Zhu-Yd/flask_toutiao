from flask import request, g
from utils.jwt_util import verify_jwt


# 鉴权中间件
def auth_jwt_token():
    g.userInfo = {}
    # 从请求头信息中获取token
    auth_token = request.headers.get('Authorization')
    if auth_token:
        # 验证jwt_token
        payload = verify_jwt(auth_token)
        # 如果payload不为空，将其写入g对象
        if payload is not None:
            g.userInfo.update(payload)
