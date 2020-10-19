


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

# ToDo: Proper multiserver allowed roles save system/database
# ToDo: Make a proper config system
# ToDo: Web Interface

import os
import random
import re

from dotenv import load_dotenv

import discord
from discord.ext import commands

VERSION = "2020.1.1dev"

# Load Tokens from Environment
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Bot/Client Object
bot = commands.Bot(command_prefix=KEYWORD)

# Remove help for custom implementation
bot.remove_command('help')


@bot.event
async def on_ready():
    print(f"{bot.user}")
    print(f"Version: {VERSION}\n")
    print("### Servers ###\n")
    total = 0
    for guild in bot.guilds:
        print(
            f" - {guild.name} (id: {guild.id})\n"
        )
        total += 1
    print("_____________________________________________________")
    print(f"  TOTAL: {total} Servers \n")


#####################################################################################
#                                   [ Misc Section ]
#####################################################################################

@bot.command(name="version", help="[ADMIN] Zeigt die Version des Bots an.")
@commands.has_role(BOTGROUP)
async def version(ctx):
    await ctx.send(VERSION)


@bot.command(name="help", help="Listet alle Befehle auf. (A -> Z)")
async def help(ctx):
    helptext=""
    ordered_list = sorted(bot.commands, key=lambda command: command.name)
    for command in ordered_list:
        if "[ADMIN]" not in command.help:
            helptext+=f"{command} - {command.help}\n"
        elif discord.utils.get(ctx.author.roles, name=BOTGROUP) is not None:
            helptext+=f"{command} - {command.help}\n"
    f = Formatter()
    formatted = f.code(helptext)
    await ctx.send(formatted)


@bot.command(name="coinflip", help="\"Heads?\" \"Or Tails?\" ")
async def coinflip(ctx):
    await ctx.send("Kopf." if random.randint(0, 1) else "Zahl.")


#####################################################################################
#                                   [ Roles Section ]
#####################################################################################

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
        await ctx.send("Diese Rolle kann nur manuell vom Administrator zugewiesen werden.")  


@bot.command(name="dismiss", help="Entfernt eine Rolle.")
async def dismiss(ctx, role_name: str):
    member = ctx.author
    role = discord.utils.get(member.roles, name=role_name)
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"Dir wurde die Rolle \"{role}\" aberkannt.")
    else:
        await ctx.send("Diese Rolle hast du nicht. Vertippt? (Groß- und Kleinschreibung beachten!)")


@commands.guild_only() # To hide allowed Roles from Public (Not Necessary)
@bot.command(name="roles", help="Listet alle verfügbaren Rollen auf.")
async def roles(ctx):
    string = ""
    for role in get_allowed_roles():
        string += " - " + role + "\n"
    
    await ctx.send(f"Verfügbare Rollen:\n{string}")


@bot.command(name="roles_set", help="[ADMIN] Rollen neuschreiben, die sich Benutzer selbst geben dürfen.")
@commands.has_role(BOTGROUP)
async def roles_set(ctx, *args):
    if dangerous_warning:
        await ctx.send(f"Dieser Befehl kann deinen Sever schädigen! \nWenn du hier z.B. Admin einträgst kann sich jeder selbst zum Admin machen!\n -> Wenn du weißt was du tust tippe \"{KEYWORD}unlock\" .")
    else:
        set_allowed_roles(args)
        await ctx.send("Datei erstellt.")


@bot.command(name="roles_get", help="Listet auch nicht verfügbaren Rollen auf.")
async def roles_get(ctx):
    string = ""
    for role in ctx.guild.roles:
        string += " - " + str(role) + "\n"
    
    string = string.replace("@", "(at)") # Remove @ from @everyone
    await ctx.send(f"Alle Rollen:\n{string}")


@bot.command(name="roles_add", help="[ADMIN] Rollen hinzufügen, die sich Benutzer selbst geben dürfen.")
@commands.has_role(BOTGROUP)
async def roles_add(ctx, *args):
    if dangerous_warning:
        await ctx.send(f"Dieser Befehl kann deinen Sever schädigen! \nWenn du hier z.B. Admin einträgst kann sich jeder selbst zum Admin machen!\n -> Wenn du weißt was du tust tippe \"{KEYWORD}unlock\" .")
    else:
        add_allowed_roles(args)
        await ctx.send("Rolle(n) hinzugefügt.")


