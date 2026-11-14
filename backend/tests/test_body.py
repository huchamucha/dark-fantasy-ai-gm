import pytest
from app.engine.body import Body, Zone, OK_THRESHOLD

def test_body_full_damage():
    max_hp = {z: 10 for z in Zone}
    body = Body.create(max_hp)
    res = body.apply_damage(Zone.HEAD, 10)
    assert res.applied[Zone.HEAD] == 10
    assert body.zones[Zone.HEAD].hp == 0
    assert body.zones[Zone.HEAD].was_critical
    # Проверка перераспределения
    body = Body.create(max_hp)
    res = body.apply_damage(Zone.HEAD, 15)
    assert res.applied[Zone.HEAD] == 10
    # 5 усиляется и распределяется -> другие зоны по 1 или 2
    left = sum(res.applied[z] for z in Zone if z != Zone.HEAD)
    assert left == 5 * 1.5 // 1

def test_body_heal():
    max_hp = {z: 10 for z in Zone}
    body = Body.create(max_hp)
    body.apply_damage(Zone.LEFT_ARM, 7)
    body.heal(Zone.LEFT_ARM, 5)
    assert body.zones[Zone.LEFT_ARM].hp == 8
    body.heal(Zone.LEFT_ARM, 10)
    assert body.zones[Zone.LEFT_ARM].hp == 10

@pytest.mark.parametrize("amount", [3, 10, 15])
def test_damage_not_below_zero(amount):
    max_hp = {z: 10 for z in Zone}
    body = Body.create(max_hp)
    body.apply_damage(Zone.CHEST, amount)
    assert body.zones[Zone.CHEST].hp >= 0
