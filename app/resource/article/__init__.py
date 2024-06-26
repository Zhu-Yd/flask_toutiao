from flask import Blueprint
from flask_restful import Api
from app.resource.article.Resource import CollectionsResource, LikingsResource, CommentsResource, CommentResource, \
    CommentsCountResource, ArticlesResource, ArticleResource, SearchResource
from utils.custom_error import custom_404_error

article_bp = Blueprint('article_bp', __name__, url_prefix='/article')
api = Api(article_bp, catch_all_404s=True)

# 设置自定义的错误处理函数
api.handle_error = custom_404_error

# 注册资源
api.add_resource(CollectionsResource, '/collections')   # 收藏相关
api.add_resource(LikingsResource, '/likings')   # 点赞相关
api.add_resource(CommentsResource, '/comments')  # 评论相关
api.add_resource(CommentResource, '/comment')  # 获取指定评论信息
api.add_resource(CommentsCountResource, '/comments_count')  # 获取文章评论数量
api.add_resource(ArticlesResource,'/articles')  # 获取频道文章列表
api.add_resource(ArticleResource,'/<regx("\d+"):article_id>') # 获取文章详细信息
api.add_resource(SearchResource,'/search')  # 搜索文章
