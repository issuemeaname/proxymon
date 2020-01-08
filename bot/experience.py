from enum import Enum
from math import floor


class Equation(object):
    def default(level):
        return Equation.medium_fast(level)

    def erratic(level):
        if level <= 50:
            return level**3 * (100-level) / 50
        elif level <= 68:
            return level**3 * (150-level) / 100
        elif level <= 98:
            return level**3 * floor(1911-level*10 / 3)
        elif level <= 100:
            return level**3 * (160-level) / 100

    def fast(level):
        return 4 * level**3 / 5

    def medium_fast(level):
        return level**3

    def slow(level):
        return 5 * level**3 / 4

    def get(name):
        default = None

        return getattr(Equation, name, default)


class Group(Enum):
    DEFAULT = Equation.default
    ERRATIC = Equation.erratic
    FAST = Equation.fast
    MEDIUM_FAST = Equation.medium_fast
    SLOW = Equation.slow


class Experience(object):
    def __init__(self, current: int, max: int):
        self.current = current
        self.max = max
        self.needed = self.max - self.current

    def __iadd__(self, value):
        self.current += value
        needed = self.max - self.current

        if needed < 0:
            needed = 0
        self.needed = 0

    def setup(self, level, equation):
        self.__init__(equation(level-1), equation(level))

        return self
