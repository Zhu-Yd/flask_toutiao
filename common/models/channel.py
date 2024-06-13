from app import db


class User2Channel(db.Model):
    __tablename__ = 'tt_user2channel'
    user_id = db.Column(db.Integer, db.ForeignKey('tt_user.id'), primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('tt_channel.id'), primary_key=True)
    seq = db.Column(db.Integer)


class Channel(db.Model):
    __tablename__ = 'tt_channel'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # 该频道有哪些用户关注
    # users = db.relationship('User', secondary=User2Channel, back_populates='channels')

    # 该频道有哪些文章
    articles = db.relationship('Article', backref='channel', lazy=True)
