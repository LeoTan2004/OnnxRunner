import pickle
import socket

import select

from deploy.onnx_runner.log4py import Log4Py
from deploy.onnx_runner.repository.repository import Repository, ID, D


class Wrapper:
    def __init__(self, uid: ID, data: D):
        self.uid = uid
        self.data = data

    def __repr__(self):
        return f'Wrapper(uid={self.uid}, data={self.data})'


@Log4Py()
class RemoteClient(Repository):
    """远程客户端，用于与远程服务器进行通信。使用UDP连接通信"""

    def serialize(self, obj):
        """序列化对象为字节流，使用pickle进行序列化"""
        return pickle.dumps(obj)

    def deserialize(self, data):
        """反序列化字节流为对象，使用pickle进行反序列化"""
        return pickle.loads(data)

    def read(self, uid: ID) -> D:
        try:
            r, w, e = select.select([self.client_socket], [], [], self.client_socket.gettimeout())
            if r:
                data, addr = self.client_socket.recvfrom(1024)
                res = self.deserialize(data)
                self.logger.info(f'Received from {addr}: {res}')
                return res
            else:
                self.logger.error('Timeout occurred while waiting for message.')
                return None
        except Exception as e:
            self.logger.error(f'Error receiving message: {e}')
            return None

    def write(self, uid: ID, data: D):

        obj = Wrapper(uid, data)
        try:
            serialized_message = self.serialize(obj)
            self.client_socket.sendto(serialized_message, self.server_address)
            self.logger.info(f'Sent: {obj}')
        except Exception as e:
            self.logger.error(f'Error sending message: {e}')

    def __enter__(self):
        # 发送接口
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(self.out_time)
        # 接收接口
        self.client_socket.bind(self.client_address)
        self.client_socket.settimeout(self.out_time)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client_socket.close()

    def __init__(self, server_host, server_port, out_time=5):
        """验证远程服务器是否可用"""
        self.server_host = server_host
        self.server_port = server_port
        self.server_address = (self.server_host, self.server_port)
        self.client_address = (self.server_host, self.server_port)
        self.out_time = out_time


if __name__ == '__main__':
    client = RemoteClient('127.0.0.1', 12345)
    client.__enter__()
    client.write('test', {'a': 1, 'b': 2})
    data = client.read('test')
    print(data)
