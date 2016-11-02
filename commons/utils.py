import asyncio
import logging
import os
import schedule
from discord.ext.commands import Bot
from .errors import catch_exceptions
from settings import HEARTBEAT_FILE, LOGGER_SCHEDULER, SCHEDULER_FREQUENCY

log = logging.getLogger(LOGGER_SCHEDULER)


@catch_exceptions
def touch(file_name, mode=0o666, dir_fd=None, **kwargs):
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(file_name, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(f.fileno()
                 if os.utime in os.supports_fd
                 else file_name, dir_fd=None if os.supports_fd else dir_fd, **kwargs)


@asyncio.coroutine
def scheduler_tick(ironbot: Bot):

    log.info('Global scheduler starting...')
    yield from ironbot.wait_until_ready()

    # heartbeat function
    schedule.every(2).minutes.do(touch, HEARTBEAT_FILE)

    log.info('Global scheduler started')

    log.info('Scheduled jobs are:')
    for job in schedule.jobs:
        log.info(' * {}: {}'.format(id(job), job))

    while not ironbot.is_closed:
        schedule.run_pending()
        yield from asyncio.sleep(SCHEDULER_FREQUENCY, loop=ironbot.loop)
