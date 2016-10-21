import asyncio
import logging.config
import settings
import traceback
from commons import messages, errors
from discord import DiscordException
from discord.ext.commands import Bot, Context

log = logging.getLogger(settings.LOGGER_IRONBOT)


def main():

    logging.config.dictConfig(settings.LOGGING)
    log.info('Starting')
    messages.initialize()
    log.debug('Retrieved i18n dictionaries')
    log.debug(messages.msg_map)
    log.info('i18n tables loaded. Available languages are [{}]'.format(', '.join(messages.msg_map.keys())))
    ironbot = Bot(**settings.BOT)
    for ext in ('cogs.basic', 'cogs.maple'):
        try:
            ironbot.load_extension(ext)
        except Exception as e:
            log.error('Failed to load extension {}.\n{} - {}'.format(ext, type(e).__name__, e))
            log.error(traceback.extract_tb())

    @ironbot.event
    @asyncio.coroutine
    def on_ready():
        log.info('Logged in as {} id={}'.format(ironbot.user.name, ironbot.user.id))

    @ironbot.event
    @asyncio.coroutine
    def on_error(event):
        log.error('An error occurred: {}'.format(event))

    @ironbot.event
    @asyncio.coroutine
    def on_command_error(error: DiscordException, ctx: Context):
        k = (type(error), type(ctx.message.channel), ctx.command.name)
        if k in errors.handled:
            log.debug('Handled command error: {}'.format(error))
            yield from ctx.bot.send_message(ctx.message.channel, errors.get(*k))
        else:
            log.warn('Unhandled command error: {}'.format(error))

    ironbot.run(settings.DISCORD_TOKEN)

if __name__ == '__main__':
    main()
