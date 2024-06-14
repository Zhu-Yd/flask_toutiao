from app import db


class BaseModel(db.Model):
    __abstract__ = True  # 设置为抽象基类，不会创建表

    # 根据字典动态更新模型的方法
    def update_from_dict(self, data):
        for field in data:
            if hasattr(self, field):
                setattr(self, field, data[field])
