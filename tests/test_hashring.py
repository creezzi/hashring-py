from collections import Counter

import pytest

from hashring import HashRing


def test_empty_ring():
    ring = HashRing()
    assert ring.get("k") is None and ring.get_nodes("k", 3) == []


def test_deterministic_and_member():
    ring = HashRing(["a", "b", "c"])
    assert ring.get("key") == ring.get("key") in {"a", "b", "c"}


def test_distribution_is_roughly_even():
    ring = HashRing(["a", "b", "c", "d"])
    counts = Counter(ring.get(f"k{i}") for i in range(8000))
    assert min(counts.values()) > 1200 and max(counts.values()) < 2800


def test_removing_a_node_only_moves_its_keys():
    ring = HashRing(["a", "b", "c", "d"])
    keys = [f"k{i}" for i in range(2000)]
    before = {k: ring.get(k) for k in keys}
    ring.remove("c")
    for k in keys:
        if before[k] != "c":
            assert ring.get(k) == before[k]
        else:
            assert ring.get(k) != "c"


def test_adding_a_node_moves_a_minority_of_keys():
    ring = HashRing(["a", "b", "c", "d"])
    keys = [f"k{i}" for i in range(2000)]
    before = {k: ring.get(k) for k in keys}
    ring.add("e")
    moved = sum(before[k] != ring.get(k) for k in keys)
    assert 0 < moved < 600


def test_replicas_are_distinct():
    ring = HashRing(["a", "b", "c"])
    nodes = ring.get_nodes("x", 5)
    assert len(nodes) == 3 and len(set(nodes)) == 3 and nodes[0] == ring.get("x")


def test_weight_attracts_more_keys():
    ring = HashRing(["a"])
    ring.add("heavy", weight=4)
    counts = Counter(ring.get(f"k{i}") for i in range(4000))
    assert counts["heavy"] > counts["a"] * 2


def test_invalid_vnodes():
    with pytest.raises(ValueError):
        HashRing(vnodes=0)
