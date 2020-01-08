from enum import auto
from enum import Enum
from random import choice


class Rarity(Enum):
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    MYTHIC = auto()
    LEGENDARY = auto()

    def random():
        return choice([r for r in Rarity])
