from datetime import datetime
from typing import Union

import discord

from bot.locations import Location
from bot.proxydex import TrainerProxydex
from bot.utils import get_timezone


class TrainerBase(object):
    def __init__(self, name: str, gender: str, id: int, team: list, money: int,
                 location: str):
        from bot.proxymon import ProxymonBase

        self.name = name
        self.gender = gender
        self.id = id
        self.team = []
        self.money = money
        self.location = Location[location]

        for proxymon in team:
            if proxymon is not None:
                proxymon = ProxymonBase(**proxymon)

            self.team.append(proxymon)

    def at_location(self, location: Location):
        return self.location == location

    def process_name(self, member: discord.Member):
        if self.name is None:
            return member.name
        return self.name

    def dump_team(self):
        from bot.proxymon import ProxymonBase

        dump = []

        for proxymon in self.team:
            is_proxymon = type(proxymon) is ProxymonBase

            if proxymon is not None and is_proxymon:
                proxymon = proxymon.dump()
            dump.append(proxymon)
        return dump

    def dump(self):
        return {
            "name": self.name,
            "id": self.id,
            "team": self.dump_team(),
            "money": self.money,
            "location": self.location.value.dump()
        }

    async def edit(self, **attribs):
        for k, v in attribs.items():
            setattr(self, k, v)

        return self

    async def add_to_team(self, *args):
        added = 0

        for proxymon in args:
            if proxymon.owner is None:
                proxymon.set_owner(self.id)
                proxymon.level_met = proxymon.level
                proxymon.met_at = self.location

            for pos, trainer_proxymon in enumerate(self.team):
                if trainer_proxymon is None:
                    added += 1
                    self.team[pos] = proxymon
                    self.proxydex.add(proxymon)

                    break
        return added != 0 and added


class Trainer(TrainerBase):
    def __init__(self, name, gender, id, team, money, location,
                 starter: Union[bool, str], registered: int, proxydex: dict):
        super().__init__(name, gender, id, team, money, location)
        self.starter = starter
        self.registered = registered
        self.proxydex = TrainerProxydex(**proxydex)

    def is_new(self):
        now = datetime.now()
        difference = now - datetime.utcfromtimestamp(self.registered)

        return difference.days < 1

    def format_reg_date(self, date_format=None):
        datetime_obj = datetime.utcfromtimestamp(self.registered)

        if date_format is None:
            date_format = f"%I:%M:%S %p ({get_timezone()}) %m/%d/%Y"

        return datetime_obj.strftime(date_format)

    def dump(self, safe=False):
        if safe:
            pass
        return {
            **super().dump(),
            "starter": self.starter,
            "registered": self.registered,
            "proxydex": self.proxydex.dump(),
        }
