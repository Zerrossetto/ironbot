import os
from configparser import ConfigParser
from discord.ext.commands import Bot
import ironbot.commands


def main():
    conf = ConfigParser()
    conf.read(os.path.join('ironbot', 'bot.conf'))
    client = Bot(command_prefix=conf['default']['command_prefix'],
                 description=conf['default']['description'])
    ironbot.commands.bind_to(client)
    client.run(os.environ['DISCORD_TOKEN'])

if __name__ == '__main__':
    main()
