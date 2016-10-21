from .messages import get as get_message
from discord import Channel, PrivateChannel, DiscordException
from discord.ext.commands.errors import CheckFailure
from typing import Generic

handled = {
    (CheckFailure, PrivateChannel, 'set-server-start'): 'error.set-server-start.pvt',
    (CheckFailure, Channel, 'set-server-start'): 'error.set-server-start.pvt'
}


def get(error: DiscordException, channel: Generic(Channel, PrivateChannel), command: str) -> str:
    k = (error, channel, command)
    if k in handled:
        return get_message(handled[k])
    else:
        raise ValueError('Error label not found')
