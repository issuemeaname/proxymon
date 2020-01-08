import datetime
import json
import os
import random
from typing import Union

import aiofiles
import discord

from bot.locations import Location
from bot.trainer import Trainer


class _JsonDB(object):
    def __init__(self, path: str):
        self.path = path
        self.db = None

    async def get(self):
        if getattr(self, "db", None) is None:
            self.db = dict()
            db_exists = os.path.exists(self.path)
            db_is_empty = db_exists and os.path.getsize(self.path) == 0
            mode = "r+" if db_exists else "w+"

            async with aiofiles.open(self.path, mode) as db:
                if db_is_empty:
                    dump = json.dumps(self.db, indent=4)
                    await db.write(dump)
                elif db_exists:
                    dump = await db.read()
                    self.db = json.loads(dump)
        return self.db

    async def save(self):
        await self.get()

        async with aiofiles.open(self.path, "w") as db:
            dump = json.dumps(self.db, indent=4)
            await db.write(dump)

        return self.db


class _CsvDB(object):
    def __init__(self, path):
        self.path = path

    async def get(self):
        with aiofiles.open(self.path, "r") as db:
            data = db.read()

            return data.split(",")

    async def random(self):
        db = await self.get()

        return random.choice(db)


class _Database(_JsonDB):
    def __init__(self, path):
        super().__init__(path)

    async def get_default(self):
        await self.get()

        return {
            "id": len(self.db.keys()) + 1,
            "proxydex": {
                "completed": False,
                "met": [],
                "caught": [],
                "shinies": []
            },
            "team": [None]*6,
            "starter": None,
            "name": "",
            "gender": "",
            "money": 0,
            "registered": int(datetime.datetime.now().timestamp()),
            "location": Location.STARTER_TOWN.value.dump(),
            # "settings": {}
            # "system": [[None]*36]*12
        }

    async def create_trainer(self, member: discord.Member, **kwargs):
        await self.get()
        default = await self.get_default()
        attribs = self.db.setdefault(str(member.id))

        if kwargs is None:
            attribs = default.update(kwargs)
            self.db[str(member.id)] = attribs

        await self.save()
        return Trainer(**attribs)

    async def get_trainer(self, member: Union[discord.Member, discord.User]):
        from bot.proxymon import ProxymonBase

        await self.get()
        kwargs = self.db.get(str(member.id))
        default = await self.get_default()

        if kwargs is None:
            return None

        for k, v in default.items():
            if k == "team":
                v = [p and ProxymonBase(**p) for p in v]

            kwargs.setdefault(k, v)
        return Trainer(**kwargs)

    async def edit_trainer(self,
                           trainer: Union[Trainer, discord.Member,
                                          discord.User], **attribs):
        await self.get()

        if type(trainer) is not Trainer:
            trainer = await self.get_trainer(trainer)

        for k, v in attribs.items():
            trainer[k] = v

        await self.save()

        try:
            return Trainer(**trainer)
        except TypeError:
            return trainer

    async def save_trainer(self, trainer: Union[Trainer,
                                                discord.Member,
                                                discord.User]):
        await self.get()

        if type(trainer) is not Trainer:
            trainer = await self.get_trainer(trainer)

        stats = trainer.dump()
        self.db[str(trainer.id)] = stats

        await self.save()
        return True

    async def remove_trainer(self, trainer: Union[discord.Member,
                                                  discord.User]):
        await self.get()

        self.db.pop(str(trainer.id))

        await self.save()
        return True


class _Blacklist(_JsonDB):
    def __init__(self, path):
        super().__init__(path)

    async def get(self):
        blacklist = await super().get()
        blacklist.setdefault("blacklist", list())

        return blacklist

    async def add(self, member: Union[discord.Member, discord.User]):
        await self.get()
        blacklist = self.db.get("blacklist")
        mid = member.id

        if mid not in blacklist:
            blacklist.append(mid)
            await self.save()

            return mid
        return False

    async def remove(self, member: Union[discord.Member, discord.User]):
        await self.get()
        blacklist = self.db.get("blacklist")
        mid = member.id

        if mid in blacklist:
            blacklist.remove(mid)
            await self.save()

            return mid
        return False

    async def check(self, member: Union[discord.Member, discord.User]):
        await self.get()

        return member.id in self.db.get("blacklist")


Database = _Database(r"bot\files\db.json")
Blacklist = _Blacklist(r"bot\files\blacklist.json")
Names = _CsvDB(r"bot\files\names.csv")


async def save_dbs():
    await Database.save()
    await Blacklist.save()
