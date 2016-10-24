import aiohttp
import asyncio
import logging
import schedule
import settings
from datetime import datetime, timedelta
from discord import ChannelType
from discord.ext.commands import Bot, command, check
from pytz import utc, timezone
from commons import checks
from commons.messages import get as msg
from commons.errors import catch_exceptions
from crawlers.hiddenstreet import HiddenStreet


log = logging.getLogger(settings.LOGGER_IRONBOT)
schedule_log = logging.getLogger(settings.LOGGER_SCHEDULER)


def format_pierre_interval(hours: int, minutes: int, seconds: int) -> str:
    hours, minutes, seconds = [int(round(n)) for n in (hours, minutes, seconds)]
    if seconds == 60:
        minutes += 1
        seconds = 0
    if minutes == 60:
        hours += 1
        minutes = 0
    suffix = ''.join([n for n, t in (('h', hours), ('m', minutes), ('s', seconds)) if t > 0])
    fmt = msg('pierre.respawn.{}'.format(suffix))
    data = dict(h_time=hours,
                hour=msg('time.hours' if hours > 1 else 'time.hour'),
                m_time=minutes,
                minute=msg('time.minutes' if minutes > 1 else 'time.minute'),
                s_time=seconds,
                second=msg('time.seconds' if seconds > 1 else 'time.second'))
    return fmt.format(**data)


