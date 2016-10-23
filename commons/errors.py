import functools
import logging
import settings
import traceback
from .messages import get as get_message
from discord import Channel, PrivateChannel, DiscordException
from discord.ext.commands.errors import CheckFailure
from typing import Generic


log = logging.getLogger(settings.LOGGER_IRONBOT)

handled = {
    (CheckFailure, PrivateChannel, 'set-server-start'): 'error.set-server-start.pvt',
    (CheckFailure, Channel, 'set-server-start'): 'error.set-server-start.pub'
}


def get(error: DiscordException, channel: Generic(Channel, PrivateChannel), command: str) -> str:
    k = (error, channel, command)
    if k in handled:
        return get_message(handled[k])
    else:
        raise ValueError('Error label not found')


def catch_exceptions(job_func):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            job_func(*args, **kwargs)
        except AssertionError as ae:
            log.warn(ae)
            log.warn(traceback.extract_tb())
        except Exception as e:
            log.error(e)
            log.error(traceback.extract_tb())

    return wrapper
