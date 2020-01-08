from math import floor


class Health(object):
    def __init__(self, current: int, max: int):
        self.current = current
        self.max = max

    def __mul__(self, level):
        return Health(
            floor(self.current * level),
            floor(self.max * level)
        )

    def dump(self):
        return {
            "hp": self.current,
            "hp_max": self.max
        }


class StatHolder(object):
    def __init__(self, stat: int, sp_stat: int):
        self.physical = stat
        self.special = sp_stat

    def __mul__(self, level):
        return StatHolder(
            floor(self.physical * level),
            floor(self.special * level)
        )

    def __imul__(self, level):
        self.physical = floor(self.physical * level)
        self.special = floor(self.special * level)


class Multipliers(object):
    def __init__(self):
        self.min = -6
        self.max = 6
        self.attack = 0
        self.defense = 0
        self.sp_attack = 0
        self.sp_defense = 0
        self.speed = 0

    def __repr__(self):
        return (f"{type(self).__class__.__name__}("
                f"min={self.min}, "
                f"max={self.max}, "
                f"attack={self.attack}, "
                f"defense={self.defense}, "
                f"sp_attack={self.sp_attack}, "
                f"sp_defense={self.sp_defense}, "
                f"speed={self.speed})")

    def increase(self, multiplier: int, value: int):
        if multiplier == self.max:
            return False

        multiplier += value

        if multiplier > self.max:
            multiplier = self.max
        return True

    def decrease(self, multiplier: int, value: int):
        if multiplier == self.min:
            return False

        multiplier -= value

        if multiplier < self.min:
            multiplier = self.min
        return True

    def get_multiplier(self, stage: str):
        if stage == 0:
            return 1
        elif stage > 0:
            return (2 + stage) / 2
        elif stage < 0:
            return 2 / -(stage - 2)
        return None

    def reset(self):
        self.__init__()


class Stats(object):
    def __init__(self, hp: int, hp_max: int, attack: int, defense: int,
                 sp_attack: int, sp_defense: int, speed: int):
        self.stats = [hp, attack, defense, sp_attack, sp_defense, speed]
        self.health = Health(hp, hp_max)
        self.attack = StatHolder(attack, sp_attack)
        self.defense = StatHolder(defense, sp_defense)
        self.speed = speed

        # runtime stats
        self.accuracy = 0
        self.evasion = 0
        self.multipliers = Multipliers()

    def __mul__(self, level):
        level = level / 50
        attack = self.attack * level
        defense = self.defense * level
        health = self.health * level

        return Stats(
            health.current,
            health.max,
            attack.physical,
            defense.physical,
            attack.special,
            defense.special,
            floor(self.speed * level)
        )

    def __imul__(self, level):
        self.attack *= level
        self.defense *= level
        self.speed *= level

    def __repr__(self):
        return (f"{type(self).__class__.__name__}("
                f"hp={self.health.current}, "
                f"hp_max={self.health.max}, "
                f"attack={self.attack.physical}, "
                f"defense={self.defense.physical}, "
                f"sp_attack={self.attack.special}, "
                f"sp_defense={self.defense.special}, "
                f"speed={self.speed}, accuracy={self.accuracy}, "
                f"evasion={self.evasion}, "
                f"multipliers={repr(self.multipliers)})")

    def get_multiplier(self, stage: str):
        if stage == 0:
            return 1
        elif stage > 0:
            return (stage + 3) / 3
        elif stage < 0:
            return 3 / -(stage - 3)
        return None

    def reset(self, runtime: bool = False):
        if runtime:
            self.accuracy = 0
            self.evasion = 0
            self.multipliers.reset()
        else:
            self.__init__(*[50]*7)

    def dump(self):
        return {
            **self.health.dump(),
            "attack": self.attack.physical,
            "defense": self.defense.physical,
            "sp_attack": self.attack.special,
            "sp_defense": self.defense.special,
            "speed": self.speed
        }


class EVs(Stats):
    def __init__(self, *args):
        super().__init__(*args)

    def total(self):
        return sum([self.attack, self.defense, self.sp_attack, self.sp_defense,
                    self.speed])
