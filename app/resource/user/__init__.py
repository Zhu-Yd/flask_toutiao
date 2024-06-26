from flask import Blueprint
from flask_restful import Api
from app.resource.user.Resource import TodoItem, CurrentUserProfileResource, SpecifyUserProfileResource, \
    UserFollowingsResource, UserUnFollowingsResource, UserFollowersResource
from utils.custom_error import custom_404_error

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')
api = Api(user_bp, catch_all_404s=True)

# 设置自定义的错误处理函数
api.handle_error = custom_404_error

# 注册资源
api.add_resource(TodoItem, '/todos/<regx("\d+"):id>')
api.add_resource(CurrentUserProfileResource, '/profile')
api.add_resource(SpecifyUserProfileResource, '/profile/<regx("\d+"):id>')
api.add_resource(UserFollowingsResource, '/followings')
api.add_resource(UserUnFollowingsResource, '/followings/<regx("\d+"):to_user_id>')
api.add_resource(UserFollowersResource, '/followers')
