from enum import Enum

from bot.objects import ProxymonObject


class TypeBase(ProxymonObject, dict):
    def __init__(self, name, **kwargs):
        self.name = name
        self._kwargs = kwargs

    def setup(self):
        for t in Type:
            self[t.name] = 1.0

        # t, m = Type, Multiplier
        for t, m in self._kwargs.items():
            self[t] *= m


class Type(Enum):
    NORMAL = TypeBase("Normal")
    FIGHTING = TypeBase("Fighting")
    FLYING = TypeBase("Flying")
    POISON = TypeBase("Poison")
    GROUND = TypeBase("Ground")
    ROCK = TypeBase("Rock")
    BUG = TypeBase("Bug")
    GHOST = TypeBase("Ghost")
    STEEL = TypeBase("Steel")
    FIRE = TypeBase("Fire")
    WATER = TypeBase("Water")
    GRASS = TypeBase("Grass")
    ELECTRIC = TypeBase("Electric")
    PSYCHIC = TypeBase("Psychic")
    ICE = TypeBase("Ice")
    DRAGON = TypeBase("Dragon")
    DARK = TypeBase("Dark")
    FAIRY = TypeBase("Fairy")
    TYPELESS = TypeBase("Typeless")
    UNKNOWN = TypeBase("Unknown")

    def setup():
        for t in Type:
            t.value.setup()


# Type.setup()


class TypeDual(TypeBase):
    def __init__(self, **kwargs):
        self.types = []

        for k in kwargs.keys():
            self.types.append(getattr(Type, k, None))

    def __str__(self):
        return (", ").join([t.name.title() for t in self.types])

    def __iter__(self):
        return iter(self.value)
