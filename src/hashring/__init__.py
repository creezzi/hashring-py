"""Consistent hashing."""
from __future__ import annotations

import bisect
import hashlib
from typing import Dict, Iterable, List, Optional

__all__ = ["HashRing"]


def _hash(key: str) -> int:
    return int.from_bytes(hashlib.md5(key.encode()).digest()[:8], "big")


class HashRing:
    def __init__(self, nodes: Iterable[str] = (), vnodes: int = 100):
        if vnodes < 1:
            raise ValueError("vnodes must be >= 1")
        self.vnodes = vnodes
        self._weights: Dict[str, int] = {}
        self._keys: List[int] = []
        self._owner: Dict[int, str] = {}
        for node in nodes:
            self.add(node)

    def __len__(self) -> int:
        return len(self._weights)

    def __contains__(self, node: object) -> bool:
        return node in self._weights

    def add(self, node: str, weight: int = 1) -> None:
        if node in self._weights:
            self.remove(node)
        self._weights[node] = weight
        for i in range(self.vnodes * weight):
            point = _hash(f"{node}#{i}")
            self._owner[point] = node
            bisect.insort(self._keys, point)

    def remove(self, node: str) -> None:
        weight = self._weights.pop(node)
        for i in range(self.vnodes * weight):
            point = _hash(f"{node}#{i}")
            if self._owner.get(point) == node:
                del self._owner[point]
                self._keys.pop(bisect.bisect_left(self._keys, point))

    def get(self, key: str) -> Optional[str]:
        nodes = self.get_nodes(key, 1)
        return nodes[0] if nodes else None

    def get_nodes(self, key: str, count: int) -> List[str]:
        """Up to `count` distinct nodes clockwise from the key (primary first)."""
        if not self._keys:
            return []
        want = min(count, len(self._weights))
        start = bisect.bisect(self._keys, _hash(key))
        found: List[str] = []
        for i in range(len(self._keys)):
            node = self._owner[self._keys[(start + i) % len(self._keys)]]
            if node not in found:
                found.append(node)
                if len(found) == want:
                    break
        return found
