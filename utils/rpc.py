# -*- coding: utf-8 -*-

import struct
import gevent
from gevent import socket, queue
from gevent.lock import Semaphore
import msgpack as packer


RPC_REQUEST = 0
RPC_RESPONSE = 1
RPC_NOTICE = 2

SOCKET_RECV_SIZE = 1024
RPC_DATA_MAX_LENGTH = 2147483647


class RPCProtocolError(Exception):
    pass


class RPCError(Exception):
    pass


class _RPCConnection:
    def __init__(self, socket):
        self._socket = socket
        self._send_lock = Semaphore()
        self.mq = queue.Queue()

    def recv(self, buf_size):
        return self._socket.recv(buf_size)

    def send(self, msg):
        self._send_lock.acquire()
        try:
            self._socket.sendall(msg)
        finally:
            self._send_lock.release()

    def __del__(self):
        try:
            self._socket.close()
        except:
            pass


class RPCServer:
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], gevent.socket.socket):
            self._run(_RPCConnection(args[0]))
        self._buff = ''

    def __call__(self, sock, _):
        self._run(sock)

    def _run(self, conn):
        while True:
            data = conn.recv(SOCKET_RECV_SIZE)
            if not data:
                break

            self._buff += data
            if len(self._buff) >= 4:
                data_length, = struct.unpack('!i', self._buff[:4])

            if len(self._buff[4:]) < data_length:
                continue
            else:
                request = self._buff[4:4 + data_length]
                self._buff = self._buff[4 + data_length:]  # _buff = ''

                try:
                    req = packer.loads(request)
                except Exception:
                    continue

                (_, msg_id, method_name, args) = req
                method = self.get_method(method_name)
                try:
                    ret = method(*args)
                except Exception, e:
                    print(e)
                    continue
                else:
                    msg = (RPC_RESPONSE, msg_id, None, ret)
                    buf = packer.dumps(msg)
                    conn.send(struct.pack("!i", len(buf)) + buf)


    def get_method(self, method_name):
        return getattr(self, method_name)


class RPCClient:
    def __init__(self, host, port):
        self._msg_id = 0
        self._socket = socket.create_connection((host, port))
        self.buff = ''

    def call(self, method, *args):
        self._msg_id += 1
        req = (RPC_REQUEST, self._msg_id, method, args)
        buf = packer.dumps(req)
        self._socket.sendall(struct.pack("!i", len(buf)) + buf)
        while True:
            data = self._socket.recv(SOCKET_RECV_SIZE)
            self.buff += data
            if len(self.buff) >= 4:
                data_length, = struct.unpack('!i', self.buff[:4])

            if len(self.buff[4:]) < data_length:
                continue
            else:
                request = self.buff[4:4 + data_length]
                self.buff = self.buff[4 + data_length:]

                try:
                    response = packer.loads(request)
                    break
                except Exception:
                    continue
        return self._parse_response(response)

    def _parse_response(self, response):
        if (len(response) != 4 or response[0] != RPC_RESPONSE):
            raise RPCProtocolError('Invalid protocol')

        (_, msg_id, error, result) = response

        if msg_id != self._msg_id:
            raise RPCError('Invalid Message ID')

        if error:
            raise RPCError(str(error))

        return result
