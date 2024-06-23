import os
from flask_restful import Resource, inputs
import flask_restful
from flask import g
import werkzeug
from sqlalchemy import func
from sqlalchemy.orm import load_only
from flask_restful.reqparse import RequestParser

from utils.decorators import login_required
from app import db
from models.user import User, UserProfile, user2user
from models.article import Article, IsLike, Comment
from utils import validate_util, qiniu_storage


class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!"'}


class CurrentUserProfileResource(Resource):
    method_decorators = {'get': [login_required], 'patch': [login_required]}

    def get(self):
        """获取当前用户信息"""
        user, profile = db.session.query(User, UserProfile).outerjoin(UserProfile,
                                                                      User.id == UserProfile.user_id).filter(
            User.id == g.userInfo.get('id')).first()
        userInfo = {**(user.to_dict()), **(profile.to_dict() if profile else {})}

        return {'message': '获取用户信息成功', 'status': 200, 'data': userInfo}

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

        def upload(file, name):
            if file is not None:

                file.seek(0, os.SEEK_END)  # 将指针移动到文件末尾
                file_size = file.tell()  # 获取文件大小

                # 检查文件大小
                if file_size > 1048576:  # 1M = 1024 * 1024 字节
                    raise Exception(f"File size exceeds 1MB: {file_size} bytes")

                file.seek(0, os.SEEK_SET)  # 重置文件指针

                photo_url = qiniu_storage.uploadFile(file.read())
                args[name] = photo_url
            return

        try:
            photo = args['photo']
            upload(photo, 'photo')
            id_card_front = args['id_card_front']
            upload(id_card_front, 'id_card_front')
            id_card_back = args['id_card_back']
            upload(id_card_back, 'id_card_back')
            id_card_handheld = args['id_card_handheld']
            upload(id_card_handheld, 'id_card_handheld')
        except Exception as e:
            flask_restful.abort(500, message='THIRD_ERROR:{}'.format(e))
            # return {'status':500,'message': 'THIRD_ERROR:{}'.format(e)},500

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

        return {
            'status': 200, 'message': '更新信息成功',
        }


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

        res_dict = {'follow_count': follow_count, 'fans_count': fans_count, 'art_count': art_count,
                    'like_count': a_like_count + c_like_count}

        return {'status': 200, 'message': '获取指定用户信息成功', 'data': res_dict}


class UserFollowingsResource(Resource):
    method_decorators = {'get': [login_required], 'post': [login_required]}

    def get(self):
        """获取用户关注列表"""
        parser = RequestParser()
        parser.add_argument('page', type=int, location=['args'])
        parser.add_argument('per_page', type=int, location=['args'])
        args = parser.parse_args()
        res_dict = {}
        user_list = []
        if args['page'] and args['per_page']:
            paginate = db.session.query(User).options(load_only(User.id, User.name, User.photo)). \
                outerjoin(user2user, User.id == user2user.c.to_user_id).filter(
                user2user.c.from_user_id == g.userInfo.get('id')).paginate(args['page'], args['per_page'])
            users = paginate.items  # 获取当前页的用户列表
            res_dict['total_count'] = paginate.total  # 获取总记录数
        else:
            users = db.session.query(User).options(load_only(User.id, User.name, User.photo)). \
                outerjoin(user2user, User.id == user2user.c.to_user_id).filter(
                user2user.c.from_user_id == g.userInfo.get('id')).all()
            res_dict['total_count'] = len(users)
        for item in users:
            user_dict = {
                'id': item.id,
                'name': item.name,
                'photo': item.photo,
                'mutual_follow': False,
                'fans_count': 0
            }
            item_following = item.following  # item 关注的 用户
            for item_in in item_following:
                # 如果item关注的用户中有当前用户 则为 相互关注
                if item_in.id == g.userInfo.get('id'):
                    user_dict['mutual_follow'] = True
                    break

            item_followers = item.followers  # item 的 粉丝
            user_dict['fans_count'] = item_followers.count()  # item 的 粉丝数量

            user_list.append(user_dict)
        res_dict.update({'status': 200, 'message': '获取用户关注列表成功',
                         'data': {'page': args['page'], 'per_page': args['per_page'], 'results': user_list}})

        return res_dict

    def post(self):
        """关注用户"""
        parser = RequestParser()
        parser.add_argument('to_user_id', type=int, required=True, location=['form', 'json'])
        args = parser.parse_args()
        try:
            # 当前用户
            user = db.session.query(User).options(load_only(User.id)).filter(User.id == g.userInfo.get('id')).one()
            # 拟关注用户
            to_user = db.session.query(User).options(load_only(User.id)).filter(User.id == args['to_user_id']).one()
            # 关注
            user.following.append(to_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flask_restful.abort(500, message=str(e))
        return {'status': 200, 'message': '关注用户成功', 'data': {
            'target': args['to_user_id']
        }}


class UserFollowersResource(Resource):
    method_decorators = {'get': [login_required]}

    def get(self):
        """获取用户粉丝列表"""
        parser = RequestParser()
        parser.add_argument('per_page', type=int, location=['args'])
        parser.add_argument('page', type=int, location=['args'])
        args = parser.parse_args()
        res_dict = {}
        user_list = []
        if args['per_page'] and args['page']:
            paginate = db.session.query(User).options(load_only(User.id, User.name, User.photo)).outerjoin(user2user,
                                                                                                           User.id == user2user.c.from_user_id).filter(
                user2user.c.to_user_id == g.userInfo.get('id')).paginate(args['page'], args['per_page'])
            users = paginate.items
            res_dict['totle_count'] = paginate.total
        else:
            users = db.session.query(User).options(load_only(User.id, User.name, User.photo)).outerjoin(user2user,
                                                                                                        User.id == user2user.c.from_user_id).filter(
                user2user.c.to_user_id == g.userInfo.get('id')).all()
            res_dict['totle_count'] = len(users)
        for item in users:
            dict = {
                'id': item.id,
                'name': item.name,
                'photo': item.photo,
                'mutual_follow': False,
                'fans_count': 0
            }
            item_followers = item.followers  # 获取 item 粉丝
            # 判断 item 与 当前用户 是否相互关注
            for item_in in item_followers:
                dict['mutual_follow'] = True if item_in.id == g.userInfo.get('id') else False
                break
            dict['fans_count'] = item_followers.count()  # 获取 item 粉丝数量
            user_list.append(dict)
        res_dict.update({'status': 200, 'message': '获取用户粉丝列表成功',
                         'data': {'page': args['page'], 'per_page': args['per_page'], 'results': user_list}})
        return res_dict


class UserUnFollowingsResource(Resource):
    method_decorators = {'delete': [login_required]}

    def delete(self, to_user_id):
        """取消关注用户"""
        try:
            user = db.session.query(User).options(load_only(User.id)).filter(User.id == g.userInfo.get('id')).one()
            to_user = db.session.query(User).options(load_only(User.id)).filter(User.id == to_user_id).one()
            user.following.remove(to_user)
            db.session.commit()
        except Exception as e:
            flask_restful.abort(500, message=str(e))

        return {'status': 200, 'message': '取消关注用户成功'}
