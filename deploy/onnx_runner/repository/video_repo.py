import os

import cv2
from cv2 import VideoWriter

from .repository import Repository, ID, D


class VideoRepository(Repository):

    @staticmethod
    def with_cap(cap, save_path='./save_video', encode='XVID', is_color=True):
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return VideoRepository(save_path, fps, width, height, encode, is_color)

    def __init__(self, save_path='./save_video', fps=30.0, width=320, height=240,
                 fourcc='XVID',
                 is_color=True):
        self.save_path = save_path
        self.fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self.width = width
        self.height = height
        self.fps = fps
        self.is_color = is_color

    def read(self, uid: ID) -> D:
        raise NotImplementedError

    def write(self, uid: ID, data: D):
        self.writer.write(data)

    def __enter__(self):
        dir_path = os.path.dirname(self.save_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.writer = VideoWriter(self.save_path, self.fourcc, self.fps, (self.width, self.height), self.is_color)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.writer.release()
