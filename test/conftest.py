import pytest

import asyncio
import threading

from cloudbot import setup_bot
from cloudbot.util import paths
from cloudbot.bot import CloudBot


class ThreadFixture(object):
    def stop(self):
        self.thread.join(15)

    @property
    def alive(self):
        return self.thread.is_alive()


@pytest.fixture(scope='session')
def server(request):
    """Return a miniircd server bound to localhost
    """
    from expp.cloudbot.test import miniircd
    class IRCOptions(object):
        listen = '127.0.0.1'
        ports = [6667]
        password = None
        ssl_pem_file = None
        motd = None
        verbose = False
        debug = False
        logdir = None
        chroot = False
        setuid = False
        statedir = None
        ssl = False

    server = miniircd.Server(IRCOptions())
    thread = threading.Thread(target=server.start)
    thread.daemon = True
    thread.start()

    def fin():
        thread.join(5)
    request.addfinalizer(fin)

    return server


@pytest.yield_fixture(scope='session')
def bot(request, server):
    """Return a CloudBot instance connected to a local irc server
    """
    def run_bot(loop):
        asyncio.set_event_loop(loop)

        paths.set_path('config_file', 'test/conf.test.json')
        paths.set_path('log_dir', 'test/logs')
        paths.set_path('data_dir', 'test/data')
        paths.reload_paths(daemon=True)
        setup_bot()

        bot = CloudBot(loop)

    thread = threading.Thread(target=run_bot, args=(asyncio.get_event_loop(),))
    thread.daemon = True
    thread.start()

    def fin():
        thread.join(5)
    request.addfinalizer(fin)

    yield bot
