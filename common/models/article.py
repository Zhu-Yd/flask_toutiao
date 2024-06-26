from app import db
from datetime import datetime
from models import BaseModel

# 用户收藏文章关系表
user2article = db.Table('tt_user2article',
                     db.Column('user_id', db.Integer, db.ForeignKey('tt_user.id'), primary_key=True),
                     db.Column('article_id', db.Integer, db.ForeignKey('tt_article.id'), primary_key=True)
                     )

class Article(BaseModel):
    __tablename__ = 'tt_article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    auth_id = db.Column(db.Integer, db.ForeignKey('tt_user.id'))
    pubdate = db.Column(db.DateTime, default=datetime.now)
    channel_id = db.Column(db.Integer, db.ForeignKey('tt_channel.id'))
    cover_1 = db.Column(db.String)
    cover_2 = db.Column(db.String)
    cover_3 = db.Column(db.String)
    like_num = db.Column(db.String)

    # 文章的评论
    comments = db.relationship('Comment', backref='article', lazy=True)

    # 收藏该文章的用户
    users = db.relationship('User', secondary=user2article, back_populates='collect_articles')


    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'auth_id': self.authId,
            'pubdate': self.pubdate.isofomat(),
            'channel_id': self.channelId,
            'cover_1': self.cover_1,
            'cover_2': self.cover_2,
            'cover_3': self.cover_3,
            'like_num': self.like_num
        }


class IsLike(BaseModel):
    __tablename__ = 'tt_islike'

    class LikeType:
        ARTICLE = 0
        COMMENT = 1

    user_id = db.Column(db.Integer, db.ForeignKey('tt_user.id'), primary_key=True)
    like_type = db.Column(db.Integer, primary_key=True)
    like_id = db.Column(db.Integer, primary_key=True)


class Comment(BaseModel):
    __tablename__ = 'tt_comment'

    class IsTop:
        NO = '0'
        YES = '1'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('tt_user.id'))
    pubdat = db.Column(db.DateTime, default=datetime.now)
    article_id = db.Column(db.Integer, db.ForeignKey('tt_article.id'))
    is_top = db.Column(db.Integer, default=IsTop.NO)
    comment_id = db.Column(db.Integer, default=0, doc='父级评论ID')
