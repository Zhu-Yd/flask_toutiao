from flask_restful import Resource
from flask import g
from utils.decorators import login_required

from app import db
from models.user import User, UserProfile, user2user
from models.article import Article, IsLike, Comment
from sqlalchemy import func


class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!"'}


class CurrentUserProfileResource(Resource):
    method_decorators = {'get': [login_required], 'post': [login_required]}

    def get(self):
        user, profile = db.session.query(User, UserProfile).outerjoin(UserProfile,
                                                                      User.id == UserProfile.userId).filter(
            User.id == g.userInfo.get('id')).first()
        userInfo = {**(user.to_dict()), **(profile.to_dict() if profile else {})}

        return {'message': '获取用户信息成功', 'status': 0, 'data': userInfo}

    def post(self, id):
        print(g.userInfo)
        return 'ok'


class SpecifyUserProfileResource(Resource):
    method_decorators = {'get': [login_required]}

    def get(self, id):
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
