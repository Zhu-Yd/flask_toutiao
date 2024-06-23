from flask import Blueprint
from flask_restful import Api
from app.resource.channel.Resource import ChannelsResource, ChannelsAllResource
from utils.custom_error import custom_404_error

channel_bp = Blueprint('channel_bp', __name__, url_prefix='/channel')
api = Api(channel_bp, catch_all_404s=True)

# 设置自定义的 404 错误处理函数
api.handle_error = custom_404_error

# 注册资源
api.add_resource(ChannelsResource, '/channels')
api.add_resource(ChannelsAllResource, '/getAllChannels')

