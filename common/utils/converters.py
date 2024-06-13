from werkzeug.routing import BaseConverter


class RegxConverter(BaseConverter):
    def __init__(self, map, *args, **kwargs):
        super().__init__(map, *args, **kwargs)
        self.regex = args[0]

    # 用于将匹配的参数转换为指定的类型
    def to_python(self, value: str):
        return value


class MobileConverter(BaseConverter):
    """
    手机号格式
    """
    regex = r'1[3-9]\d{9}'


def register_converters(app):
    app.url_map.converters['regx'] = RegxConverter
    app.url_map.converters['mobile'] = MobileConverter
