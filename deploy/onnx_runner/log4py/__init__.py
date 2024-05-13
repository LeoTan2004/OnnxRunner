import inspect
import logging
import time
from inspect import getmodulename

from .log import __console_handle, __file_handle

global_logger_level = logging.INFO


def get_logger(name='', level=global_logger_level):
    l = logging.getLogger(name)
    l.setLevel(level)

    __console_handle(l)

    __file_handle(l)
    return l


# 创建日志器logger并将其日志级别设置为DEBUG
# lo = get_logger("onnx_runner")


# logger.warning("This is a warning message.")
# logger.error("This is an error message.")
# logger.info("This is an info message.")
# logger.debug("This is a debug message.")
# logger.critical("This is a critical message.")


class Tracert:
    def __init__(self, level=logging.DEBUG, show_res=False, show_args=False):
        self.show_res = show_res
        self.show_args = show_args
        self.level = level

    def __call__(self, func):
        if not hasattr(func, '__is_dec__'):
            return func

        def decorate(*args, **kw):
            name = inspect.getmodule(func).__name__
            if name is None:
                name = getmodulename(func.__code__.co_filename)
            l = get_logger(name)
            try:
                if self.show_args:
                    l.log(level=self.level, msg=f'call {func.__name__}({args}, {kw})')
                else:
                    l.log(level=self.level, msg=f'call {func.__name__}()')
                s = time.time()
                res = func(*args, **kw)
                if self.show_res:
                    l.log(level=self.level, msg=f'{func.__name__} finished in [{time.time() - s}s] result: {res} ')
                else:
                    l.log(level=self.level, msg=f'{func.__name__} finished in [{time.time() - s}s]')
            except Exception as e:
                l.error(f'{func.__name__} error: {e}')
                raise e
            return res

        decorate.__is_dec__ = True
        return decorate


class Log4Py:
    def __init__(self, name=''):  # @语句处调用
        self.name = name

    def __call__(self, Class):
        self.Class = Class
        if not hasattr(Class, 'logger'):
            if len(self.name) == 0:
                self.name = Class.__name__
            self.Class.logger = get_logger(self.name)

        def wrapper(*args, **kwargs):  # 创建实例时调用
            self.wrapped = self.Class(*args, **kwargs)
            return self.wrapped

        return wrapper

# @Log4Py()
# class Hello:
#     @Tracert()
#     def test(self):
#         self.logger.info('Hello')
#
#
# @Tracert(logging.INFO)
# def __test_log(hello):
#     # 1 / 0
#     print(hello)
#
#
# if __name__ == '__main__':
#     h = Hello()
#     h.test()
#     __test_log('wuhu')
