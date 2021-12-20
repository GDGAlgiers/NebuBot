import discord
import json
import os
from types import SimpleNamespace
import sys
from core.errors import *


def loads_to_object(json_file):
    """
        Loads from a json file  to a python object filling its properties with 
        dictionnary key 
    """
    return json.loads(open(json_file, "r").read(),object_hook=lambda d: SimpleNamespace(**d))




if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    config = loads_to_object("config.json")



async def getchannel(bot,id):
    channel = bot.get_channel(id)
    if not channel:
        try:
            channel = await bot.fetch_channel(id)
        except discord.InvalidData:
            channel = None
        except discord.HTTPException:
            channel = None
    return channel

async def getuser(bot,id):
    user = bot.get_user(id)

    if not user:
        user = await bot.fetch_user(id)

    return user

async def getguild(bot,id):
    guild = bot.get_guild(id)

    if not guild:
        guild = await bot.fetch_guild(id)

    return guild

async def send_embed(context,title, description, color =  int(config.EMBED_COLOR,16)):
    embed = discord.Embed(
                title=title,
                description=description,
                color=color
            )
    await context.send(embed=embed)

def verify_api(discord_id):
    r =  requests.post(config.HACK_THE_BOT_URL+"/api/participant/verify", json={"discord_id":discord_id}) 
    res = r.json()
    if res["status"] =='UNAUTHORIZED':
        raise NotRegistered()
    elif res["status"] =='UNKNOWN_ERROR':
        raise UnknownError()
    elif res["status"] =='SUCCESS':
        return res["participant_id"]
    else:
        raise UnknownError()