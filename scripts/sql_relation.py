from app import db

# 多对多关系定义
student_course = db.Table('student_course',
                          db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
                          db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
                          )


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    courses = db.relationship('Course', secondary=student_course, back_populates='students')


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    students = db.relationship('Student', secondary=student_course, back_populates='courses')


# 一对多关系定义
class Parent(db.Model):
    __tablename__ = 'parent'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    children = db.relationship('Child', backref='parent', lazy=True)


class Child(db.Model):
    __tablename__ = 'child'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)


# 定义一对一关系
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    profile = db.relationship('UserProfile', backref='user', uselist=False)
    # profile = db.relationship('UserProfile', backref=db.backref('user', uselist=False), uselist=False)


class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
