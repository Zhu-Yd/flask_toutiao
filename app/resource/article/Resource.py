from flask_restful import Resource
import flask_restful
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only
from sqlalchemy import func, desc
from utils.decorators import login_required, set_read_db
from flask import g
from models.article import Article, user2article, IsLike, Comment
from models.user import User, user2user
from app import db
from utils import validate_util


class CollectionsResource(Resource):
    method_decorators = {'get': [login_required, set_read_db], 'post': [login_required]}

    def get(self):
        """获取当前用户收藏文章列表"""
        parser = RequestParser()
        parser.add_argument('page', type=int, default=1, location=['args'])
        parser.add_argument('per_page', type=int, default=2, location=['args'])
        args = parser.parse_args()
        data_dict = {}
        article_list = []

        paginate = db.session.query(Article).join(user2article, Article.id == user2article.c.article_id).filter(
            user2article.c.user_id == g.userInfo.get('id')).paginate(args['page'], args['per_page'])
        user_articles = paginate.items  # type:list[Article]
        data_dict['total_count'] = paginate.total
        data_dict['page'] = args['page']
        data_dict['per_page'] = args['per_page']
        for item in user_articles:
            article_dict = {
                'art_id': item.id,  # 文章ID
                'title': item.title,  # 文章标题
                'auth_id': item.auth_id,  # 作者ID
                'pubdate': item.pubdate.isoformat(),  # 发布时间
            }
            auth = db.session.query(User).options(load_only(User.name)).filter(
                User.id == item.auth_id).one()  # type:User
            article_dict['name'] = auth.name  # 作者名称
            article_dict['comm_count'] = len(item.comments)  # 评论数量
            isLike_count = db.session.query(func.count(1)).filter(IsLike.like_id == item.id,
                                                                  IsLike.like_type == IsLike.LikeType.ARTICLE).scalar()
            article_dict['like_count'] = isLike_count  # 点赞数量
            article_dict['collect_count'] = len(item.users)  # 收藏数量
            isLiking = db.session.query(func.count(1)).filter(IsLike.like_id == item.id,
                                                              IsLike.like_type == IsLike.LikeType.ARTICLE,
                                                              IsLike.user_id == g.userInfo.get('id')).scalar()
            article_dict['is_liking'] = isLiking  # 当前用户是否收藏该文章

            img_dict = {
                'type': 0,
                'images': []
            }
            if not item.cover_1:
                pass
            elif item.cover_3:
                img_dict['type'] = 3
                img_dict['images'] = [item.cover_1, item.cover_2, item.cover_3]
            else:
                img_dict['type'] = 1
                img_dict['images'] = [item.cover_1]
            article_dict['cover'] = img_dict  # 文章封面
            article_list.append(article_dict)
            data_dict.update({'status': 200, 'message': '获取用户收藏文章列表成功', 'data': article_list})
        return data_dict

    def post(self):
        """收藏|取消收藏"""
        parser = RequestParser()
        parser.add_argument('type', type=int, choices=(0, 1), required=True, location=['form', 'json'])
        parser.add_argument('target', type=int, required=True, location=['form', 'json'])
        args = parser.parse_args()
        try:
            target_articles = db.session.query(Article).options(load_only(Article.id)).filter(
                Article.id == args['target']).one()
            user = db.session.query(User).options(load_only(User.id)).filter(User.id == g.userInfo.get('id')).one()
            if args['type'] == 0:
                user.collect_articles.remove(target_articles)
                message = '取消收藏文章成功'
            if args['type'] == 1:
                user.collect_articles.append(target_articles)
                message = '收藏文章成功'

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flask_restful.abort(500, message=str(e))
        return {'status': 200, 'message': message, 'data': {'target': args['target']}}


class LikingsResource(Resource):
    method_decorators = {'post': [login_required]}

    def post(self):
        """点赞|取消点赞 (文章&评论)"""
        parser = RequestParser()
        parser.add_argument('target', type=int, required=True, location=['form', 'json'])
        parser.add_argument('type', type=int, choices=(0, 1), required=True, location=['form', 'json'])
        parser.add_argument('like_type', type=int, choices=(0, 1), required=True, location=['form', 'json'])
        args = parser.parse_args()
        try:
            if args['type'] == 0:
                db.session.query(IsLike).filter(IsLike.like_id == args['target'], IsLike.like_type == args['like_type'],
                                                IsLike.user_id == g.userInfo.get('id')).delete()
                message = '取消点赞成功'
            if args['type'] == 1:
                db.session.add(
                    IsLike(like_id=args['target'], like_type=args['like_type'], user_id=g.userInfo.get('id')))
                message = '点赞成功'
            db.session.commit()
        except Exception as e:
            flask_restful.abort(500, message=str(e))
        return {'status': 200, 'message': message, 'data': {'target': args['target']}}


