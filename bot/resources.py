import os
from enum import Enum


REGION = "Rammus"
START_COMMAND = "profile create"
INVITE = (r"https://discordapp.com/api/oauth2/authorize?client_id="
          "502519551465095178&permissions=8&scope=bot")
OWNERS = {
    "DJ":           173225726139564032,
    "Orcles":       301638410815406081,
    "Sheeptrainer": 295307539443220480,
    "Afhnd":        335829816609734656,
    "Kai":          297874688145752066,
    "Roy":          353180156883632128,
    "Preson":       210477913152290821,
}


async def command_prefix(bot, message):
    return [f"{bot.user.mention} ", "proxy.", "p."]


def _get_cogs(path=r"bot\cogs"):
    cog_path = path.replace("\\", ".")
    cogs = []

    for obj in os.listdir(path):
        if obj.startswith("_"):
            continue
        origin = os.path.join(path, obj)

        if os.path.isfile(origin):
            obj = os.path.splitext(obj)[0]
            obj_path = f"{cog_path}.{obj}"

            cogs.append(obj_path)
        elif os.path.isdir(origin):
            cogs += _get_cogs(origin)
    return sorted(cogs) or None


class Chances(Enum):
    FIND = 5
