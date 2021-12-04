# -*- coding: utf-8 -*-
# Based on https://gist.github.com/obskyr/b9d4b4223e7eaf4eedcd9defabb34f13
# released into the public domain

from io import BytesIO, SEEK_SET, SEEK_END


class RequestsResponseStream:
    '''
    Provides a :term:`file-like object` by wrapping a `requests` response iterator.
    Requires the request is made with ``stream=True``.

    Use the response as a context manager or call close when finished with this stream.
    '''

    def __init__(self, response, chunksize=4096):
        self._bytes = BytesIO()
        self._iterator = response.iter_content(chunksize)
        self._response = response

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position += self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self):
        return self._bytes.tell()

    def read(self, size=None):
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        self._bytes.seek(left_off_at)
        return self._bytes.read(size)

    def seek(self, position, whence=SEEK_SET):
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()

    def close(self):
        self._response.close()
        self._bytes.close()
