from flask_sqlalchemy import SignallingSession, get_state


class RoutingSession(SignallingSession):
    """
    读写分离路由的session
    """

    def __init__(self, db, autocommit=False, autoflush=True, **options):
        self._name = options.get('bind_name', None)  # 数据库引擎名称
        self.engine_cache = {}  # 数据库引擎缓存
        SignallingSession.__init__(self, db, autocommit=autocommit, autoflush=autoflush, **options)

    def get_bind(self, mapper=None, clause=None):
        """
        获取数据库绑定
        """
        state = get_state(self.app)

        # mapper is None if someone tries to just get a connection
        if mapper is not None:
            """在模型类中 使用 __bind_key__ = 'db_name' 实现 垂直|水平 分库"""
            try:
                # SA >= 1.3
                persist_selectable = mapper.persist_selectable
            except AttributeError:
                # SA < 1.3
                persist_selectable = mapper.mapped_table

            info = getattr(persist_selectable, 'info', {})
            bind_key = info.get('bind_key')
            if bind_key is not None:
                return state.db.get_engine(self.app, bind=bind_key)

        if self.engine_cache.get(self._name) is not None:  # 命中缓存
            print('Using cache bind: _name={}'.format(self._name))
            return self.engine_cache.get(self._name)
        else:  # 没有命中缓存
            if self._name:
                # 指定数据库
                print('Using DB bind: _name={}'.format(self._name))
                self.engine_cache[self._name] = state.db.get_engine(self.app, bind=self._name)
            else:
                # 默认数据库
                print('Using default DB bind: _name={}'.format(state.db.default_bind))
                self.engine_cache[self._name] = state.db.get_engine(self.app, bind=state.db.default_bind)
            return self.engine_cache[self._name]

    def set_to_write(self):
        """
        设置用写数据库
        """
        state = get_state(self.app)

        self._name = state.db.get_bind_for_write()

    def set_to_read(self):
        """
        设置用读数据库
        """
        state = get_state(self.app)

        self._name = state.db.get_bind_for_read()
