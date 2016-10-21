import asyncio
import logging
import settings
from datetime import datetime, timedelta
from discord.ext.commands import Bot, command, check
from pytz import utc, timezone
from commons import checks
from commons.messages import get as msg
from crawlers.hiddenstreet import HiddenStreet


log = logging.getLogger(settings.LOGGER_IRONBOT)


class Maple:
    """Maple Story commands"""

    def __init__(self, bot: Bot):
        self.b = bot
        self.hiddenstreet = HiddenStreet()
        self.server_start = None

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

        now = utc.localize(datetime.utcnow(), is_dst=True)
        req_intv = now - self.server_start
        next_spawn = timedelta(0, 14400 - (req_intv.total_seconds() % 14400))
        t = next_spawn.total_seconds()
        yield from self.b.say(msg('pierre.respawn').format(t // 3600, t % 3600 // 60, t % 60))

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

    @command(name='set-server-start')
    @check(checks.is_admin)
    @asyncio.coroutine
    def set_server_uptime(self, server_date: str = None, server_time: str = None, uptime: str = None):
        """Sets the time reference for server start.
        Syntax: !set-server-start <server start YYYY-MM-DD HH:MM:SS> <uptime DD:HH:MM:SS>
        Example: !set-server-start 2016-10-19 22:35:01 1:12:56:21"""

        if not all((server_date, server_time, uptime)):
            yield from self.b.say(msg('set-server-start.missing params'))
            return

        fmt = '%Y-%m-%d %H:%M:%S'
        server_datetime = "{} {}".format(server_date, server_time)
        try:
            london = timezone('Europe/London')
            sampling = london.localize(datetime.strptime(server_datetime, fmt), is_dst=False)
        except ValueError:
            yield from self.b.say(msg('set-server-start.parsing datetime').format(server_datetime))
            return

        try:
            d, h, m, s = [int(s) for s in uptime.split(':')]
        except ValueError:
            yield from self.b.say(msg('set-server-start.parsing uptime').format(uptime))
            return

        uptime_delta = timedelta(days=d, hours=h, minutes=m, seconds=s)
        self.server_start = sampling - uptime_delta
        yield from self.b.say(msg('set-server-start.done').format(self.server_start.strftime(fmt)))


def setup(bot: Bot) -> None:
    bot.add_cog(Maple(bot))
    log.info('{} cog loaded'.format(__name__))