class CommentsResource(Resource):
    method_decorators = {'post': [login_required], 'get': [set_read_db]}

    def get(self):
        parser = RequestParser()
        parser.add_argument('source', required=True, type=int, location=['args'])
        parser.add_argument('type', required=True, choices=('a', 'c'), location=['args'])
        parser.add_argument('offset', type=int, default=0, location=['args'])
        parser.add_argument('limit', type=int, default=2, location=['args'])
        args = parser.parse_args()
        data_dict = {}
        comment_list = []
        if args['type'] == 'a':
            comments = db.session.query(Comment).options(load_only(Comment.id)).filter(
                Comment.article_id == args['source'], Comment.comment_id == 0).order_by(
                desc(Comment.id)).all()  # 获取所有主评论(Comment.comment_id == 0)

        if args['type'] == 'c':
            comments = db.session.query(Comment).options(load_only(Comment.id)).filter(
                Comment.comment_id == args['source']).order_by(desc(Comment.id)).all()  # 获取所有子评论
        if args['offset'] == 0:
            args['offset'] = comments[0].id if len(comments) else -1

        data_dict['total_count'] = len(comments)

        if args['type'] == 'a':  # 主评论
            comments_users = db.session.query(Comment, User).join(User, Comment.user_id == User.id).filter(
                Comment.article_id == args['source'], Comment.id <= args['offset']).order_by(
                desc(Comment.id)).limit(args['limit']).all()

        if args['type'] == 'c':  # 子评论
            comments_users = db.session.query(Comment, User).join(User, Comment.user_id == User.id).filter(
                Comment.comment_id == args['source'], Comment.id <= args['offset']).order_by(
                desc(Comment.id)).limit(args['limit']).all()

        for item in comments_users:
            dict = {
                'com_id': item.Comment.id,
                'aut_id': item.User.id,
                'aut_name': item.User.name,
                'aut_photo': item.User.photo,
                'pubdat': item.Comment.pubdat.isoformat(),
                'content': item.Comment.content,
                'is_top': item.Comment.is_top,
            }

            like_count = db.session.query(func.count(1)).filter(IsLike.like_id == item.Comment.id,
                                                                IsLike.like_type == 1).scalar()
            dict['like_count'] = like_count  # 评论点赞数量

            reply_count = db.session.query(func.count(1)).filter(Comment.comment_id == item.Comment.id).scalar()
            dict['reply_count'] = reply_count  # 评论回复数量

            is_liking = db.session.query(func.count(1)).filter(IsLike.like_id == item.Comment.id,
                                                               IsLike.like_type == 1,
                                                               IsLike.user_id == g.userInfo.get('id')).scalar()
            dict['is_liking'] = (is_liking == 1)  # 当前用户是否点赞

            comment_list.append(dict)
        if comment_list and comment_list[-1]['com_id'] != 1:
            last_id = comment_list[-1]['com_id'] - 1
        else:
            last_id = -1
        data_dict.update({'last_id': last_id, 'results': comment_list})
        return {'status': 200, 'message': '获取评论信息成功', 'data': data_dict}

    def post(self):
        parser = RequestParser()
        parser.add_argument('target', type=int, required=True, location=['form', 'json'])
        parser.add_argument('art_id', type=int, default=0, location=['form', 'json'])
        parser.add_argument('content', required=True, type=validate_util.notNoneStr, location=['form', 'json'])
        args = parser.parse_args()
        try:
            if args['art_id']:  # 添加子评论
                comment = Comment(user_id=g.userInfo.get('id'), content=args['content'], article_id=args['art_id'],
                                  comment_id=args['target'])
                message = '回复评论成功'
            else:  # 添加主评论
                comment = Comment(user_id=g.userInfo.get('id'), content=args['content'], article_id=args['target'])
                message = '添加评论成功'
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flask_restful.abort(500, message=str(e))
        return {'status': 200, 'message': message, 'data': {'com_id': comment.id, 'target': args['target'],
                                                            'art_id': args['art_id'] if args['art_id'] else args[
                                                                'target']}}


class CommentResource(Resource):
    method_decorators = {'get': [set_read_db]}

    def get(self):
        parser = RequestParser()
        parser.add_argument('target', required=True, type=int, location=['args'])
        args = parser.parse_args()
        data = {}
        try:
            comment = db.session.query(Comment).filter(Comment.id == args['target']).one()
            user = comment.user
            reply_count = db.session.query(func.count(1)).filter(Comment.comment_id == comment.id).scalar()
            data.update({
                'com_id': comment.id,
                'aut_id': user.id,
                'aut_name': user.name,
                'aut_photo': user.photo,
                'reply_count': reply_count,
                'pubdat': comment.pubdat.isoformat(),
                'content': comment.content
            })
        except Exception as e:
            flask_restful.abort(500, message=str(e))
        return {'status': 200, 'message': '获取指定评论信息成功', 'data': data}


