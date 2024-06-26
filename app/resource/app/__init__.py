from flask import Blueprint
from flask_restful import Api
from app.resource.app.Resource import LoginResource
from utils.custom_error import custom_404_error

app_bp = Blueprint('app_bp', __name__, url_prefix='/app')
api = Api(app_bp, catch_all_404s=True)

# 设置自定义的错误处理函数
api.handle_error = custom_404_error

# 注册资源
api.add_resource(LoginResource, '/login')
