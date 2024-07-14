from flask import Flask
from app.settings.config import config_dict
from utils import constants
from redis import StrictRedis
from models import db

# redis对象
# redis_cli = None  # type: StrictRedis
redis_master = None  # type: StrictRedis
redis_slave = None  # type: StrictRedis


def create_flask_app(env: str):
    app = Flask(__name__)  # 创建app
    app.config.from_object(config_dict[env])  # 加载配置信息
    app.config.from_envvar(constants.EXTRA_ENV_CONFIG, True)  # 加载隐私配置信息
    return app


def create_app(env: str):
    app = create_flask_app(env)

    # 加载拓展组件
    register_extensions(app)

    # 加载蓝图
    register_buleprint(app)

    return app


def register_extensions(app: Flask):
    # 延后加载app，进行数据库对象的初始化
    db.init_app(app)

    # 延后加载redis,进行redis对象的初始化
    # global redis_cli
    # redis_cli = StrictRedis(
    #     host=app.config['REDIS_HOST'],
    #     port=app.config['REDIS_PORT'],
    #     password=app.config['REDIS_PASSWORD'],
    #     decode_responses=True  # 自动解码
    # )
    # 配置redis哨兵实现主从分离+高可用
    from redis.sentinel import Sentinel
    _sentinel = Sentinel(app.config['REDIS_SENTINELS'])
    global redis_master
    redis_master = _sentinel.master_for(app.config['REDIS_SENTINEL_SERVICE_NAME'],
                                        password=app.config['REDIS_PASSWORD'], decode_responses=True)
    global redis_slave
    redis_slave = _sentinel.slave_for(app.config['REDIS_SENTINEL_SERVICE_NAME'], password=app.config['REDIS_PASSWORD'],
                                      decode_responses=True)

    # 加载自定义路由转换器:转换器必须在蓝图注册之前注册
    from utils import converters
    converters.register_converters(app)

    # 加载中间件
    from utils import middlewares
    app.before_request(middlewares.auth_jwt_token)  # 添加请求钩子（鉴权中间件）

    # 支持跨域请求
    from flask_cors import CORS
    CORS(app, supports_credentials=True)


def register_buleprint(app: Flask):
    # 导入app模块蓝图
    from app.resource.app import app_bp
    app.register_blueprint(app_bp)
    # 导入用户模块蓝图
    from app.resource.user import user_bp
    app.register_blueprint(user_bp)
    # 导入频道模块蓝图
    from app.resource.channel import channel_bp
    app.register_blueprint(channel_bp)
    # 导入文章模块蓝图
    from app.resource.article import article_bp
    app.register_blueprint(article_bp)
