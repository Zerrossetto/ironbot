import asyncio
import logging
import random
from discord.ext.commands import Bot, Context, command, group
from commons.messages import get as msg
from settings import LOGGER_IRONBOT


log = logging.getLogger(LOGGER_IRONBOT)


class Basic:
    """Basic commands from basic_bot tutorial"""

    def __init__(self, bot: Bot):
        self.b = bot

    @command()
    @asyncio.coroutine
    def roll(self, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            yield from self.b.say(msg('roll.wrong format'))
            return
    
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        yield from self.b.say(result)

    @command(description='For when you wanna settle the score some other way')
    @asyncio.coroutine
    def choose(self, *choices: str):
        """Chooses between multiple choices."""
        yield from self.b.say(random.choice(choices))

    @command()
    @asyncio.coroutine
    def repeat(self, times: int, *content):
        """Repeats a message multiple times."""
        if times > 5:
            yield from self.b.say(msg('repeat.no way'))
        else:
            for i in range(times):
                yield from self.b.say(' '.join(content))

    @group(pass_context=True)
    @asyncio.coroutine
    def cool(self, ctx: Context):
        """Says if a user is cool.
        In reality this just checks if a subcommand is being invoked.
        """
        if ctx.invoked_subcommand is None:
            yield from self.b.say(msg('cool.no').format(ctx))

    @cool.command(name='bot')
    @asyncio.coroutine
    def _bot(self):
        """Is the bot cool?"""
        yield from self.b.say(msg('cool.yes'))


def setup(bot: Bot) -> None:
    bot.add_cog(Basic(bot))
    log.info('{} cog loaded'.format(__name__))
