import random
import asyncio
import logging
import logging.config
import os
from pytz import utc, timezone
from datetime import datetime, timedelta
from .hiddenstreet import HiddenStreet

logging.config.fileConfig(os.path.join('ironbot', 'logger.conf'),
                          disable_existing_loggers=False)
log = logging.getLogger('ironbot')

hidden_street = HiddenStreet()
server_start = None


def is_admin(ctx):
    author = ctx.message.author
    return ctx.message.channel.permissions_for(author).administrator


def bind_to(bot):
    """Binds basic IronBot commands to a bot instance"""

    @bot.event
    @asyncio.coroutine
    def on_ready():
        log.info('logged in as "{:s}" with app ID {:s}'.format(bot.user.name,
                                                               bot.user.id))

    @bot.command()
    @asyncio.coroutine
    def roll(dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            yield from bot.say('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        yield from bot.say(result)

    @bot.command(description='For when you wanna settle the score '
                             'some other way')
    @asyncio.coroutine
    def choose(*choices: str):
        """Chooses between multiple choices."""
        yield from bot.say(random.choice(choices))

    @bot.command()
    @asyncio.coroutine
    def repeat(times: int, *content):
        """Repeats a message multiple times."""
        if times > 5:
            yield from bot.say('No way I\'m repeating it that many times')
        else:
            for i in range(times):
                yield from bot.say(' '.join(content))

    @bot.group(pass_context=True)
    @asyncio.coroutine
    def cool(ctx):
        """Says if a user is cool.
        In reality this just checks if a subcommand is being invoked.
        """
        if ctx.invoked_subcommand is None:
            msg = 'No, {0.subcommand_passed} is not cool'
            yield from bot.say(msg.format(ctx))

    @cool.command(name='bot')
    @asyncio.coroutine
    def _bot():
        """Is the bot cool?"""
        yield from bot.say('Yes, the bot is cool.')

    @bot.command(name='mobstats')
    @asyncio.coroutine
    def monster_stats(*chuncks):
        """Finds stats for a monster put --exact (or -e for short) to \
have the exact match for the name you're looking for. Data is by kind \
concession from http://bbb.hidden-street.net/"""
        flag = chuncks[0] in ['--exact', '-e']
        if flag:
            name = ' '.join(chuncks[1:])
        else:
            name = ' '.join(chuncks)

        result = hidden_street.monsters_by_name(name, exact_match=flag)
        if len(result) == 0:
            yield from bot.say('No result for keyword "{}"'.format(name))
        elif len(result) > 3:
            n = '", "'.join([m.name for m in result])
            yield from bot.say('Too many results! '
                               'Right now I\'m getting "{}"'.format(n))
        else:
            tpl = '***{name}***\n' \
                  '**Level** {level} **EXP** {experience} ' \
                  '**HP** {health_points}\n' \
                  '**Elemental weakness** {weakness_to_magic} \n' \
                  '**Elemental resistance** {resistance_to_magic}\n ' \
                  '{link}'

            for monster in result:
                if monster.experience:
                    monster.experience *= 4
                mdict = monster.to_dict()
                mdict['link'] = 'http://bbb.hidden-street.net' \
                                '/monster/{}'.format(monster.name
                                                            .lower()
                                                            .replace(' ', '-')
                                                            .replace('\'', ''))
                message = tpl.format(**mdict)
                if monster.image_url:
                    message += '\n{}'.format(monster.image_url)
                yield from bot.say(message)

    @bot.command()
    @asyncio.coroutine
    def pierre():
        """Shows the next respawn time for Pierre."""

        global server_start

        if server_start is None:
            yield from bot.say('Server start date is still not set. '
                               'Use **!set-server-start** command first')
            return

        now = utc.localize(datetime.utcnow(), is_dst=True)
        req_intv = now - server_start
        next_spawn = timedelta(0, 14400 - (req_intv.total_seconds() % 14400))
        t = next_spawn.total_seconds()
        f = '**Pierre will respawn in approximately** {:.0f} hours, ' \
            '{:.0f} minutes and {:.0f} seconds'
        yield from bot.say(f.format(t // 3600, t % 3600 // 60, t % 60))

    @bot.command()
    @asyncio.coroutine
    def event():
        """A quick Halloween Event guide for the lazy Mapler"""
        yield from bot.say('**MapleRoyals Halloween Event 2016**\n'
                           '*October 15th ~ November 15th*\n\n'
                           '**Quick Guide:** https://mapleroyals.com/'
                           'forum/threads/pierre-the-clown.80732/\n\n'
                           'http://i.imgur.com/vTO05be.png')

    @bot.command(name='set-server-start', pass_context=True)
    @asyncio.coroutine
    def set_server_uptime(ctx,
                          server_date_str: str=None,
                          server_time_str: str=None,
                          uptime_str: str=None):
        """Sets the time reference for server start.\n
    Syntax: !set-server-start <server start YYYY-MM-DD HH:MM:SS> \
    <uptime DD:HH:MM:SS>\n
    Example: !set-server-start 2016-10-19 22:35:01 1:12:56:21"""

        global server_start

        if not is_admin(ctx):
            yield from bot.say('Sorry, you should be an admin to '
                               'use this command')
            return

        if server_date_str is None or \
            server_time_str is None or \
                uptime_str is None:
            yield from bot.say('Command parameters are missing \n'
                               'Example: *!set-server-start* 2016-10-19 '
                               '22:35:01 1:12:56:21')
            return

        sampling = None
        uptime = None
        fmt = '%Y-%m-%d %H:%M:%S'
        server_time_str = "{} {}".format(server_date_str, server_time_str)
        try:
            london = timezone('Europe/London')
            sampling = london.localize(datetime.strptime(server_time_str, fmt),
                                       is_dst=False)
        except ValueError:
            yield from bot.say('Error while parsing server time date "{:s}".\n'
                               'Format should be YYYY-MM-DD '
                               'HH:MM:SS'.format(server_time_str))
            return

        try:
            uptime = [int(s) for s in uptime_str.split(':')]
            if len(uptime) != 4:
                raise ValueError
        except ValueError:
            yield from bot.say('Error while parsing uptime '
                               'interval "{:s}". \nFormat should '
                               'be DD:HH:MM:SS'.format(uptime_str))
            return

        uptime = timedelta(days=uptime[0], hours=uptime[1],
                           minutes=uptime[2], seconds=uptime[3])
        server_start = sampling - uptime
        yield from bot.say('{:s} was set as '
                           'server start'.format(server_start.strftime(fmt)))
