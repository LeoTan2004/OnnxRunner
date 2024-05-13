from multiprocessing import Process, Queue, Manager
from typing import TypeVar, Generic

from .onnx_detector import YoloDetector
from ..log4py import get_logger, Log4Py

IN = TypeVar('IN')
OUT = TypeVar('OUT')


class Worker(Process):

    def __init__(self, model, queue: Queue, output: Queue):
        super().__init__()
        self.detector = None
        self.model = model
        self.output = output
        self.queue = queue
        self.running = True
        self.logger = get_logger('Worker')

    def run(self):
        self.detector = YoloDetector(self.model())
        while self.running:
            data: Wrapper = self.queue.get()
            if data is not None:
                self.logger.debug(f'got data: {data}')
                res = self.detector.detect(data.input_element)
                self.logger.debug(f'detect result: {res} will go to the output queue')
                self.output.put(Wrapper(data.id, data.input_element, res))
                self.logger.info(f'put result to the output queue {self.queue.qsize()}')

    def stop(self):
        self.running = False


class Wrapper(Generic[IN, OUT]):
    def __init__(self, id, input_element: IN, output_element: OUT):
        self.id = id
        self.input_element = input_element
        self.output_element = output_element


@Log4Py()
class ModelPool:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.join()
        for w in self.worker:
            w.join()
            w.close()

    def __init__(self, model, workers_num=2):
        """
        :param model: Detector
        :param workers_num: the number of workers to run in parallel
        """
        self.model = model
        self.workers_num = workers_num
        self.manage = Manager()
        self.input_queue = self.manage.Queue()
        self.output_queue = self.manage.Queue()
        self.worker = [Worker(model, self.input_queue, self.output_queue) for _ in range(workers_num)]
        for w in self.worker:
            w.start()

    def submit(self, data, id):
        self.input_queue.put(Wrapper(id, data, None))

    def stop(self):
        for w in self.worker:
            w.stop()

    def join(self):
        last_size = self.input_queue.qsize()
        while self.input_queue.qsize() > 0:
            if last_size != self.input_queue.qsize():
                self.logger.debug(f"still has {self.input_queue.qsize()}")
                last_size = self.input_queue.qsize()
        for w in self.worker:
            w.stop()
        self.logger.info("all workers has required to be stopped")
        for w in self.worker:
            self.logger.info(f"Process {w.name} over!")
            w.terminate()
