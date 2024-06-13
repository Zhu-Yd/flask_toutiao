from app import db
from models.article import user2article
user2user = db.Table('tt_user2user',
                     db.Column('from_user_id', db.Integer, db.ForeignKey('tt_user.id'), primary_key=True),
                     db.Column('to_user_id', db.Integer, db.ForeignKey('tt_user.id'), primary_key=True)
                     )


class User(db.Model):
    __tablename__ = 'tt_user'

    class GENDER:
        MALE = '0'
        FEMALE = '1'
        OTHER = '2'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String)
    name = db.Column(db.String)
    photo = db.Column(db.String)
    gender = db.Column(db.String, default='0')
    birthday = db.Column(db.Date, default='1970-01-01')

    # 用户附加信息
    profile = db.relationship('UserProfile', backref='user', uselist=False)

    # 该用户的粉丝
    followers = db.relationship('User', secondary=user2user,
                                primaryjoin=(user2user.c.to_user_id == id),
                                secondaryjoin=(user2user.c.from_user_id == id),
                                backref=db.backref('following', lazy='dynamic', uselist=True), lazy='dynamic')

    # 用户关注频道
    # channels = db.relationship('Channel', secondary=User2Channel, back_populates='users')

    # 用户发布的文章
    articles = db.relationship('Article', backref='user', lazy=True)

    # 用户发布的评论
    comments = db.relationship('Comment', backref='user', lazy=True)

    # 用户收藏的文章
    collect_articles = db.relationship('Article', secondary=user2article, back_populates='users')


    def to_dict(self):
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.name,
            'photo': self.photo,
            'gender': self.gender,
            'birthday': self.birthday.isoformat() if self.birthday else None
        }


class UserProfile(db.Model):
    __tablename__ = 'tt_user_info'
    real_name = db.Column('real_name', db.String)
    id_number = db.Column('id_number', db.String)
    id_card_front = db.Column('id_card_front', db.String)
    id_card_back = db.Column('id_card_back', db.String)
    id_card_handheld = db.Column('id_card_handheld', db.String)
    intro = db.Column(db.String)
    user_id = db.Column('user_id', db.ForeignKey('tt_user.id'), primary_key=True)

    def to_dict(self):
        return {
            'real_name': self.real_name,
            'id_number': self.id_number,
            'id_card_front': self.id_card_front,
            'id_card_back': self.id_card_back,
            'id_card_handheld': self.id_card_handheld,
            'intro': self.intro,
            'user_id': self.user_id
        }
