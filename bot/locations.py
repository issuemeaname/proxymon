from enum import Enum

from bot.objects import ProxymonObject


class LocationBase(ProxymonObject):
    def __init__(self, name, north: list = [], east: list = [],
                 south: list = [], west: list = []):
        self.name = name
        self.north = north
        self.east = east
        self.south = south
        self.west = west


class Location(Enum):
    NONE = LocationBase("None")
    SOMEWHERE = LocationBase("Somewhere")
    YOUR_ROOM = LocationBase("Your Room")
    STARTER_TOWN = LocationBase("Starter Town")
