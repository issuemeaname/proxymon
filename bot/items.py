from enum import Enum

from bot.objects import ProxymonObject


class ItemBase(ProxymonObject):
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Item(Enum):
    NONE = ItemBase("None", "")

    def get(name: str):
        for item in Item:
            if item.value.name == name.title():
                return item
