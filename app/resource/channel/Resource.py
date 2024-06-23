from flask import g
from flask_restful import Resource
import flask_restful
from flask import request
from sqlalchemy import desc
from models.channel import Channel, User2Channel
from app import db
from utils.decorators import login_required


class ChannelsResource(Resource):
    method_decorators = {'put': [login_required]}

    def get(self):
        """获取用户频道信息"""
        flag = False
        if g.userInfo.get('id') is not None:
            user_channel_list = db.session.query(Channel.id, Channel.name, User2Channel.seq).outerjoin(User2Channel,
                                                                                                       Channel.id == User2Channel.channel_id).filter(
                User2Channel.user_id == g.userInfo.get('id')).order_by(User2Channel.seq, desc(Channel.id)).all()
            channel_list = [{'id': item.id, 'name': item.name, 'seq': item.seq} for item in user_channel_list]
            flag = len(channel_list) > 0
        if not flag:
            channel_list = [{'id': 7, 'name': '推荐', 'seq': 0}, {'id': 1, 'name': '新闻', 'seq': 1}, {
                'id': 2, 'name': '财经', 'seq': 2}, {'id': 3, 'name': '科技', 'seq': 3}]
        return {'status': 200,
                'message': '获取频道列表成功',
                'data': {'channels': channel_list}}

    def put(self):
        """更改用户频道信息"""
        json_data = request.get_json()
        # Step 1: Validate each item in the 'channels' list
        channels = json_data.get('channels')  # 自动转化成字典列表
        # print(channels)
        if not isinstance(channels, list):
            flask_restful.abort(400, message="'channels' must be a list")

        for channel in channels:
            if not isinstance(channel, dict):
                flask_restful.abort(400, message="Each item in 'channels' must be a dictionary")
            if 'id' not in channel or 'seq' not in channel:
                flask_restful.abort(400, message="Each channel dictionary must contain 'id' and 'seq' keys")

        # Step 2: Process the validated data
        try:

            user_id = g.userInfo.get('id')
            # 先删除用户的原始频道
            db.session.query(User2Channel).filter(User2Channel.user_id == user_id).delete()

            for channel in channels:
                channel_id = channel['id']
                seq = channel['seq']
                user_channel = User2Channel(user_id=user_id, channel_id=channel_id, seq=seq)
                db.session.add(user_channel)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flask_restful.abort(500, message=f"An error occurred: {str(e)}", error_type=type(e).__name__)

        return {'status': 200, 'message': '更改用户频道信息成功', 'data': {'channels': channels}}


class ChannelsAllResource(Resource):
    def get(self):
        """获取全部频道信息"""
        channels = db.session.query(Channel).order_by(Channel.id).all()
        return {
            "status": 200,
            "message": "获取全部频道信息成功",
            "data": {
                "channels": [{"id": channel.id, "name": channel.name} for channel in channels]
            }
        }
