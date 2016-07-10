import random
import asyncio
import logging
import logging.config
import os
from .hiddenstreet import HiddenStreet

logging.config.fileConfig(os.path.join('ironbot', 'logger.conf'),
                          disable_existing_loggers=False)
log = logging.getLogger('ironbot')

hidden_street = HiddenStreet()


def bind_to(bot):

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

    # @bot.command()
    # @asyncio.coroutine
    # def joined(member: discord.Member):
    #     """Says when a member joined."""
    #     yield from bot.say('{0.name} joined in {0.joined_at}'.format(member))

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
