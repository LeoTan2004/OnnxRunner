from abc import abstractmethod

import cv2
import numpy as np
from PIL import Image

from ..log4py import Log4Py, Tracert


class Detector:

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    @abstractmethod
    def detect(self, frame):
        ...


@Log4Py()
class YoloDetector(Detector):
    def __init__(self, model):
        self.model = model

    # 检测图片
    @Tracert()
    def detect(self, frame):
        # 格式转变，BGRtoRGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 转变成Image
        frame = Image.fromarray(np.uint8(frame))
        # 进行检测
        res = self.model.detect_image(frame)
        self.logger.info(f"detect success: {res}")
        return res
