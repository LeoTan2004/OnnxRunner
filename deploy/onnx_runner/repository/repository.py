from abc import abstractmethod
from typing import Generic, TypeVar

ID = TypeVar("ID")
D = TypeVar("D")


class Repository(Generic[ID, D]):
    """数据持久化接口"""

    @abstractmethod
    def read(self, uid: ID) -> D:
        """
        从存储中读取数据

        :param uid: 数据唯一标识

        :raises: 数据读取失败
        """
        ...

    @abstractmethod
    def write(self, uid: ID, data: D):
        """
        将数据写入存储

        :param uid: 数据唯一标识
        :param data: 数据

        :raises: 数据写入失败
        """
        ...

    @abstractmethod
    def __enter__(self):
        ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        ...
