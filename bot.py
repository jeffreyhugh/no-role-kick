import discord
import asyncio
from discord.ext import commands, tasks
import json
import sys
from datetime import datetime
import typing

def tpfx(code=0):
    '''Return the current time to use in volatile logging'''
    # Codes (integers)
    # 3 - fatal
    # 2 - error
    # 1 - warning
    # 0 - info (default)
    t = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    if code == 3:
        tag = "[FATAL] "
    elif code == 2:
        tag = "[ERROR] "
    elif code == 1:
        tag = "[WARN]  "
    else:
        tag = "[INFO]  "

    return (tag + t + ">")

# Attempt to read a bot config file (called bot_config.json). If the file does not exist, create it and quit.
try:
    with open('bot_config.json','r') as cfg_file:
        bot_config = json.load(cfg_file)
except FileNotFoundError:
    bot_config = {
        "token":"YOUR_TOKEN_HERE",
        "prefix":"!!",
        "good_rxn":"🟩",
        "bad_rxn":"🟥"
    }
    with open('bot_config.json','w') as cfg_file:
        json.dump(bot_config, cfg_file)
        print("{} Wrote template bot_config.json, please update before running again".format(tpfx(3)))
        print("{} Please read https://q5f.net/tutorial/dbt if you need help making a bot application and token".format(tpfx()))
    sys.exit()

# Attempt to read a server config file (called server_config.json). If the file does not exist, create an empty dictionary in memory.
try:
    with open('server_config.json','r') as cfg_file:
        server_config = json.load(cfg_file)
except FileNotFoundError:
    server_config = {}

# Setup for Discord bot
bot = commands.Bot(command_prefix=commands.when_mentioned_or(bot_config["prefix"]))
bot.remove_command('help')

def write_server_config():
    '''Dump the server config in memory to a file'''
    with open('server_config.json','w') as cfg_file:
        json.dump(server_config, cfg_file)

async def no_pm(ctx):
    '''Check to make sure the user is not using specific commands in PMs'''
    if ctx.guild is None:
        raise commands.errors.NoPrivateMessage()
    return ctx.guild

async def perms(ctx):
    '''Check to make sure the user has the Manage Guild permission for certain commands'''
    gperms = ctx.author.guild_permissions
    if not gperms.manage_guild:
        raise commands.errors.MissingPermissions(["Manage Guild"])
    return gperms.manage_guild

# When the bot is fully logged in and the cache is created, log it.
@bot.event
async def on_ready():
    print("{} {} is fully logged in and ready".format(tpfx(),bot.user))

# If the bot disconnects from Discord, log it.
@bot.event
async def on_disconnect():
    print("{} Disconnected from Discord".format(tpfx(1)))

# If the bot resumes its connection to Discord, log it.
@bot.event
async def on_resumed():
    print("{} Resumed connection to Discord".format(tpfx()))

@bot.command(name="help")
async def _help(ctx, cmd=None):
    '''Help command. Self-explanatory'''
    await ctx.message.add_reaction(bot_config["good_rxn"])
    if cmd == None:
        await ctx.send('''```For help about a specific command, type {}help <command_name>
help - show this command
timeout <time_in_minutes> - set the amount of time to wait before kicking users without roles
toggle - toggle whether or not to kick users who don't have roles```'''.format(bot_config["prefix"]))
    elif cmd.lower() == "timeout":
        await ctx.send('''```timeout - set the amount of time to wait before kicking users without roles.
argument <time_in_minutes> - set the time in minutes to wait before kicking users. If not specified, display the current value.
note - only users with the Manage Guild permission can use this command.
note - this command cannot be used in PMs.
example - {}timeout 20```'''.format(bot_config["prefix"]))
    elif cmd.lower() == "toggle":
        await ctx.send('''```toggle - toggle whether or not to kick users who don't have roles
note - only users with the Manage Guild permission can use this command.
note - this command cannot be used in PMs.
example - {}toggle```'''.format(bot_config["prefix"]))
    else:
        await ctx.send("No further help available for that command.")

@bot.command(name="timeout", aliases=["delay"])
@commands.check(no_pm)
@commands.check(perms)
async def _timeout(ctx, timeout: typing.Optional[int] = None):
    '''Set the timeout for a specific server. Timeout values must be greater than or equal to 1 minute. Only users with the Manage Guild permission can use this command.'''
    if timeout == None:
        await ctx.message.add_reaction(bot_config["good_rxn"])
        await ctx.send("\{}Current timeout is **{}** minutes.".format(bot_config["good_rxn"],server_config[str(ctx.guild.id)]["timeout"]))
        return

    int_timeout = int(timeout)

    if int_timeout < 1:
        await ctx.message.add_reaction(bot_config["bad_rxn"])
        await ctx.send("\{}Timeout must not be less than 1.".format(bot_config["bad_rxn"]))
        return

    try:
        old_timeout = server_config[str(ctx.guild.id)]["timeout"]
    except KeyError:
        old_timeout = -1

    server_config[str(ctx.guild.id)] = {}
    server_config[str(ctx.guild.id)]["timeout"] = int_timeout
    server_config[str(ctx.guild.id)]["enabled"] = True
    write_server_config()
    print("{} Delay update for guild ID {} ({} -> {}, invoked by user ID {})".format(tpfx(),ctx.guild.id,old_timeout,timeout,ctx.author.id))
    await ctx.message.add_reaction(bot_config["good_rxn"])

