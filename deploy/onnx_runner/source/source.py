"""数据源"""
import time
from abc import abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

ID = TypeVar("ID")


class IdentifyWrapper(Generic[T, ID]):
    """带上id的数据包裹"""

    def __init__(self, identity: ID, data: T) -> None:
        self.id = identity
        self.data = data
        self.created_at = time.time()

    def data(self) -> T:
        return self.data

    def identity(self) -> ID:
        return self.id


class Source(Generic[T]):

    def __next__(self) -> T:
        return self.get_next()

    @abstractmethod
    def get_next(self) -> T:
        ...

    def __iter__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class IdGenerator(Generic[T, ID]):
    @abstractmethod
    def get_id_for(self, data: T) -> ID:
        ...


class IdGeneratorFactory:

    @staticmethod
    def get_instance(sw):
        if sw == "auto_incr_id":
            return IdGeneratorFactory.auto_incr_id(0, 1)
        elif sw == "create_time_id":
            return IdGeneratorFactory.create_time_id()
        else:
            raise ValueError(f"Unknown source: {sw}")


    @staticmethod
    def auto_incr_id(base, step) -> IdGenerator:
        class Generator(IdGenerator):
            def __init__(self) -> None:
                self.base = base
                self.step = step
                self.current = base

            def get_id_for(self, data):
                self.current += self.step
                return self.current

        return Generator()

    @staticmethod
    def create_time_id() -> IdGenerator:
        class Generator(IdGenerator):
            def get_id_for(self, data):
                return time.time()

        return Generator()


class IdentitySourceWrapper(Generic[T, ID], Source[T]):
    """带上id的数据源"""

    def __init__(self, source: Source[T], id_generator: IdGenerator[T, ID] = IdGeneratorFactory.create_time_id()):
        self.id_generator = id_generator
        self.source = source

    def get_next(self) -> T:
        data = self.source.get_next()
        return IdentifyWrapper(self.id_generator.get_id_for(data), data)
