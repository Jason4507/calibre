#!/usr/bin/env python2
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2015, Kovid Goyal <kovid at kovidgoyal.net>'

import os, ctypes, errno, socket
from io import DEFAULT_BUFFER_SIZE
from select import select

from calibre.constants import iswindows, isosx

def file_metadata(fileobj):
    try:
        fd = fileobj.fileno()
        return os.fstat(fd)
    except Exception:
        pass

def copy_range(src_file, start, size, dest):
    src_file.seek(start)
    while size > 0:
        data = src_file.read(min(size, DEFAULT_BUFFER_SIZE))
        dest.write(data)
        size -= len(data)
        del data


if iswindows:
    sendfile_to_socket = None
elif isosx:
    sendfile_to_socket = None
else:
    libc = ctypes.CDLL(None, use_errno=True)
    sendfile = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int64), ctypes.c_size_t, use_errno=True)(('sendfile64', libc))
    del libc

    def sendfile_to_socket(fileobj, offset, size, socket_file):
        off = ctypes.c_int64(offset)
        timeout = socket_file.gettimeout()
        if timeout == 0:
            return copy_range(fileobj, off.value, size, socket_file)
        total_sent = 0
        while size > 0:
            r, w, x = select([], [socket_file], [], timeout)
            if not w:
                raise socket.timeout('timed out in sendfile() waiting for socket to become writeable')
            sent = sendfile(socket_file.fileno(), fileobj.fileno(), ctypes.byref(off), size)
            if sent < 0:
                err = ctypes.get_errno()
                if err in (errno.ENOSYS, errno.EINVAL):
                    return copy_range(fileobj, off.value, size, socket_file)
                if err != errno.EAGAIN:
                    raise IOError((err, os.strerror(err)))
            elif sent == 0:
                break  # EOF
            else:
                size -= sent
                total_sent += sent