class Maple:
    """Maple Story commands"""

    def __init__(self, bot: Bot):

        self.b = bot
        self.hiddenstreet = HiddenStreet(bot.loop)

        if settings.SET_SERVER_START_DEFAULT is None:
            self.server_start = None
            log.warn('Server start wasn\'t set at bot start. Defaulting to None')
            self.cog_is_initializing = False
        else:
            bot.loop.create_task(self._init_server_start())

    @catch_exceptions
    def pierre_alert_job(self, first_run=False):

        assert not self.b.is_closed or self.b.is_logged_in, 'Connection to host is closed, skipping execution'
        assert self.server_start is not None, 'Server start is not currently set'

        t = self.pierre_next_respawn().total_seconds()

        for destination in [server.default_channel
                            for server in self.b.servers
                            if server.default_channel.type == ChannelType.text]:
            message = format_pierre_interval(t // 3600, t % 3600 // 60, t % 60)
            self.b.loop.create_task(self.b.send_message(destination, message))
            schedule_log.info('Pierre alert sent to channel {}: {}'.format(destination.name, message))

        if first_run:
            schedule_log.info('First run, now rescheduling for next four hours')
            schedule.every(4).hours.do(self.pierre_alert_job, first_run=False)
            return schedule.CancelJob
        else:
            schedule_log.info('Standard run, terminating normally')

    def pierre_next_respawn(self) -> timedelta:
        now = utc.localize(datetime.utcnow(), is_dst=True)
        req_interval = now - self.server_start
        return timedelta(0, 14400 - (req_interval.total_seconds() % 14400))

    @asyncio.coroutine
    def _init_server_start(self):
        self.cog_is_initializing = True
        with aiohttp.ClientSession() as client:
            response = yield from client.get(settings.SET_SERVER_START_DEFAULT)
            args = yield from response.text()
            args = args.rstrip()

        yield from self.set_server_uptime.callback(self, *args.split())
        self.cog_is_initializing = False

    @command()
    @asyncio.coroutine
    def event(self):
        """A quick Halloween Event guide for the lazy Mapler"""
        yield from self.b.say('**MapleRoyals Halloween Event 2016**\n'
                              '*October 15th ~ November 15th*\n\n'
                              '**Quick Guide:** https://mapleroyals.com/'
                              'forum/threads/pierre-the-clown.80732/\n\n'
                              'http://i.imgur.com/vTO05be.png')

    @command()
    @asyncio.coroutine
    def pierre(self):
        """Shows the next respawn time for Pierre."""

        if self.server_start is None:
            yield from self.b.say(msg('pierre.date not set').format(**settings.BOT))
            return

        t = self.pierre_next_respawn().total_seconds()
        yield from self.b.say(format_pierre_interval(t // 3600, t % 3600 // 60, t % 60))

    @command(name='mobstats')
    @asyncio.coroutine
    def monster_stats(self, *words):
        """Finds stats for a monster put --exact (or -e for short) to \
have the exact match for the name you're looking for. Data is by kind \
concession from http://bbb.hidden-street.net/"""
        flag = words[0] in ['--exact', '-e']
        if flag:
            name = ' '.join(words[1:])
        else:
            name = ' '.join(words)

        result = self.hiddenstreet.monsters_by_name(name, exact_match=flag)
        if len(result) == 0:
            yield from self.b.say(msg('monster_stats.no results').format(name))
        elif len(result) > 3:
            n = '", "'.join([m.name for m in result])
            yield from self.b.say(msg('monster_stats.too many').format(n))
        else:

            for monster in result:
                if monster.experience:
                    monster.experience *= 4
                mdict = monster.to_dict
                mdict['link'] = 'http://bbb.hidden-street.net/monster/{}'.format(
                    monster.name.lower().replace(' ', '-').replace('\'', ''))
                message = msg('monster_stats.result').format(**mdict)
                if monster.image_url:
                    message += '\n{}'.format(monster.image_url)
                yield from self.b.say(message)

    @command(name='set-server-start', hidden=True)
    @check(checks.is_admin)
    @asyncio.coroutine
    def set_server_uptime(self, server_date: str = None, server_time: str = None, uptime: str = None):
        """Sets the time reference for server start.
        Syntax: !set-server-start <server start YYYY-MM-DD HH:MM:SS> <uptime DD:HH:MM:SS>
        Example: !set-server-start 2016-10-19 22:35:01 1:12:56:21"""

        if not all((server_date, server_time, uptime)):
            if self.b.is_logged_in:
                yield from self.b.say(msg('set-server-start.missing params'))
            else:
                log.error(msg('set-server-start.missing params'))
            return

        fmt = '%Y-%m-%d %H:%M:%S'
        server_datetime = "{} {}".format(server_date, server_time)
        try:
            london = timezone('Europe/London')
            sampling = london.localize(datetime.strptime(server_datetime, fmt), is_dst=False)
        except ValueError:
            if self.b.is_logged_in:
                yield from self.b.say(msg('set-server-start.parsing datetime').format(server_datetime))
            else:
                log.error(msg('set-server-start.parsing datetime').format(server_datetime))
            return

        try:
            d, h, m, s = [int(s) for s in uptime.split(':')]
        except ValueError:
            if self.b.is_logged_in:
                yield from self.b.say(msg('set-server-start.parsing uptime').format(uptime))
            else:
                log.error(msg('set-server-start.parsing uptime').format(uptime))
            return

        uptime_delta = timedelta(days=d, hours=h, minutes=m, seconds=s)
        self.server_start = sampling - uptime_delta

        if self.cog_is_initializing:  # this is to let me use this function also to set server_start in the init phase
            log.info(msg('set-server-start.done').format(self.server_start.strftime(fmt)))
        else:
            yield from self.b.say(msg('set-server-start.done').format(self.server_start.strftime(fmt)))

        # Scheduling jobs for automatic Pierre notifications
        # this is done every time the server time is being adjusted
        schedule.clear()
        remaining_respawn_time = self.pierre_next_respawn()

        for interval in (timedelta(minutes=30), timedelta(minutes=20),
                         timedelta(minutes=10), timedelta(minutes=5)):
            if remaining_respawn_time > interval:
                t = (remaining_respawn_time - interval).total_seconds()
            else:
                t = (remaining_respawn_time + timedelta(hours=4) + interval).total_seconds()
            schedule.every(t).seconds.do(self.pierre_alert_job, first_run=True)

def setup(bot: Bot) -> None:
    bot.add_cog(Maple(bot))
    log.info('{} cog loaded'.format(__name__))
