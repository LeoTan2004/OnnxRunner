import os
import shelve

from .repository import Repository, ID, D


class ObjectRepository(Repository):
    """对象存储"""

    def __init__(self, db_filename='./db/obj_repository.db', prefix='obj'):
        self.db_filename = db_filename
        self.prefix = prefix

    def read(self, uid: ID) -> D:
        return self.db.get(f'{self.prefix}_{str(uid)}', None)

    def write(self, uid: ID, data: D):
        self.db[f'{self.prefix}_{str(uid)}'] = data

    def __enter__(self):
        # 检查数据库是否存在，如果不存在则创建
        dir_path = os.path.dirname(self.db_filename)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        # 打开数据库
        self.db = shelve.open(self.db_filename)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