@bot.command(name="roles_remove", help="[ADMIN] Rollen löschen, die sich Benutzer selbst geben dürfen.")
@commands.has_role(BOTGROUP)
async def roles_remove(ctx, *args):
    if dangerous_warning:
        await ctx.send(f"Dieser Befehl kann deinen Sever schädigen! \nWenn du hier z.B. Admin einträgst kann sich jeder selbst zum Admin machen!\n -> Wenn du weißt was du tust tippe \"{KEYWORD}unlock\" .")
    else:
        not_removed = remove_allowed_roles(args)
        if not_removed:
            for e in not_removed:
                await ctx.send(f'Rolle \"{e}\" nicht gefunden. Vertippt?')
        await ctx.send("Rolle(n) gelöscht.")


@bot.command(name="roles_create", help="[ADMIN] Erstellt eine, oder mehrere neue Rolle(n).")
@commands.has_role(BOTGROUP)
async def roles_create(ctx, *roles):
    for role in roles:
        if discord.utils.find(lambda m: m.name == role, ctx.guild.roles):
            await ctx.send(f"Rolle {role} existiert bereits.")
        else:
            await ctx.guild.create_role(name=role, mentionable=True)
            await ctx.send(f"Rolle(n) {role} erstellt.")


@bot.command(name="scan", help="{EXPERIMENTAL}[ADMIN] Scann einen Kanal und macht daraus Rollen, die selbst zugewiesen werden dürfen.")
@commands.has_role(BOTGROUP)
async def scan(ctx):
    async with ctx.channel.typing(): # Show typing animation
        async for message in ctx.channel.history(limit=100):
            roles = re.findall(r"\[([A-Za-z0-9_]+)\]", message.content)
            for role in roles:
                await roles_create(ctx, role)
                add_allowed_roles(role)
        await ctx.send(f"Scan fertig.") 
                
            

#####################################################################################
#                                   [ Move Section ]
#####################################################################################

@bot.command(name="move", help="[ADMIN] Veschiebt Jemanden in einen Channel")
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
        await ctx.send(f'Schiebung nach: \"{channel_name}\" !')
        for voice_channel in ctx.guild.voice_channels:
            for member in voice_channel.members:
                await member.move_to(channel, reason="Bot allmove.")


#####################################################################################
#                                   [ Security Section ]
#####################################################################################

@bot.command(name="unlock", help="[ADMIN] Ermöglich das Ändern sicherheitsrelevanter Einstellungen.")
@commands.has_role(BOTGROUP)
async def unlock(ctx):
    global dangerous_warning
    dangerous_warning = False
    print(f"[WARNING]: {ctx.author} unlocked {ctx.guild}")
    await ctx.send("Gott sei mit dir.")


@bot.command(name="lock", help="[ADMIN] Sperrt Ändern sicherheitsrelevanter Einstellungen.")
@commands.has_role(BOTGROUP)
async def lock(ctx):
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


#####################################################################################
#                                   [ Helpers Section ]
#####################################################################################

def get_allowed_roles():
    file = open("allowed_roles.txt","r")
    if file.mode == 'r':
        contents = file.read()
    file.close()
    roles = contents.splitlines()
    return roles


def set_allowed_roles(roles):
    file = open("allowed_roles.txt","w+")
    for role in roles:
        file.write(role + "\n")
    file.close()


def add_allowed_roles(roles):
    new_roles = get_allowed_roles()+list(roles)
    file = open("allowed_roles.txt","w+")
    for role in new_roles:
        file.write(role + "\n")
    file.close()


def remove_allowed_roles(roles):
    not_removed = list()
    new_roles = get_allowed_roles()
    for to_remove in list(roles):
        try:
            new_roles.remove(to_remove)
        except:
            not_removed.append(to_remove)
    file = open("allowed_roles.txt","w+")
    for role in new_roles:
        file.write(role + "\n")
    file.close()
    return not_removed


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


bot.run(DISCORD_TOKEN) # RUN!
