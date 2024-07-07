from flask_sqlalchemy import SQLAlchemy
from models.db_routing.routing_sqlalchemy import RoutingSQLAlchemy
# 数据库对象
db: SQLAlchemy = RoutingSQLAlchemy()


class BaseModel(db.Model):
    __abstract__ = True  # 设置为抽象基类，不会创建表

    # 根据字典动态更新模型的方法
    def update_from_dict(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
