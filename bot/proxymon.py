from enum import Enum
from random import random
from typing import Union

import discord

from bot.abilities import Ability
from bot.experience import Experience
from bot.db import Database
from bot.genders import Gender
from bot.items import Item
from bot.locations import Location
from bot.natures import Nature
from bot.proxydex import Proxydex
from bot.rarities import Rarity
from bot.stats import Stats
from bot.statuses import Status
from bot.utils import proxymon_dump


class Evolution(object):
    def __init__(self, name: str, level: int = None, item: str = None):
        self.name = name
        self._requirement = {
            "level": level,
            "item": item
        }

    def get_requirement(self):
        level = self._requirement.get("level")

        if level is not None and level > 0:
            return level
        return self._requirement.get("item")

    def dump(self):
        return {
            "name": self.name,
            **self.requirement
        }


class ProxymonBase(object):
    def __init__(self, name, owner: int = None, level: int = 1,
                 female_chance: int = 50, level_met: int = 1,
                 hp: int = 50, hp_max: int = 50, attack: int = 50,
                 defense: int = 50, sp_attack: int = 50, sp_defense: int = 50,
                 speed: int = 50, moves: tuple = [None]*4, learnset: list = [],
                 evolutions: list = [], shiny: bool = False,
                 experience: int = None,
                 met_at: Union[Location, str] = None,
                 item: Union[Item, str] = None,
                 gender: Union[Gender, str] = None,
                 nature: Union[Nature, str] = None,
                 ability: Union[Ability, str] = None,
                 hidden_ability: Union[Ability, str] = None,
                 rarity: Union[Rarity, str] = None,
                 status: Union[Status, str] = None):
        data = Proxydex.get_entry_by(name)
        group = data.exp_group
        self.type = data.type
        self.id = data.id

        self.name = name.title()
        self.owner = owner
        self.level = level
        self.female_chance = female_chance
        self.level_met = level_met
        self.base_stats = Stats(hp, hp_max, attack, defense, sp_attack,
                                sp_defense, speed)
        self.stats = self.base_stats * level
        self.moves = moves
        self.learnset = learnset
        self.evolutions = evolutions or str(evolutions)
        self.shiny = shiny

        if experience is not None:
            self.experience = Experience(experience, group(self.level))
        else:
            self.experience = Experience(0, 0).setup(self.level, group)

        # this needs to be changed, at some point
        self.met_at = self.setup(met_at, Location, default_is_none=True)
        self.item = self.setup(item, Item, default_is_none=True)
        self.gender = self.setup(gender, Gender, self.female_chance)
        self.nature = self.setup(nature, Nature)
        self.ability = self.setup(ability, Ability)
        self.hidden_ability = self.setup(hidden_ability, Ability)
        self.rarity = self.setup(rarity, Rarity)
        self.status = self.setup(status, Status, default_is_none=True)

    async def edit(self, **attribs):
        for k, v in attribs.items():
            if getattr(self, k) is not None:
                setattr(self, k, v)

        if self.owner is not None:
            user = self.get_user(self.id)
            trainer = await Database.get_trainer(user)
            await trainer.edit(starter=self)
        return self

    def setup(self, value, vtype, *args, default_is_none=False):
        ret = None

        if value is None and default_is_none:
            ret = vtype["NONE"]
        elif value is None:
            ret = vtype.random(*args)
        elif type(value) is vtype:
            ret = value
        elif type(value) is str:
            ret = vtype[value]
        return ret

    def has_evolutions(self):
        return self.evolutions and True or False

    def is_shiny(self):
        return self.shiny

    def fainted(self):
        return self.stats.health == 0

    def calc_shiny(self):
        shiny_chance = 100 / 2**13
        chance = random()

        if chance <= shiny_chance:
            self.shiny = True
        return self.is_shiny()

    def set_owner(self, member: Union[discord.Member, int]):
        if type(member) is discord.Member:
            self.owner = member.id
        else:
            member_id = member
            self.owner = member_id

    def reset_runtime_stats(self):
        self.stats.reset(runtime=True)

    def setup_stats(self):
        entry = Proxydex.get_entry_by(self.name)
        self.stats = self.base_stats * self.level
        self.experience.max = entry.exp_group.value(self.level)

        return self.stats

    def level_up(self, number: int = 1):
        if self.level >= 100:
            return False

        self.level += number
        self.setup_stats()
        return self.level

    def dump(self):
        return {
            "name": self.name,
            "owner": self.owner,
            "level": self.level,
            "female_chance": self.female_chance,
            "level_met": self.level_met,
            **self.base_stats.dump(),
            "moves": list(map(proxymon_dump, self.moves)),
            "learnset": list(map(proxymon_dump, self.learnset)),
            "evolutions": [],
            "shiny": self.shiny,
            "experience": self.experience.current,
            "met_at": self.met_at.value.dump(),
            "item": self.item.value.dump(),
            "gender": self.gender.name,
            "nature": self.nature.value.dump(),
            "ability": self.ability.value.dump(),
            "hidden_ability": self.hidden_ability.value.dump(),
            "rarity": self.rarity.name,
            "status": self.status.value.dump()
        }


class Starter(Enum):
    AITHOS = ProxymonBase("Aithos", level=5, rarity=Rarity.RARE,
                          ability=Ability.BLAZE,
                          hidden_ability=Ability.SOLAR_POWER,
                          female_chance=12.5)
    SALAQUA = ProxymonBase("Salaqua", level=5, rarity=Rarity.RARE,
                           ability=Ability.TORRENT,
                           hidden_ability=Ability.RAIN_DISH,
                           female_chance=12.5)
    XAZELA = ProxymonBase("Xazela", level=5, rarity=Rarity.RARE,
                          ability=Ability.OVERGROW,
                          hidden_ability=Ability.CHLOROPHYLL,
                          female_chance=12.5)

    def get_starter(proxymon: str):
        for s in Starter:
            if proxymon == s.name.title():
                return s.value
