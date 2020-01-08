from enum import Enum
from random import randint

from bot.objects import ProxymonObject


class StatusBase(ProxymonObject):
    def __init__(self, name: str, min: int, max: int,
                 bonus: int, treatment: str = None):
        self.name = name
        self.duration = randint(min, max)
        self.bonus = bonus
        self.treatment = treatment

    def done(self):
        return self.duration == 0

    def requires_treatment(self):
        return self.treatment is not None


class Status(Enum):
    SLEEP = StatusBase("Sleep", min=1, max=5, bonus=200)
    FAINTED = StatusBase("Fainted", min=-1, max=-1, bonus=-1)
    NONE = StatusBase("None", min=0, max=0, bonus=0)
