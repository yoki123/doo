# -*- coding: utf-8 -*-

import socket
import traceback
import sys

from gevent.lock import Semaphore
from gevent import queue

from datapacker import PROTO_HEADER_LEN
from factory import factory
from utils.log import log


SOCK_RECV_SIZE = 1024

_os = sys.platform


def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)


class Connection(object):
    factory = factory

    def __init__(self, socket, address):
        self._socket = socket
        self._send_lock = Semaphore()
        self._inbox = queue.Queue()
        self.address = address  # the address of the local endpoint
        self.sid = 0

        if _os == 'linux2':
            set_keepalive_linux(socket)

        self.on_connect()

    def getaddress(self):
        return self.address  # example: ('127.0.0.1', 12345)

    def recv(self, buf_size):
        return self._socket.recv(buf_size)

    def send(self, msg):
        self._send_lock.acquire()
        try:
            self._socket.sendall(msg)
        finally:
            self._send_lock.release()

    def close(self):
        self.on_close()
        self._socket.close()

    def __del__(self):
        try:
            self._socket.close()
        except:
            pass

    def on_connect(self):
        self.sid = self.factory.conn_pool.connection_made(self, self.address)

    def on_close(self):
        self.factory.conn_pool.connection_lose(self.sid)

    def write_response(self, pid, msg):
        buff = self.factory.packer.pack(pid, msg)
        return self.send(buff)


class ConnectionPool(object):
    def __init__(self):
        self._connections = {}
        self.sid = 0

    def connection_made(self, sock, address):
        self.sid += 1
        if self.sid in self._connections:
            raise Exception('connections conflict')
        self._connections[self.sid] = sock
        log.debug('%s:%s accept, sid=%d' % (address[0], address[1], self.sid))
        return self.sid


    def connection_lose(self, sid):
        sock = self._connections.get(sid, None)
        if not sock:
            raise Exception('connections not exist')
        log.debug('%s:%s lose, sid=%d' % (sock.address[0], sock.address[1], sock.sid))
        self._connections.pop(sid)

    def get_connection(self, sid):
        return self._connections.get(sid, None)


    def push_msg(self, pid, msg, target_list):
        for target in target_list:
            try:
                conn = self._connections.get(target, None)
                if conn:
                    conn.write_response(pid, msg)
            except Exception, e:
                log.error('%s\n%s' % (e, traceback.format_exc()))


class NetServer(object):
    '''Net Server
    This class is assumed to be used with gevent StreamServer.

    '''
    factory = factory

    def __init__(self, *args, **kwargs):
        # wrapper base socket
        _conn = Connection(*args)
        self._run(_conn, args[1])


    def _run(self, conn, address):
        buff = ''
        while True:
            try:
                data = conn.recv(SOCK_RECV_SIZE)
                assert (data)
            except Exception, e:
                conn.close()
                break

            if len(data) == 0:
                conn.close()

            buff += data
            if len(buff) < PROTO_HEADER_LEN:
                continue

            result = self.factory.packer.unpack(buff[0:PROTO_HEADER_LEN])
            if not result:
                log.debug('error package')
                conn.close()
                break

            pid, length = result
            request = buff[PROTO_HEADER_LEN:PROTO_HEADER_LEN + length]
            if request.__len__() < length:
                log.debug('data lose')
                conn.close()
                break

            buff = buff[PROTO_HEADER_LEN + length:]

            response = self.factory.router.call(pid, conn.sid, buff)
            if response:
                conn.write_response(pid, response)
