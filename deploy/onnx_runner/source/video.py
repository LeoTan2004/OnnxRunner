"""视频数据源"""

import cv2
from cv2 import Mat

from ..log4py import Log4Py
from .source import Source


@Log4Py()
class VideoCap(Source[Mat]):
    """视频数据源"""

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.video_path)

        self.logger.info(
            f"打开视频文件成功，视频来源：{self.video_path}, 帧率：{self.get_video_fps()}, 帧宽：{self.get_frame_width()}, 帧高：{self.get_frame_height()}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __init__(self, video_path):
        """
        :param video_path: 视频文件路径
        """
        self.video_path = video_path

    def release(self):
        """
        释放视频数据源
        """
        self.logger.info("释放视频数据源")
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()

    def get_next(self) -> Mat:
        """
        获取下一帧
        :return 返回视频帧
        """
        frame = self.read()
        if frame is None:
            raise StopIteration
        return frame

    def read(self) -> Mat:
        """
        读取视频帧
        :return 返回视频帧
        """
        ret, frame = self.cap.read()
        if not ret:
            self.logger.error("读取视频帧失败")
            return None
        self.logger.debug(f"读取视频帧成功")
        return frame

    def get_frame_height(self) -> int:
        """
        获取视频帧高度
        :return 返回视频帧高度
        """
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_frame_width(self) -> int:
        """
        获取视频帧宽度
        :return 返回视频帧宽度
        """
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    def get_video_fps(self) -> float:
        """
        获取视频帧率
        :return 返回视频帧率
        """
        return self.cap.get(cv2.CAP_PROP_FPS)
