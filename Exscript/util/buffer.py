#
# Copyright (C) 2010-2017 Samuel Abels
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
A buffer object.
"""
from __future__ import absolute_import
from builtins import object
from builtins import str
from io import StringIO
from .cast import to_regexs


class MonitoredBuffer(object):

    """
    A specialized string buffer that allows for monitoring
    the content using regular expression-triggered callbacks.
    """

    def __init__(self, io=None):
        """
        Constructor.
        The data is stored in the given file-like object. If no object is
        given, or the io argument is None, a new StringIO is used.

        :type  io: file-like object
        :param io: A file-like object that is used for storing the data.
        """
        self.io = StringIO(u'') if io is None else io
        self.monitors = []
        self.clear()

    def __str__(self):
        """
        Returns the content of the buffer.
        """
        return self.io.getvalue()

    def size(self):
        """
        Returns the size of the buffer.

        :rtype: int
        :return: The size of the buffer in bytes.
        """
        return self.io.tell()

    def head(self, bytes):
        """
        Returns the number of given bytes from the head of the buffer.
        The buffer remains unchanged.

        :type  bytes: int
        :param bytes: The number of bytes to return.
        """
        oldpos = self.io.tell()
        self.io.seek(0)
        head = self.io.read(bytes)
        self.io.seek(oldpos)
        return head

    def tail(self, bytes):
        """
        Returns the number of given bytes from the tail of the buffer.
        The buffer remains unchanged.

        :type  bytes: int
        :param bytes: The number of bytes to return.
        """
        self.io.seek(max(0, self.size() - bytes))
        return self.io.read()

    def pop(self, bytes):
        """
        Like :class:`head()`, but also removes the head from the buffer.

        :type  bytes: int
        :param bytes: The number of bytes to return and remove.
        """
        self.io.seek(0)
        head = self.io.read(bytes)
        tail = self.io.read()
        self.io.seek(0)
        self.io.write(tail)
        self.io.truncate()
        return head

    def append(self, data):
        """
        Appends the given data to the buffer, and triggers all connected
        monitors, if any of them match the buffer content.

        :type  data: str
        :param data: The data that is appended.
        """
        self.io.write(data)
        if not self.monitors:
            return

        # Check whether any of the monitoring regular expressions matches.
        # If it does, we need to disable that monitor until the matching
        # data is no longer in the buffer. We accomplish this by keeping
        # track of the position of the last matching byte.
        buf = str(self)
        for item in self.monitors:
            regex_list, callback, bytepos, limit = item
            bytepos = max(bytepos, len(buf) - limit)
            for i, regex in enumerate(regex_list):
                match = regex.search(buf, bytepos)
                if match is not None:
                    item[2] = match.end()
                    callback(i, match)

    def clear(self):
        """
        Removes all data from the buffer.
        """
        self.io.seek(0)
        self.io.truncate()
        for item in self.monitors:
            item[2] = 0

    def add_monitor(self, pattern, callback, limit=80):
        """
        Calls the given function whenever the given pattern matches the
        buffer.

        Arguments passed to the callback are the index of the match, and
        the match object of the regular expression.

        :type  pattern: str|re.RegexObject|list(str|re.RegexObject)
        :param pattern: One or more regular expressions.
        :type  callback: callable
        :param callback: The function that is called.
        :type  limit: int
        :param limit: The maximum size of the tail of the buffer
                      that is searched, in number of bytes.
        """
        self.monitors.append([to_regexs(pattern), callback, 0, limit])