class CommentsCountResource(Resource):
    method_decorators = {'get': [set_read_db]}

    def get(self):
        parser = RequestParser()
        parser.add_argument('target', type=int, required=True, location=['args'])
        args = parser.parse_args()
        comments_count = db.session.query(func.count(1)).filter(Comment.article_id == args['target']).scalar()
        return {'status': 200, 'message': '获取评论数量成功', 'data': {'count': comments_count}}


class ArticlesResource(Resource):
    method_decorators = {'get': [set_read_db]}

    def get(self):
        parser = RequestParser()
        parser.add_argument('per_page', type=int, default=5, location=['args'])
        parser.add_argument('now_id', type=int, default=0, location=['args'])
        parser.add_argument('channel', type=int, required=True, location=['args'])
        args = parser.parse_args()
        articles = db.session.query(Article).filter(Article.channel_id == args['channel']).order_by(
            desc(Article.id)).all()
        data_dict = {}
        article_list = []
        if args['now_id'] == 0:
            args['now_id'] = articles[0].id if len(articles) else -1
        if args['per_page'] > 100:
            args['per_page'] = 100
        data_dict['total_count'] = len(articles)

        articles_users = db.session.query(Article, User).join(User, Article.auth_id == User.id).filter(
            Article.channel_id == args['channel'], Article.id <= args['now_id']).order_by(desc(Article.id)).limit(
            args['per_page']).all()
        for item in articles_users:
            dict = {
                'art_id': item.Article.id,
                'title': item.Article.title,
                'aut_id': item.User.id,
                'aut_name': item.User.name,
                'pubdate': item.Article.pubdate.isoformat(),
            }
            comments = item.Article.comments
            dict['comm_count'] = len(comments)

            img_dict = {
                'type': 0,
                'images': []
            }
            if not item.Article.cover_1:
                pass
            elif item.Article.cover_3:
                img_dict['type'] = 3
                img_dict['images'] = [item.Article.cover_1, item.Article.cover_2, item.Article.cover_3]
            else:
                img_dict['type'] = 1
                img_dict['images'] = [item.Article.cover_1]
            dict['cover'] = img_dict  # 文章封面
            article_list.append(dict)
        if article_list and article_list[-1]['art_id'] != 1:
            data_dict['now_id'] = article_list[-1]['art_id'] - 1
        else:
            data_dict['now_id'] = -1

        data_dict['per_page'] = args['per_page']
        data_dict['results'] = article_list
        return {'status': 200, 'message': '获取频道文章列表成功', 'data': data_dict}


class ArticleResource(Resource):
    method_decorators = {'get': [set_read_db]}

    def get(self, article_id):
        dict = {}
        article, auth = db.session.query(Article, User).join(User, Article.auth_id == User.id).filter(
            Article.id == article_id).one()
        dict.update({
            'art_id': article.id,
            'title': article.title,
            'pubdate': article.pubdate.isoformat(),
            'aut_id': auth.id,
            'aut_name': auth.name,
            'aut_photo': auth.photo,
            'content': article.content
        })
        # 当前用户是否关注文章作者
        is_followed = db.session.query(func.count(1)).filter(user2user.c.from_user_id == g.userInfo.get('id'),
                                                             user2user.c.to_user_id == auth.id).scalar()
        dict['is_followed'] = True if is_followed else False
        # 当前用户是否点赞文章
        attitude = db.session.query(func.count(1)).filter(IsLike.like_id == article.id,
                                                          IsLike.like_type == IsLike.LikeType.ARTICLE,
                                                          IsLike.user_id == g.userInfo.get('id')).scalar()
        dict['attitude'] = True if attitude else False
        # 当前用户是否收藏文章
        is_collected = db.session.query(func.count(1)).filter(user2article.c.article_id == article.id,
                                                              user2article.c.user_id == g.userInfo.get('id')).scalar()
        dict['is_collected'] = True if is_collected else False

        return {'status': 200, 'message': '获取文章详细信息成功', 'data': {'results': [dict]}}


class SearchResource(Resource):
    method_decorators = {'get': [set_read_db]}

    def get(self):
        parser = RequestParser()
        parser.add_argument('keys', required=True, type=validate_util.notNoneStr, location=['args'])
        args = parser.parse_args()
        article_list = []
        search_pattern = f'%{args["keys"]}%'
        articles = db.session.query(Article).options(load_only(Article.id, Article.title)).filter(
            Article.title.like(search_pattern)).all()
        for item in articles:
            dict = {
                'id': item.id,
                'title': item.title
            }
            article_list.append(dict)
        return {'status': 200, 'message': '获取搜索列表成功', 'data': {'result': article_list}}
