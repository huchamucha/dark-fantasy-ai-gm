"""Зоны тела и HP (раздел 4 спецификации)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

class Zone(str, Enum):
    HEAD = "head"
    CHEST = "chest"
    ABDOMEN = "abdomen"
    LEFT_ARM = "left_arm"
    RIGHT_ARM = "right_arm"
    LEFT_LEG = "left_leg"
    RIGHT_LEG = "right_leg"

VITAL_ZONES = frozenset({Zone.HEAD, Zone.CHEST, Zone.ABDOMEN})

class ZoneState(str, Enum):
    OK = "ok"             # «Всё ок»: 40–100 %
    DAMAGED = "damaged"   # «Не очень»: >0 и <40 %
    CRITICAL = "critical" # «Критическое»: ровно 0
    SEVERE = "severe"     # «Очень не очень»: после критического, пока <40 %

# Согласовано OK_THRESHOLD = 0.40
# Согласовано: урон, пришедшийся на зону с 0 HP, усиливается в 1.5 раза.
# Это и удар по уже нулевой зоне, и остаток прямого удара сверх HP зоны.
ZERO_ZONE_DAMAGE_MULTIPLIER = 1.5
# Согласовано: усиленный урон перераспределяется по зонам с HP > 0,
# пока не кончится. Теряется только когда все зоны на нуле.
# ПРЕДВАРИТЕЛЬНО: недобор при перераспределении повторно не усиливается.

def _boost(amount: int) -> int:
    """Усиление урона по нулевой зоне. Половина округляется вверх
    (встроенный round() округляет 22.5 до 22)."""
    return math.floor(amount * ZERO_ZONE_DAMAGE_MULTIPLIER + 0.5)

def split_proportional(total: int, weights: list[int]) -> list[int]:
    """Делит целое число пропорционально весам (метод наибольшего остатка)."""
    s = sum(weights)
    if total <= 0 or s <= 0:
        return [0] * len(weights)
    raw = [total * w / s for w in weights]
    base = [int(r) for r in raw]
    rest = total - sum(base)
    order = sorted(range(len(raw)), key=lambda i: raw[i] - base[i], reverse=True)
    for i in order[:rest]:
        base[i] += 1
    return base

@dataclass
class BodyZone:
    zone: Zone
    max_hp: int
    hp: int
    was_critical: bool = False

    @property
    def ratio(self) -> float:
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    @property
    def state(self) -> ZoneState:
        if self.hp <= 0:
            return ZoneState.CRITICAL
        if self.ratio >= OK_THRESHOLD:
            return ZoneState.OK
        return ZoneState.SEVERE if self.was_critical else ZoneState.DAMAGED

@dataclass(frozen=True)
class Opportunity:
    zone: Zone
    kind: str  # "lethal_attack" | "amputation"

@dataclass
class DamageResult:
    applied: dict[Zone, int] = field(default_factory=dict)
    lost: int = 0
    opportunities: list[Opportunity] = field(default_factory=list)

@dataclass
class Body:
    zones: dict[Zone, BodyZone]

    @classmethod
    def create(cls, max_hp: dict[Zone, int]) -> "Body":
        # Формула HP от жизнеспособности не утверждена, max HP передаётся снаружи.
        return cls({z: BodyZone(z, max_hp[z], max_hp[z]) for z in Zone})

    @property
    def total_hp(self) -> int:
        return sum(z.hp for z in self.zones.values())

    @property
    def max_total_hp(self) -> int:
        return sum(z.max_hp for z in self.zones.values())

    def apply_damage(self, zone: Zone, amount: int) -> DamageResult:
        res = DamageResult()
        if amount <= 0:
            return res

        target = self.zones[zone]
        if target.hp > 0:
            dealt = min(amount, target.hp)
            self._hit(target, dealt, res)
            self._spread(_boost(amount - dealt), res)
        else:
            self._spread(_boost(amount), res)
        return res

    def _spread(self, remaining: int, res: DamageResult) -> None:
        """Распределяет урон по зонам с HP > 0 пропорционально их max HP.
        Недобор от обнулившихся зон распределяется повторно."""
        while remaining > 0:
            receivers = [z for z in self.zones.values() if z.hp > 0]
            if not receivers:
                res.lost += remaining
                return
            shares = split_proportional(remaining, [z.max_hp for z in receivers])
            leftover = 0
            for z, share in zip(receivers, shares):
                dealt = min(share, z.hp)
                self._hit(z, dealt, res)
                leftover += share - dealt
            remaining = leftover

    def heal(self, zone: Zone, amount: int) -> None:
        """Лечит HP. Травмы (Injury) отдельная сущность, лечение HP их не снимает."""
        if amount <= 0:
            return
        z = self.zones[zone]
        z.hp = min(z.max_hp, z.hp + amount)
        if z.ratio >= OK_THRESHOLD:
            z.was_critical = False

    def _hit(self, z: BodyZone, dealt: int, res: DamageResult) -> None:
        if dealt <= 0:
            return
        z.hp -= dealt
        res.applied[z.zone] = res.applied.get(z.zone, 0) + dealt
        if z.hp == 0:
            z.was_critical = True
            kind = "lethal_attack" if z.zone in VITAL_ZONES else "amputation"
            res.opportunities.append(Opportunity(z.zone, kind))