@_timeout.error
async def _timeout_error(ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.message.add_reaction(bot_config["bad_rxn"])
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.message.add_reaction(bot_config["bad_rxn"])
        await ctx.send("\{}You must have the `Manage Guild` permission to use this command.".format(bot_config["bad_rxn"]))
    else:
        raise(error)

@bot.command(name="toggle")
@commands.check(no_pm)
@commands.check(perms)
async def _toggle(ctx):
    '''Toggle whether or not to enforce the timeout value for a specific server. Only users with the Manage Guild permission can use this command.'''
    try:
        if server_config[str(ctx.guild.id)]["enabled"] == True:
            server_config[str(ctx.guild.id)]["enabled"] = False
        elif server_config[str(ctx.guild.id)]["enabled"] == False:
            server_config[str(ctx.guild.id)]["enabled"] = True
        print("{} Toggle for guild ID {} ({}, invoked by user ID {})".format(tpfx(),ctx.guild.id,server_config[str(ctx.guild.id)]["enabled"],ctx.author.id))
        write_server_config()

        await ctx.message.add_reaction(bot_config["good_rxn"])
        if server_config[str(ctx.guild.id)]["enabled"] == True:
            await ctx.send("\{}**Enabled** this server".format(bot_config["good_rxn"]))
        elif server_config[str(ctx.guild.id)]["enabled"] == False:
            await ctx.send("\{}**Disabled** this server".format(bot_config["good_rxn"]))
    except KeyError:
        server_config[str(ctx.guild.id)] = {}
        server_config[str(ctx.guild.id)]["timeout"] = 20
        server_config[str(ctx.guild.id)]["enabled"] = True
        print("{} Toggle for unmapped guild ID {} ({}, invoked by user ID {})".format(tpfx(),ctx.guild.id,server_config[str(ctx.guild.id)]["enabled"],ctx.author.id))
        write_server_config()

        await ctx.message.add_reaction(bot_config["good_rxn"])
        await ctx.send("\{}Enabled this server with a timeout of **20** minutes".format(bot_config["good_rxn"]))

@_toggle.error
async def _toggle_error(ctx, error):
    if isinstance(error, commands.errors.NoPrivateMessage):
        await ctx.message.add_reaction(bot_config["bad_rxn"])
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.message.add_reaction(bot_config["bad_rxn"])
        await ctx.send("\{}You must have the `Manage Guild` permission to use this command.".format(bot_config["bad_rxn"]))
    else:
        raise(error)

# When a user joins, after x minutes, check if they have any roles. If they don't, kick them.
@bot.event
async def on_member_join(member):
    try:
        server_config[str(member.guild.id)]
    except KeyError:
        return

    if server_config[str(member.guild.id)]["enabled"] == False:
        return


    # If you want to add a message when the user joins, do it here.
    # An example message is given below. Feel free to uncomment it.

    #await member.send("Welcome, {}, to {}!".format(member.name,member.guild.name))

    print("{} User ID {} joined guild ID {}, waiting {} seconds ({} minutes) to kick".format(tpfx(),member.id,member.guild.id,(server_config[str(member.guild.id)]["timeout"]*60),server_config[str(member.guild.id)]["timeout"]))
    await asyncio.sleep(int((server_config[str(member.guild.id)]["timeout"]))*60)

    if len(member.roles) == 1: #If a user "has no roles", they actually have the @everyone role, so the length of the roles is 1.

        # If you want to send the member a message before they get kicked, such as a "here's the resaon you were kicked" or "here's an invite to try again", do that here.
        # An example message is given below. Feel free to uncomment it.

        #await member.send("You were kicked from {} because you did not have any roles.".format(member.guild.name))

        await member.kick(reason="Did not have any roles after {} minutes".format(server_config[str(member.guild.id)]["timeout"]))
        print("{} Kicked user ID {} from guild ID {} as they did not have any roles after {} minutes".format(tpfx(),member.id,member.guild.id,server_config[str(member.guild.id)]["timeout"]))


# Start the Discord bot.
bot.run(bot_config["token"])
