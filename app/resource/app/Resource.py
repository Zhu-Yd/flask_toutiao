from flask_restful import Resource, inputs
from flask_restful.reqparse import RequestParser
from utils import validate_util
from app import db
from models.user import User
from utils.jwt_util import generate_jwt


class LoginResource(Resource):
    def post(self):
        # 验证参数
        parser = RequestParser()
        parser.add_argument('mobile', required=True, type=validate_util.mobile, location=['json', 'form'],
                            help='{error_msg}')
        parser.add_argument('code', required=True, type=inputs.regex(r'^\d{6}$'), location=['json', 'form'])
        args = parser.parse_args()
        mobile = args['mobile']
        code = args['code']
        print(f'手机号:{mobile}验证码:{code}')

        # 查询用户是否存在 且 验证码是否正确
        if code != '910219':
            return {'message': '验证码错误'}, 500

        user = db.session.query(User).filter(User.phone == args['mobile']).first()

        # 如果用户不存在，则注册用户
        if not user:
            user = User(name=mobile, phone=mobile)
            db.session.add(user)

        # 提交数据库事务
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            return {'message': '登录失败,请稍后再试'}, 500

        # 构建userInfo
        userInfo = {**user.to_dict()}
        # 生成token
        token = generate_jwt(userInfo)

        return {'status': 200,
                'message': '登录成功',
                'token': token}
