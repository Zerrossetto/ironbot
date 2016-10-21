from discord.ext.commands import Context


def is_admin(ctx: Context) -> bool:
    channel = ctx.message.channel
    author = ctx.message.author
    return not channel.is_private and channel.permissions_for(author).administrator
