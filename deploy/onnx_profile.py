import cv2

from onnx_runner.log4py import get_logger
from onnx_runner.source.source import IdGeneratorFactory
from onnx_runner.source.dir_img import DirImg
from yolo import YOLO_ONNX_DETECT
import numpy as np
from PIL import Image

detect = YOLO_ONNX_DETECT()
logger = get_logger('onnx_profile')


def det(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 转变成Image
    frame = Image.fromarray(np.uint8(frame))
    # 进行检测
    res, cost_time = detect.detect_image(frame)
    return cost_time


def write(data, path='data.csv'):
    with open(path, 'w') as f:
        for line in data:
            f.write(str(line) + '\r')


time_table = []
idg = IdGeneratorFactory.auto_incr_id(-1, 1)
with DirImg('../test-set/img') as source:
    for img in source:
        idx = idg.get_id_for(None)
        logger.info(f'detect with img-{idx}')
        time_table.append(det(img))

op_count = 54953574592
flops = op_count / np.array(time_table)

print(flops.mean())
write(flops)

import matplotlib.pyplot as plt

x = list(range(1, flops.size + 1))

a = plt.bar(x, flops)

plt.xlabel('Pic')
plt.ylabel('flops')
plt.title('Onnx Model flops Statistics')
plt.savefig('./result_on_laptop.jpg')
