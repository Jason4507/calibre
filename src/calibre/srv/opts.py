#!/usr/bin/env python2
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2015, Kovid Goyal <kovid at kovidgoyal.net>'

from itertools import izip_longest
from collections import namedtuple, OrderedDict
from operator import attrgetter

Option = namedtuple('Option', 'name default longdoc shortdoc choices')

class Choices(frozenset):
    def __new__(cls, *args):
        self = super(Choices, cls).__new__(cls, args)
        self.default = args[0]
        return self

raw_options = (

    'Path to the SSL certificate file',
    'ssl_certfile', None,
    None,

    'Path to the SSL private key file',
    'ssl_keyfile', None,
    None,

    'Max. queued connections while waiting to accept',
    'request_queue_size', 5,
    None,

    'Timeout in seconds for accepted connections',
    'timeout', 10.0,
    None,

    'Total time in seconds to wait for clean shutdown',
    'shutdown_timeout', 5.0,
    None,

    'Minimum number of connection handling threads',
    'min_threads', 10,
    None,

    'Maximum number of simultaneous connections (beyond this number of connections will be dropped)',
    'max_threads', 500,
    None,

    'Allow socket pre-allocation, for example, with systemd socket activation',
    'allow_socket_preallocation', True,
    None,

    'Max. size of single HTTP header (in KB)',
    'max_header_line_size', 8.0,
    None,

    'Max. size of a HTTP request (in MB)',
    'max_request_body_size', 500.0,
    None,

    'Minimum size for which responses use data compression (in bytes)',
    'compress_min_size', 1024,
    None,

    'Decrease latency by using the TCP_NODELAY feature',
    'no_delay', True,
    'no_delay turns on TCP_NODELAY which decreases latency at the cost of'
    ' worse overall performance when sending multiple small packets. It'
    ' prevents the TCP stack from aggregating multiple small TCP packets.',

    'Use zero copy file transfers for increased performance',
    'use_sendfile', True,
    'This will use zero-copy in-kernel transfers when sending files over the network,'
    ' increasing performance. However, it can cause corrupted file transfers on some'
    ' broken filesystems. If you experience corrupted file transfers, turn it off.',
)
assert len(raw_options) % 4 == 0

options = []

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue=fillvalue)

for shortdoc, name, default, doc in grouper(4, raw_options):
    choices = None
    if isinstance(default, Choices):
        choices = default
        default = default.default
    options.append(Option(name, default, doc, shortdoc, choices))
options = OrderedDict([(o.name, o) for o in sorted(options, key=attrgetter('name'))])
del raw_options

class Options(object):

    __slots__ = tuple(name for name in options)

    def __init__(self, **kwargs):
        for opt in options.itervalues():
            setattr(self, opt.name, kwargs.get(opt.name, opt.default))
