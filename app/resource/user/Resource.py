import time

from flask_restful import Resource, inputs
from flask import g
import werkzeug
from sqlalchemy import func
from flask_restful.reqparse import RequestParser

from utils.decorators import login_required
from app import db
from models.user import User, UserProfile, user2user
from models.article import Article, IsLike, Comment
from utils import validate_util


class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!"'}


class CurrentUserProfileResource(Resource):
    method_decorators = {'get': [login_required], 'post': [login_required]}

    def get(self):
        """获取当前用户信息"""
        user, profile = db.session.query(User, UserProfile).outerjoin(UserProfile,
                                                                      User.id == UserProfile.user_id).filter(
            User.id == g.userInfo.get('id')).first()
        userInfo = {**(user.to_dict()), **(profile.to_dict() if profile else {})}

        return {'message': '获取用户信息成功', 'status': 0, 'data': userInfo}

    def patch(self):
        """修改当前用户信息"""
        parser = RequestParser()
        parser.add_argument('name', type=inputs.regex(r'^[\u4e00-\u9fa5a-zA-Z]{1,7}$'), location=['json', 'form'])
        parser.add_argument('mobile', type=validate_util.mobile, location=['json', 'form'],
                            help='{error_msg}')
        parser.add_argument('gender', choices=('0', '1', '2'), location=['json', 'form'])
        parser.add_argument('birthday', type=inputs.regex(r'^\d{4}-\d{1,2}-\d{1,2}$'), location=['json', 'form'])
        parser.add_argument('photo', type=validate_util.image_file, location=['files'])
        parser.add_argument('id_card_front', type=werkzeug.datastructures.FileStorage, location=['files'])
        parser.add_argument('id_card_back', type=werkzeug.datastructures.FileStorage, location=['files'])
        parser.add_argument('id_card_handheld', type=werkzeug.datastructures.FileStorage, location=['files'])
        parser.add_argument('real_name', type=inputs.regex(r'^[\u4e00-\u9fa5a-zA-Z]{1,20}$'), location=['json', 'form'])
        parser.add_argument('id_number', type=inputs.regex(r'^\d{17}(\d|x|X)$'), location=['json', 'form'])
        parser.add_argument('intro', location=['json', 'form'])
        args = parser.parse_args()
        photo = args['photo']

        args = {key: value for key, value in args.items() if value}  # 生成动态更新字典
        # 查询当前用户的信息和附加信息(select for update 锁定)
        user, user_profile = db.session.query(User, UserProfile).outerjoin(UserProfile,
                                                                           User.id == UserProfile.user_id).filter(
            User.id == g.userInfo.get('id')).with_for_update().one()
        # 如果没有附加信息则创建
        if user_profile is None:
            user_profile = UserProfile(user_id=user.id)
            db.session.add(user_profile)
        # 根据动态更新字典更新用户信息和用户附加信息
        user_profile.update_from_dict(args)
        user.update_from_dict(args)

        # 提交事务
        db.session.commit()

        return 'ok'


class SpecifyUserProfileResource(Resource):
    method_decorators = {'get': [login_required]}

    def get(self, id):
        """获取指定用户相关数据"""
        user = db.session.query(User).filter(User.id == id).first()
        # 方式一:使用orm查询指定账号关注的用户数量
        # follow_count=user.following.count()

        # 方式二:使用连接查询多对多关系,查询指定账号关注的用户数量(可获取用户的详细信息)
        # follow_count = db.session.query(User.name).join(user2user, User.id == user2user.c.to_user_id).filter(
        #     user2user.c.from_user_id == id).count()

        # 方式三:直接查找多对多关系表，获取指定账号粉丝数量（效率最高，其他两种方式都用的是嵌套查询）
        follow_count = db.session.query(func.count(1)).filter(user2user.c.from_user_id == id).scalar()

        # 用户粉丝数量
        fans_count = db.session.query(func.count(1)).filter(user2user.c.to_user_id == id).scalar()

        # 用户发表文章数量
        art_count = len(user.articles)

        # 用户发表文章点赞数
        a_like_count = db.session.query(func.count(IsLike.user_id)). \
            join(Article, IsLike.like_id == Article.id).filter(
            Article.auth_id == id, IsLike.like_type == IsLike.LikeType.ARTICLE).scalar()

        # 用户发表文章点赞数
        c_like_count = db.session.query(func.count(IsLike.user_id)). \
            join(Comment, IsLike.like_id == Comment.id).filter(
            Comment.user_id == id, IsLike.like_type == IsLike.LikeType.COMMENT).scalar()

        res_dict = {'follow_count': follow_count, 'fan_count': fans_count, 'art_count': art_count,
                    'like_count': a_like_count + c_like_count}

        return {'status': 0, 'message': '获取指定用户信息成功', 'data': res_dict}
