from enum import Enum
from random import choice

from bot.objects import ProxymonObject


class AbilityBase(ProxymonObject):
    def __init__(self, name: str, desc: str, hidden: bool = False,
                 function=None):
        self.name = name
        self.description = desc
        self.hidden = hidden
        self.function = function

    def process(self, proxymon, target):
        return self.function(proxymon, target)


class Ability(Enum):
    NONE = AbilityBase("None", "Nothing happens.")
    OVERGROW = AbilityBase("Overgrow", "Increases Attack and Special attack "
                                       "stats by 50% when the Proxymon is at "
                                       "or below 1/3 of it's max HP")
    BLAZE = AbilityBase("Blaze", "Increases Attack and Special attack stats "
                                 "50% when the Proxymon is at or below 1/3 of "
                                 "it's max HP")
    TORRENT = AbilityBase("Torrent", "Increases Attack and Special attack "
                                     "stats by 50% when the Proxymon is at or "
                                     "below 1/3 of it's max HP")
    CHLOROPHYLL = AbilityBase("Chlorophyll", "Double speed in harsh sunlight")
    SOLAR_POWER = AbilityBase("Solar Power", "1.5x Special attack and loses "
                                             "1/8th max HP per turn in harsh "
                                             "sunlight")
    RAIN_DISH = AbilityBase("Rain Dish", "Heal 1/16th max HP per turn in "
                                         "rain")

    def lookup(name):
        for ability in Ability:
            if ability.name == name.upper():
                return ability
        return None

    def random():
        return choice([a for a in Ability])
