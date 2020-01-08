from typing import Union

from bot.experience import Group
from bot.stats import Stats
from bot.types import Type
from bot.types import TypeDual


class Entry(object):
    def __init__(self, name: str, type: Union[Type, TypeDual],
                 description: str = None, group: Group = Group.DEFAULT,
                 *stats):
        self.name = name
        self.type = type
        self.description = description or "`No description provided.`"
        self.desc = self.description  # alias
        self.id = None
        self.exp_group = group

        if len(stats) > 0:
            hp, *stats = stats
            self.stats = Stats(hp, hp, *stats)


class TrainerProxydex(object):
    def __init__(self, completed: bool, met: list, caught: list,
                 shinies: list):
        self.completed = completed
        self.met = met
        self.caught = caught
        self.shinies = shinies

    def __str__(self):
        return self.format()

    def add(self, proxymon):
        met = False
        caught = False

        if self.has_met(proxymon) is False:
            self.met.append(proxymon.id)
            met = True

        if self.has_caught(proxymon) is False:
            self.caught.append(proxymon.id)
            caught = True

        return met, caught

    def has_met(self, proxymon):
        return proxymon.id in self.met

    def has_caught(self, proxymon):
        return proxymon.id in self.caught

    def format(self):
        strings = []

        if self.completed:
            strings.append("COMPLETED!\n")

        strings.append(f"Met {len(self.met)} Proxymon")
        strings.append(f"Caught {len(self.caught)} Proxymon")

        if self.shinies != []:
            shinies = len(self.shinies) == 1 and "shiny" or "shinies"
            strings.append(f"{len(self.shinies)} {shinies}")

        return ("\n").join(strings)

    def dump(self):
        return {
            "completed": self.completed,
            "met": self.met,
            "caught": self.caught,
            "shinies": self.shinies
        }


class Proxydex(object):
    entries = [
        Entry("Xazela", Type.GRASS,
              "This grass type Proxymon is known as the deer of life. It's "
              "horns have flowers blooming at the end of it, which is called "
              "the \"Fire of Life.\""
              "it's end."),

        Entry("Xalabrat", TypeDual(GRASS=True, PSYCHIC=True),
              "Xazela's evolution makes it quite smug as it thinks it is "
              "above everyone else. It has multiple flowers on it's body and "
              "sunflowers on it's new and stronger horns."),

        Entry("Xatopia", TypeDual(GRASS=True, PSYCHIC=True),
              "Xatopia is the final evolution of Xazela. In this stage "
              "Xatopia has a beautiful, leafy cape and long elder branches "
              "with vines growing on them. Xatopia uses it's psychic powers "
              "to levitate itself on a rock to stand above others."),

        Entry("Aithos", Type.FIRE,
              "Aithos is a flaming baby horse. Changes in emotion can cause "
              "it's flames to increase or decrease rapidly."),

        Entry("Salaqua", Type.WATER,
              "Despite it's appearance, Salaqua is highly intelligent. It "
              "utilizes it's poison sacs on it's head, knees, and tail for "
              "lethal blows."),

        Entry("Salaswam", TypeDual(WATER=True, POISON=True),
              "Salaswam's tail grows off into another tail, increasing it's "
              "girth for stronger attacks. It's poisonous buds help it to "
              "stick to walls."),

        Entry("Soruptolum", TypeDual(WATER=True, POISON=True),
              None),

        Entry("Layphe", Type.FAIRY,
              None),

        Entry("Forko", TypeDual(DARK=True, NORMAL=True),
              "These Proxymon are said to be the largest amount of Proxymon "
              "in the world due to breeding and avoiding conflict."),

        Entry("Harko", TypeDual(DARK=True, STEEL=True),
              "Compared to it's pre-evolved state this Proxymon is considered "
              "one of the strongest. It's fur has become metal making the "
              "only weak spots on it's body small hard to hit places."),

        Entry("Newster", TypeDual(WATER=True, POISON=True),
              "This is a Proxymon that lives in the sewers. Because of this, "
              "the body is 95% toxic waste while the feet are 100% Sewage. "
              "The body is full of holes that constantly release deadly gas. "
              "Two eyes mutated on top of the head."),

        Entry("Tenofa", TypeDual(FIRE=True, ICE=True),
              "This seal-like Proxymon's tails are eternally aflame. When "
              "diving the flame constantly makes steam. The steam is used to "
              "hide itself from enemies."),

        Entry("Gwhodin", Type.GHOST,
              "A cursed book brought to life through the cursed bookmark. It "
              "radiates a psychic, ghastly aura. The book has multiple walls "
              "of forbidden tome texts."),

        Entry("Hagouiji", TypeDual(GHOST=True, UNKNOWN=True),
              "Hagouijis are formed when a trainer constantly reads a Gwhodin "
              "causing the Gwhodin to allow the trainer to see it's secret "
              "pages. Once the trainer reads said pages Gwhodin will evolve "
              "into Hagouiji. However only the most elite trainers are "
              "capable of accomplishing this task and keeping the Hagouiji "
              "under control."),

        Entry("Velerapro", Type.ROCK,
              "This Proxymon was found as a fossil in the region and revived "
              "with modern technology. The Proxymon itself resembles a "
              "Velociraptor as shown by it's single large toe on each foot."),

        Entry("Paporaptor", TypeDual(ROCK=True, DRAGON=True),
              "Upon evolving, Velerapro gains a birdlike appearance. This "
              "helps Paporaptor move faster and more viciously."),

        Entry("Lavin", TypeDual(FIRE=True, ROCK=True),
              None),

        Entry("Magoni", TypeDual(FIRE=True, ROCK=True),
              None),

        Entry("Doros", Type.DARK,
              "It wears the scarf of it's dead father and steals money from "
              "young children during the night. If it is ever in danger, it "
              "can become invisible to deceive predators and attack them at "
              "the most unexpected time. They can be found in the shadows "
              "hiding from the day light."),

        Entry("Daroxoros", TypeDual(DARK=True, GHOST=True),
              None)
    ]

    def get_entry(entry_no: int):
        if entry_no <= 0:
            return None

        try:
            entry = Proxydex.entries[entry_no-1]
            entry.id = entry_no

            return entry
        except (KeyError, IndexError):
            return None

    def get_entry_by(no_or_name: Union[int, str]):
        if type(no_or_name) is str:
            for i, entry in enumerate(Proxydex.entries):
                if entry.name == no_or_name:
                    entry.id = i + 1

                    return entry
        elif type(no_or_name) is int:
            return Proxydex.get_entry(no_or_name)
        return None
