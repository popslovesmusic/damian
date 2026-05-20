import pytest

from engine.domain.recovery import foothold_recovery_stub
from engine.inventory.runtime import inventory_transaction_stub


@pytest.fixture
def inventory_with_shards():
    inv = inventory_transaction_stub.make_default_inventory_state(player_id="p1")
    inv["currency"]["stability_shards"] = 50.0
    return inv


@pytest.fixture
def unstable_claim():
    return {
        "claim_id": "claim_recover_1",
        "status": "DECAYING",
        "territorial_instability": 0.8
    }


def test_recovery_spends_shards_and_reduces_instability(inventory_with_shards, unstable_claim):
    res = foothold_recovery_stub.recover_foothold(unstable_claim, inventory_with_shards, effort=2)
    assert res["ok"] is True
    assert res["inventory_state"]["currency"]["stability_shards"] < 50.0
    assert res["updated_claim"]["territorial_instability"] < 0.8
    assert 0.10 <= res["updated_claim"]["territorial_instability"] <= 1.0


def test_recovery_fails_without_shards(unstable_claim):
    inv = inventory_transaction_stub.make_default_inventory_state(player_id="p2")
    inv["currency"]["stability_shards"] = 0.0
    res = foothold_recovery_stub.recover_foothold(unstable_claim, inv, effort=1)
    assert res["ok"] is False
    assert res["error"] == "InsufficientResources"

