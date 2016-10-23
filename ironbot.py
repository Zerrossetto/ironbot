import asyncio
import logging.config
import schedule
import settings
from commons import messages, errors
from discord import DiscordException
from discord.ext.commands import Bot, Context

log = logging.getLogger(settings.LOGGER_IRONBOT)


@asyncio.coroutine
def scheduler_tick(ironbot: Bot):
    yield from ironbot.wait_until_ready()
    while not ironbot.is_closed:
        schedule.run_pending()
        yield from asyncio.sleep(1)


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
            log.exception('Failed to load extension')

    @ironbot.event
    @asyncio.coroutine
    def on_ready():

        log.info('Logged in as {} id={}'.format(ironbot.user.name, ironbot.user.id))

        log.info('Starting global scheduler\nScheduled jobs are:')
        for job in schedule.jobs:
            log.info(' * {}'.format(job))

    @ironbot.event
    @asyncio.coroutine
    def on_error(event):
        log.error('An error occurred for event "{}"'.format(event))

    @ironbot.event
    @asyncio.coroutine
    def on_command_error(error: DiscordException, ctx: Context):
        k = (type(error), type(ctx.message.channel), ctx.command.name)
        if k in errors.handled:
            log.debug('Handled command error: {}'.format(error))
            yield from ctx.bot.send_message(ctx.message.channel, errors.get(*k))
        else:
            log.warn('Unhandled command error: {}'.format(error))

    ironbot.loop.create_task(scheduler_tick(ironbot))
    ironbot.run(settings.DISCORD_TOKEN)


if __name__ == '__main__':
    main()
