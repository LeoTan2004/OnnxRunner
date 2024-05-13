import os

import cv2
from cv2 import Mat

from ..log4py import Log4Py
from .source import Source


@Log4Py()
class DirImg(Source[Mat]):
    img_ext = ('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')

    def __init__(self, dir_path: str):
        super().__init__()
        self.img_path = dir_path
        self.imgs = self.refresh_dir()
        self.logger.info(f'dir_img: {self.img_path}')

    def refresh_dir(self):
        if not os.path.exists(self.img_path):
            self.logger.error(f'img_path: {self.img_path} not exists')
            return None
        return os.listdir(self.img_path)

    """每次读取目录下的一张图片"""

    def get_img(self) -> Mat:
        for img_name in self.imgs:
            if img_name.lower().endswith(self.img_ext):
                self.logger.debug(f'read img_name: {img_name} from {self.img_path}')
                yield cv2.imread(os.path.join(self.img_path, img_name))

    def get_next(self) -> Mat:
        return self.__iter__().__next__()

    def __iter__(self):
        return self.get_img().__iter__()
