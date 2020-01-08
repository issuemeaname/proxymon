from enum import Enum
from random import choice

from bot.objects import ProxymonObject


class NatureBase(ProxymonObject):
    def __init__(self, name, **kwargs):
        self.name = name

        for k, v in kwargs.items():
            setattr(self, k, v / 100)


class Nature(Enum):
    HARDY = NatureBase("Hardy")
    ADAMANT = NatureBase("Adamant", attack=1.1, sp_attack=0.9)

    def random():
        return choice([n for n in Nature])
