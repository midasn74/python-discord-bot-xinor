import discord
from discord.ext import commands
from discord.utils import get
from time import sleep
import os
import qrcode
from sys import platform
import random
from Config import *
import datetime
import subprocess

print("bot is initializing.")

TOKEN = os.environ.get('TOKEN', None)
if TOKEN == None:
    from Secrets import TOKEN
    print("imported secrets.py")
else:
    commandPrefix = os.environ.get('COMMAND_PREFIX', None)
    adminId = os.environ.get('ADMIN_ID', None)
    print("Got secrets from env vars.")

client = commands.Bot(command_prefix=commandPrefix, case_insensitive=True)

client.remove_command("help")

annoyKickMemberList = []


@client.command(pass_context=True, aliases=['h'])
async def help(ctx):
    embed = discord.Embed(title="Xinor Bot Commands", colour=discord.Colour(embedColor), url="https://github.com/midasn74/",
                          description=f"The letter(s) in the brackets after the commands are the aliases,\nuse these if you don't want to type the full command.\nCommand prefix: {commandPrefix}, this is what you put in front of the commands.")

    embed.add_field(name="help [h]", value="Shows you this embed.", inline=False)
    embed.add_field(name="join [j]", value="Connects the bot to your voice channel.\nServer only.", inline=False)
    embed.add_field(name="leave [l]", value="disconnects the bot from current voice channel.\nServer only.", inline=False)
    embed.add_field(name="ping", value="Pong!", inline=False)
    embed.add_field(name="makeqrcode",
                    value="Type something you want to make a QR code from after the command,\ntext or a URL. Then it will make a QR code out of it.", inline=False)
    embed.add_field(name="rolladice", value="Sends a random number from 1 to 6.", inline=False)
    embed.add_field(name="earrape", value="Returns a earraped version of the file you sent,\nfile must be under 0.5 MB and must be a mp3, wav or ogg file.", inline=False)
    embed.add_field(name="Moderation commands:", value="If some commands like ban doesn't work make sure the xinor bot has administrator role and is on top of the roles list.")
    embed.add_field(name="ban", value="Bans the tagged user, user must can't be the server owner.\nBan member permission required, server only.", inline=False)
    embed.add_field(name="unban", value="Unbans the tagged user.\nBan member permission required, server only.", inline=False)
    embed.add_field(name="spam", value="Sends the tagged user \'spam\' 50 times.\nAdministrator only, server only.", inline=False)
    embed.add_field(name="annoykickadd", value="Added users will be kicked every time they connect to a voice channel.\nAdministrator only, server only.", inline=False)
    embed.add_field(name="annoykickremove", value="removed users will no longer be kicked every time they connect to a voice channel.\nAdministrator only, server only.", inline=False)
    # embed.add_field(name="disablestream", value="Reconnects the user to disable thier stream and or camera.\nAdministrator only, server only.", inline=False)

    await ctx.send(embed=embed)


@client.command(pass_context=True, aliases=['j'])
async def join(ctx):
    try:
        global voice
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.move_to(channel)
            await ctx.send(f"Joined \"{channel}\"")
        else:
            voice = await channel.connect()
            await ctx.send(f"Joined \"{channel}\"")

    except:
        if ctx.message.guild == None:
            await ctx.send("This command cannot be used in private messages.")
        else:
            await ctx.send("can't join because user isn't in any channel.")

@client.command(pass_context=True, aliases=['l'])
async def leave(ctx):
    try:
        global voice
        channel = ctx.message.author.voice.channel
        voice = get(client.voice_clients, guild=ctx.guild)

        if voice and voice.is_connected():
            await voice.disconnect()
            await ctx.send(f"Left \"{channel}\"")
        else:
            await ctx.send("Couldn't disconnect because bot isn't in any channel.")
    except:
        if ctx.message.guild == None:
            await ctx.send("This command cannot be used in private messages.")
        else:
            await ctx.send("Couldn't disconnect because you have to be in the bots channel to let the bot disconnect.")


@client.command(pass_context=True)
async def ping(ctx):
    await ctx.send("pong!")


@client.command(pass_context=True)
async def makeqrcode(ctx, *arg):
    argsstr = ' '.join(map(str, arg))
    if len(argsstr) > 100:
        await ctx.send("QR code data must be less then 100 characters")
    elif argsstr == "":
        await ctx.send("Please add some data you want to add to your QR code.")
    else:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(argsstr)

        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img.save("QRCode.png")

        await ctx.send(file=discord.File('QRCode.png'))


