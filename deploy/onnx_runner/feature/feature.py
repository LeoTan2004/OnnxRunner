import numpy as np

from abc import abstractmethod
from typing import TypeVar, Generic

from ..log4py import Log4Py

IN = TypeVar('IN')
OUT = TypeVar('OUT')


class FeatureExtractor(Generic[IN, OUT]):
    """特征提取器，返回None表示不提取特征"""

    @abstractmethod
    def extract(self, input_element: IN) -> OUT:
        """
        提取特征，None表示不提取特征
        """
        ...


@Log4Py()
class StepFeatureExtractor(Generic[IN], FeatureExtractor[IN, IN]):
    """
    固定步长特征提取器，返回特征
    """

    def __init__(self, step):
        self.logger.info(f'step: {step}')
        self.step = step
        self.count = 0

    def extract(self, input_element: IN) -> OUT:
        self.count += 1
        if self.count % self.step == 0:
            self.logger.debug(f'feature out a result in: {self.count}/{self.step}')
            return input_element
        return None


@Log4Py()
class DifferenceFeatureExtractor(Generic[IN], FeatureExtractor[IN, IN]):
    """
    差分特征提取器，返回特征
    """

    def __init__(self, limit: float):
        self.logger.info(f'difference limit: {limit}')
        self.step = limit
        self.last = None
        self.__last__ = None

    def diff(self, e: IN):
        """计算图像差分"""
        t = e.astype('float64')
        if self.__last__ is None:
            dif = np.abs(t)
        else:
            dif = np.abs(t - self.__last__)
        o = np.sum(dif).squeeze()
        o /= t.size
        return o

    def __set_basic(self, basic: IN):
        self.last = basic
        self.__last__ = self.last.astype('float64')

    def extract(self, input_element: IN) -> IN:
        if input_element is None:
            return None
        if self.last is None or self.last.size != input_element.size:
            self.__set_basic(input_element)
            return input_element
        else:
            dif = self.diff(input_element)
            self.logger.debug(f'image difference: {dif}/{self.step}')
            if dif >= self.step:
                self.__set_basic(input_element)
                return input_element
            return None
