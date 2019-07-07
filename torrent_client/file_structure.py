import asyncio
import functools
import os
from bisect import bisect_right
from typing import Iterable, BinaryIO, Tuple

from torrent_client.models import DownloadInfo


def delegate_to_executor(func):
    @functools.wraps(func)
    async def wrapper(self: 'FileStructure', *args, acquire_lock=True, **kwargs):
        if acquire_lock:
            await self.lock.acquire()
        try:
            return await self._loop.run_in_executor(None, functools.partial(func, self, *args, **kwargs))
        finally:
            if acquire_lock:
                self.lock.release()

    return wrapper


class FileStructure:
    def __init__(self, download_dir: str, download_info: DownloadInfo):
        self._download_info = download_info

        self._loop = asyncio.get_event_loop()
        self._lock = asyncio.Lock()
        self._descriptors = []
        self._offsets = []
        offset = 0

        try:
            for file in download_info.files:
                path = os.path.join(download_dir, download_info.suggested_name, *file.path)
                directory = os.path.dirname(path)
                if not os.path.isdir(directory):
                    os.makedirs(os.path.normpath(directory))
                if not os.path.isfile(path):
                    f = open(path, 'w')
                    f.close()

                f = open(path, 'r+b')
                f.truncate(file.length)

                self._descriptors.append(f)
                self._offsets.append(offset)
                offset += file.length
        except (OSError, IOError):
            for f in self._descriptors:
                f.close()
            raise

        self._offsets.append(offset)  # Fake entry for convenience

    @property
    def lock(self) -> asyncio.Lock:
        return self._lock

    def _iter_files(self, offset: int, data_length: int) -> Iterable[Tuple[BinaryIO, int, int]]:
        if offset < 0 or offset + data_length > self._download_info.total_size:
            raise IndexError('Data position out of range')

        # Find rightmost file which start offset less than or equal to `offset`
        index = bisect_right(self._offsets, offset) - 1

        while data_length != 0:
            file_start_offset = self._offsets[index]
            file_end_offset = self._offsets[index + 1]
            file_pos = offset - file_start_offset
            bytes_to_operate = min(file_end_offset - offset, data_length)

            descriptor = self._descriptors[index]
            yield descriptor, file_pos, bytes_to_operate

            offset += bytes_to_operate
            data_length -= bytes_to_operate
            index += 1

    @delegate_to_executor
    def read(self, offset: int, length: int):
        result = []
        for f, file_pos, bytes_to_operate in self._iter_files(offset, length):
            f.seek(file_pos)
            result.append(f.read(bytes_to_operate))
        return b''.join(result)

    @delegate_to_executor
    def write(self, offset: int, data: memoryview):
        for f, file_pos, bytes_to_operate in self._iter_files(offset, len(data)):
            f.seek(file_pos)
            f.write(data[:bytes_to_operate])

            data = data[bytes_to_operate:]

    @delegate_to_executor
    def flush(self, offset: int, length: int):
        for f, _, _ in self._iter_files(offset, length):
            f.flush()

    def close(self):
        for f in self._descriptors:
            f.close()
