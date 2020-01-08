from enum import auto
from enum import Enum
from random import random


class Gender(Enum):
    MALE = auto()
    FEMALE = auto()
    GENDERLESS = auto()

    def random(gender_chance):
        chance = random()

        if gender_chance == 0:
            return Gender.GENDERLESS
        elif chance <= gender_chance:
            return Gender.MALE
        else:
            return Gender.FEMALE
