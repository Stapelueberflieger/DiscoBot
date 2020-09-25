


#                   A simple Discord Management-System
#                   © Stapelueberflieger 2020
#                   GIT: https://github.com/Stapelueberflieger



#####################################################################################
#                                   [ Config ]
KEYWORD = "!"               # Any
BOTGROUP = "Zauberer"       # Anyone in this Group has FULL Bot access!
dangerous_warning = True    # Recomended: True
channels = []               # Restrict the Bots to certain Channels [NOT IMPLEMENTED]

#####################################################################################

# Todo: Make a proper config system

import os
import random

from dotenv import load_dotenv

import discord
from discord.ext import commands

# Load Tokens from Environment
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Bot/Client Object
bot = commands.Bot(command_prefix=KEYWORD)

# Remove help for custom implementation
bot.remove_command('help')


@bot.event
async def on_ready():
    print("### Servers ###\n")
    total = 0
    for guild in bot.guilds:
        print(
            f'{bot.user} is connected to the following guild:\n'
            " -"f'{guild.name}(id: {guild.id})'
        )
        total += 1
    print("_____________________________________________________")
    print(f"  TOTAL: {total} Servers \n\n ")



@bot.command(name="help", help="Listet alle Befehle auf. (A -> Z)")
async def help(ctx):
    helptext=""
    ordered_list = sorted(bot.commands, key=lambda command: command.name)
    for command in ordered_list:
        helptext+=f"{command} - {command.help}\n"
    f = Formatter()
    formatted = f.code(helptext)
    await ctx.send(formatted)


@bot.command(name="coinflip", help="\"Kopf oder Zahl?\" (Bioshock Infinite).")
async def coinflip(ctx):
    await ctx.send("Kopf." if random.randint(0, 1) else "Zahl.")


@commands.guild_only() # To hide allowed Roles from Public (Not Necessary)
@bot.command(name="roles", help="Listet alle verfügbaren Rollen auf.")
async def roles(ctx):
    string = ""
    for role in get_allowed_roles():
        string += " - " + role + "\n"
    
    await ctx.send(f"Verfügbare Rollen:\n{string}")


@bot.command(name="roles_all", help="Listet auch nicht verfügbaren Rollen auf.")
async def roles_all(ctx):
    string = ""
    for role in ctx.guild.roles:
        string += " - " + str(role) + "\n"
    
    string = string.replace("@", "(at)") # Remove @ from @everyone
    await ctx.send(f"Alle Rollen:\n{string}")


@bot.command(name="allowed_roles", help="[ADMIN] Rollen bearbeiten, die sich Benutzer selbst geben dürfen.")
@commands.has_role(BOTGROUP)
async def move(ctx, *args):
    if dangerous_warning:
        await ctx.send(f"Dieser Befehl kann deinen Sever schädigen! \nWenn du hier z.B. Admin einträgst kann sich jeder selbst zum Admin machen!\n -> Wenn du weißt was du tust tippe \"{KEYWORD}unlock\" .")
    else:
        update_allowed_roles(args)
        await ctx.send("Datei erstellt.")
        roles_all()


@bot.command(name="assign", help="Weist eine Rolle zu.")
async def assign(ctx, role_name: str):
    member = ctx.author
    role = discord.utils.get(member.guild.roles, name=role_name)
    if role is None:
        await ctx.send("Diese Rolle gibt es nicht. Hast du dich vertippt? (Groß- und Kleinschreibung beachten!)")
    elif role_name in get_allowed_roles():
        await member.add_roles(role)
        await ctx.send(f"Dir wurde die Rolle \"{role}\" zugewiesen!")
    else:
        await ctx.send("Diese Rolle darf nur vom Administrator zugewiesen werden.")  


@bot.command(name="move", help="[MOVER] Veschiebt Jemanden in einen Channel")
@commands.has_role(BOTGROUP)
async def move(ctx, user_name, channel_name):
    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    member = ctx.author.guild.get_member_named(user_name)
    if member is None:
        await ctx.send(f'Benutzer \"{user_name}\" nicht gefunden!')
    elif channel is None:
        await ctx.send(f'Channel \"{channel_name}\" nicht gefunden!')
    else:
        await member.move_to(channel, reason="Bot hat gemoved.")


@bot.command(name="move_all", help="[ADMIN] Veschiebt alle user in deinen Channel")
@commands.has_role(BOTGROUP)
async def move_all(ctx, channel_name):
    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    if channel is None:
        await ctx.send(f'Channel \"{channel_name}\" nicht gefunden!')
    else:
        for voice_channel in ctx.guild.voice_channels:
            for member in voice_channel.members:
                await member.move_to(channel, reason="Bot allmove.")



@bot.command(name="unlock", help="[ADMIN] Ermöglich das Ändern sicherheitsrelevanter Einstellungen.")
@commands.has_role(BOTGROUP)
async def unlock(ctx):
    global dangerous_warning
    dangerous_warning = False
    print(f"[WARNING]: {ctx.author} unlocked {ctx.guild}")
    await ctx.send("Gott sei mit dir.")


@bot.command(name="lock", help="[ADMIN] Sperrt Ändern sicherheitsrelevanter Einstellungen.")
@commands.has_role(BOTGROUP)
async def unlock(ctx):
    global dangerous_warning
    dangerous_warning = True
    print(f"[INFO]: {ctx.author} locked {ctx.guild}")
    await ctx.send("Gesichert. Das war knapp!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Dafür hast du nicht die nötigen Rechte!')
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('Befehl nicht gefunden. Vertippt?')


def get_allowed_roles():
    file = open("allowed_roles.txt","r")
    if file.mode == 'r':
        contents = file.read()
    file.close()
    roles = contents.split()
    return roles


def update_allowed_roles(roles):
    file = open("allowed_roles.txt","w+")
    for role in roles:
        file.write(role + "\n")
    file.close()


class Formatter:
    code_multiline="```"

    @classmethod
    def code(cls, text): # TODO More Lambdas
        return cls.code_multiline + text + cls.code_multiline

    def embed(): # TODO Optional Eyecandy; Implement as @Decorator
        embedVar = discord.Embed(title="Verfügbare Rollen", color=discord.Colour(255).from_rgb(0, 255, 204))
        for role in get_allowed_roles():
            embedVar.add_field(name="Field", value=role, inline=False)
        #await ctx.send(embed=embedVar)


bot.run(DISCORD_TOKEN)
