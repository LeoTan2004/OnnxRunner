import colorsys

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image

from utils.utils import (cvtColor, preprocess_input)
from utils.utils_bbox import DecodeBoxNP


def get_onnx_session(onnx_path):
    # 加载ONNX模型
    session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    return session


class YOLO_ONNX_DETECT(object):
    _defaults = {
        # --------------------------------------------------------------------------#
        #   使用自己训练好的模型进行预测一定要修改onnx_path和classes_path！
        #   onnx_path指向logs文件夹下的权值文件，classes_path指向model_data下的txt
        #
        #   训练好后logs文件夹下存在多个权值文件，选择验证集损失较低的即可。
        #   验证集损失较低不代表mAP较高，仅代表该权值在验证集上泛化性能较好。
        #   如果出现shape不匹配，同时要注意训练时的onnx_path和classes_path参数的修改
        # --------------------------------------------------------------------------#
        "onnx_path": 'model_data/models.onnx',
        # "classes_path": 'model_data/coco_classes.txt',
        "classes_path": 'model_data/voc_classes.txt',
        # ---------------------------------------------------------------------#
        #   anchors_path代表先验框对应的txt文件，一般不修改。
        #   anchors_mask用于帮助代码找到对应的先验框，一般不修改。
        # ---------------------------------------------------------------------#
        "anchors_path": 'model_data/yolo_anchors.txt',
        "anchors_mask": [[6, 7, 8], [3, 4, 5], [0, 1, 2]],
        # ---------------------------------------------------------------------#
        #   输入图片的大小，必须为32的倍数。
        # ---------------------------------------------------------------------#
        "input_shape": [640, 640],
        # ---------------------------------------------------------------------#
        #   只有得分大于置信度的预测框会被保留下来
        # ---------------------------------------------------------------------#
        "confidence": 0.5,
        # ---------------------------------------------------------------------#
        #   非极大抑制所用到的nms_iou大小
        # ---------------------------------------------------------------------#
        "nms_iou": 0.3,
        # ---------------------------------------------------------------------#
        #   该变量用于控制是否使用letterbox_image对输入图像进行不失真的resize，
        #   在多次测试后，发现关闭letterbox_image直接resize的效果更好
        # ---------------------------------------------------------------------#
        "letterbox_image": True
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    # ---------------------------------------------------#
    #   初始化YOLO
    # ---------------------------------------------------#
    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        for name, value in kwargs.items():
            setattr(self, name, value)
            self._defaults[name] = value
        self.onnx_session = get_onnx_session(self.onnx_path)
        # 获得所有的输入node
        self.input_name = self.get_input_name()
        # 获得所有的输出node
        self.output_name = self.get_output_name()

        # ---------------------------------------------------#
        #   获得种类和先验框的数量
        # ---------------------------------------------------#
        self.class_names, self.num_classes = self.get_classes(self.classes_path)
        self.anchors, self.num_anchors = self.get_anchors(self.anchors_path)
        self.bbox_util = DecodeBoxNP(self.anchors, self.num_classes, (self.input_shape[0], self.input_shape[1]),
                                     self.anchors_mask)

        # ---------------------------------------------------#
        #   画框设置不同的颜色
        # ---------------------------------------------------#
        hsv_tuples = [(x / self.num_classes, 1., 1.) for x in range(self.num_classes)]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), self.colors))

        # show_config(**self._defaults)

    def get_classes(self, classes_path):
        with open(classes_path, encoding='utf-8') as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names, len(class_names)

    def get_anchors(self, anchors_path):
        '''loads the anchors from a file'''
        with open(anchors_path, encoding='utf-8') as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        anchors = np.array(anchors).reshape(-1, 2)
        return anchors, len(anchors)

    def get_input_name(self):
        # 获得所有的输入node
        input_name = []
        for node in self.onnx_session.get_inputs():
            input_name.append(node.name)
        return input_name

    def get_output_name(self):
        # 获得所有的输出node
        output_name = []
        for node in self.onnx_session.get_outputs():
            output_name.append(node.name)
        return output_name

    def get_input_feed(self, image_tensor):
        # 利用input_name获得输入的tensor
        input_feed = {}
        for name in self.input_name:
            input_feed[name] = image_tensor
        return input_feed

    # ---------------------------------------------------#
    #   对输入图像进行resize
    # ---------------------------------------------------#
    def resize_image(self, image, size, letterbox_image, mode='PIL'):
        if mode == 'PIL':
            iw, ih = image.size
            w, h = size

            if letterbox_image:
                scale = min(w / iw, h / ih)
                nw = int(iw * scale)
                nh = int(ih * scale)

                image = image.resize((nw, nh), Image.BICUBIC)
                new_image = Image.new('RGB', size, (128, 128, 128))
                new_image.paste(image, ((w - nw) // 2, (h - nh) // 2))
            else:
                new_image = image.resize((w, h), Image.BICUBIC)
        else:
            image = np.array(image)
            if letterbox_image:
                # 获得现在的shape
                shape = np.shape(image)[:2]
                # 获得输出的shape
                if isinstance(size, int):
                    size = (size, size)

                # 计算缩放的比例
                r = min(size[0] / shape[0], size[1] / shape[1])

                # 计算缩放后图片的高宽
                new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
                dw, dh = size[1] - new_unpad[0], size[0] - new_unpad[1]

                # 除以2以padding到两边
                dw /= 2
                dh /= 2

                # 对图像进行resize
                if shape[::-1] != new_unpad:  # resize
                    image = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
                top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
                left, right = int(round(dw - 0.1)), int(round(dw + 0.1))

                new_image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                               value=(128, 128, 128))  # add border
            else:
                new_image = cv2.resize(image, (w, h))

        return new_image

    def detect_image(self, image):
        image_shape = np.array(np.shape(image)[0:2])
        # ---------------------------------------------------------#
        #   在这里将图像转换成RGB图像，防止灰度图在预测时报错。
        #   代码仅仅支持RGB图像的预测，所有其它类型的图像都会转化成RGB
        # ---------------------------------------------------------#
        image = cvtColor(image)
        h, w = image.size
        image_data = self.resize_image(image, self.input_shape, True)
        # ---------------------------------------------------------#
        #   添加上batch_size维度
        #   h, w, 3 => 3, h, w => 1, 3, h, w
        # ---------------------------------------------------------#
        #                 边缘拓展     ERROR       归一化             读取数据
        image_data = np.expand_dims(np.transpose(preprocess_input(np.array(image_data, dtype='float32')), (2, 0, 1)), 0)

        input_feed = self.get_input_feed(image_data)
        outputs = self.onnx_session.run(output_names=self.output_name, input_feed=input_feed)

        feature_map_shape = [[int(j / (2 ** (i + 3))) for j in self.input_shape] for i in
                             range(len(self.anchors_mask))][::-1]
        for i in range(len(self.anchors_mask)):
            outputs[i] = np.reshape(outputs[i],
                                    (1, len(self.anchors_mask[i]) * (5 + self.num_classes),
                                     feature_map_shape[i][0],
                                     feature_map_shape[i][1]))
        # 从这里开始java代码翻译
        outputs = self.bbox_util.decode_box(outputs)
        # ---------------------------------------------------------#
        #   将预测框进行堆叠，然后进行非极大抑制
        # ---------------------------------------------------------#
        results = self.bbox_util.non_max_suppression(np.concatenate(outputs, 1), self.num_classes, self.input_shape,
                                                     image_shape, self.letterbox_image, conf_thres=self.confidence,
                                                     nms_thres=self.nms_iou)
        # 这里结束代码翻译
        if results[0] is None:
            return None

        top_label = np.array(results[0][:, 6], dtype='int32')
        top_conf = results[0][:, 4] * results[0][:, 5]
        top_boxes = results[0][:, :4]
        res = []
        for i, c in list(enumerate(top_label)):
            predicted_class = self.class_names[int(c)]
            box = top_boxes[i]
            score = top_conf[i]

            top, left, bottom, right = box

            top = max(0, np.floor(top).astype('int32')) / h
            left = max(0, np.floor(left).astype('int32')) / w
            bottom = min(image.size[1], np.floor(bottom).astype('int32')) / h
            right = min(image.size[0], np.floor(right).astype('int32')) / w
            box = {'top': top, 'left': left,
                   'bottom': bottom, 'right': right}
            res.append(DetectResult(predicted_class, score, box))
        return res


class DetectResult:
    def __init__(self, predict_class, top_conf, top_boxes):
        self.predict_class = predict_class
        self.score = top_conf
        self.box = top_boxes

    def __repr__(self):
        return f"{self.predict_class} {self.score} {self.box}"
