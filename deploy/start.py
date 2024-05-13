import time

import cv2

from config import config
from onnx_runner.detector.pool import ModelPool, Wrapper
from onnx_runner.feature.feature import DifferenceFeatureExtractor
from onnx_runner.log4py import get_logger
from onnx_runner.repository.obj_repository import ObjectRepository
from onnx_runner.repository.video_repo import VideoRepository
from onnx_runner.source.source import IdGeneratorFactory
from onnx_runner.source.video import VideoCap
from yolo import YOLO_ONNX_DETECT


def run():
    s = time.time()
    f = DifferenceFeatureExtractor(config['difference_feature_extractor'])
    idFacto = IdGeneratorFactory.get_instance(config['id_generator'])
    lo = get_logger("onnx_runner")
    with \
            ModelPool(YOLO_ONNX_DETECT, workers_num=config['multi_detector_pool_size']) as p, \
            VideoCap(config['video_path']) as cap, \
            VideoRepository.with_cap(cap.cap, config['save_path']) as vw:
        for e in cap:
            vw.write(1, e)
            feature = f.extract(e)
            cv2.imshow("video", e)
            if cv2.waitKey(1) == ord('q'):
                cv2.destroyAllWindows()
                break
            if feature is not None:
                lo.info("feature extract success")
                p.submit(feature, idFacto.get_id_for(feature))
    lo.info(f'detect cost time :{time.time() - s}')
    # 输出所有结果并写入文件
    with ObjectRepository(config['object_repository_path']) as repo:
        repo.write('update_time', time.time())
        while p.output_queue.qsize() > 0:
            wrap: Wrapper = p.output_queue.get()
            lo.info(f'result :{wrap.id} {wrap.output_element}')
            repo.write(wrap.id, wrap.output_element)


if __name__ == '__main__':
    run()
