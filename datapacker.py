# -*- coding: utf-8 -*-

import struct
from utils.log import log

PROTO_HEADER_LEN = 16


class DataPacker(object):
    ''' Data Packer for net node.
    '''

    def __init__(self, proto_ver, server_ver):
        self.proto_ver = proto_ver
        self.server_ver = server_ver

    def pack(self, pid, msg):
        proto_ver = self.proto_ver
        server_ver = self.server_ver
        length = msg.__len__() + 4
        _pid = pid
        data = struct.pack('!4I', proto_ver, server_ver, length, _pid)
        data = data + msg
        return data

    def unpack(self, buf):
        try:
            header = struct.unpack('!4I', buf)
        except struct.error, e:
            log.error(e)
            return None

        proto_ver = header[0]
        server_ver = header[1]
        length = header[2] - 4
        pid = header[3]
        if proto_ver != self.proto_ver or server_ver != self.server_ver:
            return None
        return pid, length