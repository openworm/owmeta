#!/usr/bin/env python3

import argparse
import asyncio
import logging
import os
import re
import signal
import sys
from contextlib import closing, suppress
from functools import partial
from typing import List

from torrent_client.control import ControlManager, ControlClient, ControlServer, DaemonExit, formatters
from torrent_client.models import TorrentInfo, TorrentState


logging.basicConfig(format='%(levelname)s %(asctime)s %(name)-23s %(message)s', datefmt='%H:%M:%S')


async def check_daemon_absence():
    try:
        async with ControlClient():
            pass
    except RuntimeError:
        pass
    else:
        raise RuntimeError('The daemon is already running')


def run_daemon(_):
    with closing(asyncio.get_event_loop()) as loop:
        loop.run_until_complete(check_daemon_absence())

        control = ControlManager()
        loop.run_until_complete(control.start())

        try:
            control.load_state()
        except Exception as err:
            logging.warning('Failed to load program state: %r', err)
        control.invoke_state_dumps()

        stopping = False

        def stop_daemon(server: ControlServer):
            nonlocal stopping
            if stopping:
                return
            stopping = True

            stop_task = asyncio.ensure_future(asyncio.wait([server.stop(), server.control.stop()]))
            stop_task.add_done_callback(lambda fut: loop.stop())

        control_server = ControlServer(control, stop_daemon)
        loop.run_until_complete(control_server.start())

        if os.name == 'posix':
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, partial(stop_daemon, control_server))

        loop.run_forever()


def show_handler(args):
    torrent_info = TorrentInfo.from_file(args.filename, download_dir=None)
    content_description = formatters.join_lines(
        formatters.format_title(torrent_info, True) + formatters.format_content(torrent_info))
    print(content_description, end='')


PATH_SPLIT_RE = re.compile(r'/|{}'.format(re.escape(os.path.sep)))


async def add_handler(args):
    torrents = [TorrentInfo.from_file(filename, download_dir=args.download_dir) for filename in args.filenames]

    if args.include:
        paths = args.include
        mode = 'whitelist'
    elif args.exclude:
        paths = args.exclude
        mode = 'blacklist'
    else:
        paths = None
        mode = None
    if mode is not None:
        if len(torrents) > 1:
            raise ValueError('Can\'t handle "--include" and "--exclude" when several files are added')
        torrent_info = torrents[0]
        if torrent_info.download_info.single_file_mode:
            raise ValueError("Can't select files in a single-file torrent")

        paths = [PATH_SPLIT_RE.split(path) for path in paths]
        torrent_info.download_info.select_files(paths, mode)

    async with ControlClient() as client:
        for info in torrents:
            await client.execute(partial(ControlManager.add, torrent_info=info))


async def control_action_handler(args):
    action = getattr(ControlManager, args.action)
    torrents = [TorrentInfo.from_file(filename, download_dir=None) for filename in args.filenames]
    # FIXME: Execute action with all torrents if torrents == []

    async with ControlClient() as client:
        for info in torrents:
            await client.execute(partial(action, info_hash=info.download_info.info_hash))


def status_server_handler(manager: ControlManager) -> List[TorrentState]:
    torrents = manager.get_torrents()
    torrents.sort(key=lambda info: info.download_info.suggested_name)
    return [TorrentState(torrent_info) for torrent_info in torrents]


async def status_handler(args):
    async with ControlClient() as client:
        torrent_states = await client.execute(status_server_handler)
    if not torrent_states:
        print('No torrents added')
        return

    paragraphs = [formatters.join_lines(formatters.format_title(state, args.verbose) +
                                        formatters.format_status(state, args.verbose))
                  for state in torrent_states]
    print('\n'.join(paragraphs).rstrip())


def stop_server_handler(_: ControlManager):
    raise DaemonExit()


async def stop_handler(_):
    async with ControlClient() as client:
        with suppress(DaemonExit):
            await client.execute(stop_server_handler)


DEFAULT_DOWNLOAD_DIR = './'


def run_in_event_loop(coro_function, args):
    with closing(asyncio.get_event_loop()) as loop:
        loop.run_until_complete(coro_function(args))


def main():
    parser = argparse.ArgumentParser(description='A prototype of BitTorrent client (console management tool)')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug messages')
    parser.set_defaults(func=lambda args: print('Use option "--help" to show usage.', file=sys.stderr))
    subparsers = parser.add_subparsers(description='Specify an action before "--help" to show parameters for it.',
                                       metavar='ACTION', dest='action')

    subparser = subparsers.add_parser('start', help='Start the daemon')
    subparser.set_defaults(func=run_daemon)

    subparser = subparsers.add_parser('stop', help='Stop the daemon')
    subparser.set_defaults(func=partial(run_in_event_loop, stop_handler))

    subparser = subparsers.add_parser('show', help="Show contents of a torrent file "
                                                   "(you don't need to start the daemon for that)")
    subparser.add_argument('filename', help='Torrent file name')
    subparser.set_defaults(func=show_handler)

    subparser = subparsers.add_parser('add', help='Add torrent from file')
    subparser.add_argument('filenames', nargs='+',
                           help='Torrent file names')
    subparser.add_argument('-d', '--download-dir', default=DEFAULT_DOWNLOAD_DIR,
                           help='Download directory')
    group = subparser.add_mutually_exclusive_group()
    group.add_argument('--include', action='append',
                       help='Download only files and directories specified in "--include" options')
    group.add_argument('--exclude', action='append',
                       help='Download all files and directories except those that specified in "--exclude" options')
    subparser.set_defaults(func=partial(run_in_event_loop, add_handler))

    control_commands = ['pause', 'resume', 'remove']
    for command_name in control_commands:
        subparser = subparsers.add_parser(command_name, help='{} torrent from file'.format(command_name.capitalize()))
        subparser.add_argument('filenames', nargs='+',
                               help='Torrent file names')
        subparser.set_defaults(func=partial(run_in_event_loop, control_action_handler))

    subparser = subparsers.add_parser('status', help='Show status of all torrents')
    subparser.add_argument('-v', '--verbose', action='store_true',
                           help='Increase output verbosity')
    subparser.set_defaults(func=partial(run_in_event_loop, status_handler))

    arguments = parser.parse_args()
    if not arguments.debug:
        logging.disable(logging.INFO)
    try:
        arguments.func(arguments)
    except (IOError, ValueError, RuntimeError) as e:
        print('Error: {}'.format(e), file=sys.stderr)


if __name__ == '__main__':
    sys.exit(main())