@client.command(pass_context=True)
async def rolladice(ctx):
    await ctx.send(random.choice(["1", "2", "3", "4", "5", "6"]))


@client.command(pass_context=True)
@commands.has_guild_permissions(administrator=True)
async def spam(ctx, member : discord.Member=None):
    if  member == None:
        await ctx.send("Please tag the user you want to spam.")
        return

    try:
        await member.send("spam")
        await ctx.send(f"Spamming <@{member.id}>.")
        for i in range(19):
            await member.send("spam")
    except:
        await ctx.send(f"Can't spam <@{member.id}>', beacuse <@{member.id}> has blocked the bot.")


@client.command(pass_context=True)
@commands.has_guild_permissions(ban_members=True)
async def ban(ctx, member : discord.Member=None,):
    await member.ban()
    await ctx.send(f"Banned {member}")


@client.command(pass_context=True)
@commands.has_guild_permissions(ban_members=True)
async def unban(ctx, arg):
    try:
        splitArg = str(arg).split("!")
        id = int(splitArg[1][:-1])
    except:
        await ctx.send("Please tag the user you want to unban")
        return
    member = await client.fetch_user(id)
    try:
        await ctx.guild.unban(member)
    except:
        await ctx.send("can't unban tagged user.")
        return
    await ctx.send(f"Unbanned {member}")


async def earrape(message):
    channel = message.channel
    if len(message.attachments) > 1:
        await channel.send("Please only attach 1 file to your message.")
        return
    if len(message.attachments) < 1:
        await channel.send("Please attach a sound file to your message.")
        return
    for attachment in message.attachments:
        splitFilename = attachment.filename.split(".")
        fileExt = "." + splitFilename[-1]
        if fileExt == ".mp3" or fileExt == ".ogg" or fileExt == ".wav":
            if attachment.size > 1000000:
                await channel.send("File must be under 1 MB")
                return
            try:
                await attachment.save("sound.mp3")
            except:
                await channel.send("Something went wrong while downloading the file.")
                return
            newFilename = "earrape" + fileExt
            subprocess.call(['ffmpeg', '-y', '-i', 'sound.mp3', '-af', 'acrusher=.1:1:64:0:log', newFilename])
            await channel.send(file=discord.File(newFilename))
            return
        await channel.send("File must have one of the following file extensions: mp3, ogg, wav.")


@client.command(pass_context=True)
async def avatar(ctx, *, member : discord.Member=None):
    await ctx.send(member.avatar_url)


@client.command(pass_context=True)
@commands.guild_only()
async def profile(ctx, *, member : discord.Member=None):
    if member == None:
        await ctx.send("Please tag the user you want to check.")
        return

    embed = discord.Embed(title=f"Profile {member.display_name}", colour=discord.Colour(embedColor),
                          url="https://github.com/midasn74/")

    embed.add_field(name="Joined server at:", value=f"``{str(member.joined_at)[:16]}``",
                    inline=False)
    embed.add_field(name="Joined discord at:", value=f"``{str(member.created_at)[:16]}``",
                    inline=False)
    embed.add_field(name="User id:", value=f"``{member.id}``",
                    inline=False)
    if member.display_name is not member.name:
        embed.add_field(name="Real discord name:", value=f"``{member.name}``",
                        inline=False)
    embed.add_field(name="Name discriminator:", value=f"``#{member.discriminator}``",
                    inline=False)

    embed.set_thumbnail(url=member.avatar_url)

    await ctx.send(embed=embed)


@client.command(pass_context=True)
@commands.has_guild_permissions(administrator=True)
@commands.guild_only()
async def annoykickadd(ctx, *, member : discord.Member=None):
    if member == None:
        await ctx.send("Please tag the user you want to add to the list.")
        return
    if str(member.id) in annoyKickMemberList:
        await ctx.send(f"{member.name} is already inside the annoy kick list.")
        return
    annoyKickMemberList.append(str(member.id))
    await member.move_to(channel=None)
    await ctx.send(f"added {member.name} to the annoy kick list.")


