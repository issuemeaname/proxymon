from enum import auto
from enum import Enum
from random import random
from typing import Union

from bot.objects import ProxymonObject
from bot.proxymon import ProxymonBase
from bot.statuses import Status
from bot.types import Type


class MoveCategory(Enum):
    PHYSICAL = auto()
    SPECIAL = auto()
    STATUS = auto()


class PPHolder(object):
    def __init__(self, current: int, max: int):
        self.current = current
        self.max = max


class MoveBase(ProxymonObject):
    def __init__(self, name, power: int = 40, accuracy: int = 100,
                 pp: int = 35, pp_max: int = 35,
                 attack_type: Union[str, Type] = Type.NORMAL,
                 category: Union[str, MoveCategory] = MoveCategory.PHYSICAL,
                 status: Status = None, status_chance: int = None,
                 percentage: int = False):
        self.name = name
        self.power = power
        self.accuracy = accuracy
        self.pp = PPHolder(pp, pp_max)

        if type(attack_type) is Type:
            self.type = attack_type
        else:
            self.type = getattr(Type, type, Type.UNKNOWN)

        if type(category) is MoveCategory:
            self.category = category
        else:
            self.category = getattr(MoveCategory, category)

        self.percentage = percentage

    def hits(self):  # , evasion: Union[int, float]):
        if self.accuracy == 0:
            return True

        hit_chance = random() * 100
        return hit_chance <= self.accuracy

    def applies_status_to(self, proxymon: ProxymonBase):
        if self.status is None or self.status_chance == 0:
            return False

        status_chance = random() * 100
        return status_chance <= self.status_chance

    def dump(self):
        return {
            **super().dump(),
            "power": self.power,
            "accuracy": self.accuracy,
            "pp": self.pp.current,
            "pp_max": self.pp.max,
            "attack_type": self.type.name,
            "category": self.category.name,
            "status": (self.status is not None and self.status.name or
                       self.status),
            "status_chance": self.status_chance,
            "percentage": self.percentage
        }


class Move(Enum):
    TACkLE = MoveBase("Tackle", power=40, accuracy=100, pp=35, pp_max=35,
                      type=Type.NORMAL, category=MoveCategory.PHYSICAL)
    FIRE_RAIN = MoveBase("Fire Rain", power=55, accuracy=90, pp=25, pp_max=25,
                         type=Type.FIRE, category=MoveCategory.SPECIAL)

    def get(name: str):
        for move in Move:
            if move.value.name == name.title():
                return move
        return None
