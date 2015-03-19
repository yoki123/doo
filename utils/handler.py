# -*- coding: utf-8 -*-
import os
import _socket
import sys

try:
    import pwd
except:
    pass


class PathError(Exception):
    pass


class NotSupport(Exception):
    pass


def unlink(path):
    from errno import ENOENT

    try:
        os.unlink(path)
    except OSError, ex:
        if ex.errno != ENOENT:
            raise


def link(src, dest):
    from errno import ENOENT

    try:
        os.link(src, dest)
    except OSError, ex:
        if ex.errno != ENOENT:
            raise


def bind_unix_listener(path, backlog=50, user=None):
    pid = os.getpid()
    tempname = '%s.%s.tmp' % (path, pid)
    backname = '%s.%s.bak' % (path, pid)
    unlink(tempname)
    unlink(backname)
    link(path, backname)
    try:
        sock = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
        sock.setblocking(0)
        sock.bind(tempname)

        if user is not None:
            user = pwd.getpwnam(user)
            os.chown(tempname, user.pw_uid, user.pw_gid)
            os.chmod(tempname, 0600)
        sock.listen(backlog)
        os.rename(tempname, path)
        return sock
    finally:
        unlink(backname)


def mq_socket(socket_path):
    path = socket_path
    if type(path) != str:
        raise PathError(path)

    if path.startswith('tcp://'):
        s_url = path[6:]
        r = s_url.split(':')
        if len(r) != 2:
            raise PathError(path)
        host = r[0]
        port = int(r[1])
        return host, port

    elif path.startswith('ipc://'):
        if sys.platform == 'win32':
            raise NotSupport('unix domain socket unsupported on windows')
        unix_path = path[6:]
        return bind_unix_listener(unix_path)

    elif path.startswith('udp://'):
        raise PathError('udp unsupported')
    else:
        raise PathError(path)


if __name__ == '__main__':
    print mq_socket('tcp://127.0.0.1:8080')
    print mq_socket('ipc:///tmp/test')