@client.command(pass_context=True)
@commands.has_guild_permissions(administrator=True)
@commands.guild_only()
async def annoykickremove(ctx, *, member : discord.Member=None):
    if member == None:
        await ctx.send("Please tag the user you want to remove from to the list.")
        return
    if str(member.id) in annoyKickMemberList:
        annoyKickMemberList.remove(str(member.id))
        await ctx.send(f"removed {member.name} from the annoy kick list.")
        return
    await ctx.send(f"{member.name} isn't inside the annoy kick list.")


# @client.command(pass_context=True)
# @commands.has_guild_permissions(administrator=True)
# @commands.guild_only()
# async def disableStream(ctx, *, member : discord.Member=None):
#     if member == None:
#         await ctx.send("Please tag the user you want to disable the stream and or video from.")
#         return
#     if member.voice == None:
#         await ctx.send(f"{member.name} isn't connected to a voice channel.")
#         return
#     if member.voice.channel is not None:
#         if member.voice.self_stream == True and member.voice.self_video == True:
#             await reconnectMember(member)
#             await ctx.send(f"Disabled stream and video for {member.name}")
#             return
#         if member.voice.self_stream == True:
#             await reconnectMember(member)
#             await ctx.send(f"Disabled stream for {member.name}")
#             return
#         if member.voice.self_video == True:
#             await reconnectMember(member)
#             await ctx.send(f"Disabled video for {member.name}")
#             return
#         await ctx.send(f"{member.name} isn't streaming or sharing video.")
#         return


@client.event
async def on_ready():
    print(f"Logged in as: {client.user}")

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"{commandPrefix}commands"))


@client.event
async def on_message_edit(messageold, messagenew):
    if messagenew.author == client.user:
        return

    messagecontent = str(messagenew.content).lower()
    for swearWord in swearWords:
        if swearWord in messagecontent:
            await messagenew.delete()


@client.event
async def on_member_join(member):
    if disableNewUserMessage:
        pass
    else:
        await member.send(newUserMessage.format(member=f"<@{member.id}>"))


@client.event
async def on_message(message):
    if message.guild == None:
        isPrivateMessage = True
    else:
        isPrivateMessage = False

    if str(message.author.id) in mutedUsers and not isPrivateMessage:
        await message.delete()
        return

    if message.author == client.user or str(message.author.id) in ignoredUsers:
        return

    if message.content == None:
        pass
    else:
        if isPrivateMessage:
            print("message: | " + "time: " + str(datetime.datetime.today())[:-7] + " | guild: " + "Private message" +
                  " | channel: " + "Private message" + " | author: " + str(message.author) + "\nMessage content: "
                  + message.content)
        else:
            print("message: | " + "time: " + str(datetime.datetime.today())[:-7] + " | guild: " + message.guild.name +
                  " | channel: " + message.channel.name + " | author: " + str(message.author) + "\nMessage content: "
                  + message.content)

    if not disableSwearWordFilter and not isPrivateMessage:
        messagecontent = str(message.content).lower()
        for swearWord in swearWords:
            if swearWord in messagecontent:
                await message.delete()

    if (message.content.lower().startswith(commandPrefix + "earrape")):
        await earrape(message)
        return

    await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.PrivateMessageOnly):
        await ctx.send("This command is for private messages only")
        return
    if isinstance(error, discord.ext.commands.errors.NoPrivateMessage):
        await ctx.send("This command cannot be used in private messages.")
        return
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("Unknown command")
        return
    if isinstance(error, discord.ext.commands.errors.MissingRole):
        await ctx.send("You are missing the required roles for this command.")
        return
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send("You are missing the required permissions for this command.")
        return
    if isinstance(error, discord.ext.commands.errors.UserInputError):
        await ctx.send("Tagged user not found.")
        return
    await ctx.send(f"Error: `{error}` report this to a developer if you think this is wrong.")


@client.event
async def on_voice_state_update(member, before, after):
    if str(member.id) in annoyKickMemberList and after.channel is not None:
        await member.move_to(channel=None)

#    if after.channel is not None and len(after.channel.members) == 1:
#        if str(after.channel.id) in duplicatingChannelId:
#            newName = after.channel.name
#            newChannel = await after.channel.clone(name=newName)
#            duplicatingChannelId.append(str(newChannel.id))
#    if after.channel is not before.channel:
#        if str(before.channel.id) in duplicatingChannelId and len(before.channel.members) == 0 and str(before.channel.id) is not duplicatingChannelId[0]:
#            await before.channel.delete()
#            duplicatingChannelId.remove(str(before.channel.id))


client.run(TOKEN)
