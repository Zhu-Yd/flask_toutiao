from urllib.parse import quote_plus

class DefaultConfig(object):
    SECRET_KEY = 'TOU_TIAO_KEY'
    RESTFUL_JSON = {"ensure_ascii": False}


class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    # mysql连接配置
    password = quote_plus('Ss910219@')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://Ddshop:{password}@192.168.1.66:3306/bigevent'
    # 关闭数据库修改性能跟踪
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 显示sql语句
    SQLALCHEMY_ECHO = True

    # redis连接配置
    REDIS_HOST = '192.168.1.66'
    REDIS_PORT = 6379
    REDIS_PASSWORD = 'zyd910219'


class ProductionConfig(DefaultConfig):
    DEBUG = False


config_dict = {
    'dev': DevelopmentConfig,
    'pro': ProductionConfig
}
