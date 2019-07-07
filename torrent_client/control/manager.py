import asyncio
import copy
import logging
import os
import pickle
from typing import Dict, List, Optional

from torrent_client.algorithms import TorrentManager
from torrent_client.models import generate_peer_id, TorrentInfo, TorrentState
from torrent_client.network import PeerTCPServer
from torrent_client.utils import import_signals


QObject, pyqtSignal = import_signals()


__all__ = ['ControlManager']


state_filename = os.path.expanduser('~/.torrent_gui_state')


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ControlManager(QObject):
    if pyqtSignal:
        torrents_suggested = pyqtSignal(list)
        torrent_added = pyqtSignal(TorrentState)
        torrent_changed = pyqtSignal(TorrentState)
        torrent_removed = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()

        self._our_peer_id = generate_peer_id()

        self._torrents = {}          # type: Dict[bytes, TorrentInfo]
        self._torrent_managers = {}  # type: Dict[bytes, TorrentManager]

        self._server = PeerTCPServer(self._our_peer_id, self._torrent_managers)

        self._torrent_manager_executors = {}  # type: Dict[bytes, asyncio.Task]
        self._state_updating_executor = None  # type: Optional[asyncio.Task]

        self.last_torrent_dir = None   # type: Optional[str]
        self.last_download_dir = None  # type: Optional[str]

    def get_torrents(self) -> List[TorrentInfo]:
        return list(self._torrents.values())

    async def start(self):
        await self._server.start()

    def _start_torrent_manager(self, torrent_info: TorrentInfo):
        info_hash = torrent_info.download_info.info_hash

        manager = TorrentManager(torrent_info, self._our_peer_id, self._server.port)
        if pyqtSignal:
            manager.state_changed.connect(lambda: self.torrent_changed.emit(TorrentState(torrent_info)))
        self._torrent_managers[info_hash] = manager
        self._torrent_manager_executors[info_hash] = asyncio.ensure_future(manager.run())

    def add(self, torrent_info: TorrentInfo):
        info_hash = torrent_info.download_info.info_hash
        if info_hash in self._torrents:
            raise ValueError('This torrent is already added')

        if not torrent_info.paused:
            self._start_torrent_manager(torrent_info)
        self._torrents[info_hash] = torrent_info

        if pyqtSignal:
            self.torrent_added.emit(TorrentState(torrent_info))

    def resume(self, info_hash: bytes):
        if info_hash not in self._torrents:
            raise ValueError('Torrent not found')
        torrent_info = self._torrents[info_hash]
        if not torrent_info.paused:
            raise ValueError('The torrent is already running')

        self._start_torrent_manager(torrent_info)

        torrent_info.paused = False

        if pyqtSignal:
            self.torrent_changed.emit(TorrentState(torrent_info))

    async def _stop_torrent_manager(self, info_hash: bytes):
        manager_executor = self._torrent_manager_executors[info_hash]
        manager_executor.cancel()
        try:
            await manager_executor
        except asyncio.CancelledError:
            pass
        del self._torrent_manager_executors[info_hash]

        manager = self._torrent_managers[info_hash]
        del self._torrent_managers[info_hash]
        await manager.stop()

    async def remove(self, info_hash: bytes):
        if info_hash not in self._torrents:
            raise ValueError('Torrent not found')
        torrent_info = self._torrents[info_hash]

        del self._torrents[info_hash]
        if not torrent_info.paused:
            await self._stop_torrent_manager(info_hash)

        if pyqtSignal:
            self.torrent_removed.emit(info_hash)

    async def pause(self, info_hash: bytes):
        if info_hash not in self._torrents:
            raise ValueError('Torrent not found')
        torrent_info = self._torrents[info_hash]
        if torrent_info.paused:
            raise ValueError('The torrent is already paused')

        await self._stop_torrent_manager(info_hash)

        torrent_info.paused = True

        if pyqtSignal:
            self.torrent_changed.emit(TorrentState(torrent_info))

    def _dump_state(self):
        torrent_list = []
        for manager, torrent_info in self._torrents.items():
            torrent_info = copy.copy(torrent_info)
            torrent_info.download_info = copy.copy(torrent_info.download_info)
            torrent_info.download_info.reset_run_state()
            torrent_list.append(torrent_info)

        try:
            with open(state_filename, 'wb') as f:
                pickle.dump((self.last_torrent_dir, self.last_download_dir, torrent_list), f)
            logger.info('state saved (%s torrents)', len(torrent_list))
        except Exception as err:
            logger.warning('Failed to save state: %r', err)

    STATE_UPDATE_INTERVAL = 5 * 60

    async def _execute_state_updates(self):
        while True:
            await asyncio.sleep(ControlManager.STATE_UPDATE_INTERVAL)

            self._dump_state()

    def invoke_state_dumps(self):
        self._state_updating_executor = asyncio.ensure_future(self._execute_state_updates())

    def load_state(self):
        if not os.path.isfile(state_filename):
            return

        with open(state_filename, 'rb') as f:
            self.last_torrent_dir, self.last_download_dir, torrent_list = pickle.load(f)

        for torrent_info in torrent_list:
            self.add(torrent_info)
        logger.info('state recovered (%s torrents)', len(torrent_list))

    async def stop(self):
        await self._server.stop()

        tasks = list(self._torrent_manager_executors.values())
        if self._state_updating_executor is not None:
            tasks.append(self._state_updating_executor)

        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.wait(tasks)

        if self._torrent_managers:
            await asyncio.wait([manager.stop() for manager in self._torrent_managers.values()])

        if self._state_updating_executor is not None:  # Only if we have loaded starting state
            self._dump_state()
