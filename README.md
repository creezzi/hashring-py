# hashring

Consistent hash ring with virtual nodes and weighted members.

## Usage

```python
from hashring import HashRing

ring = HashRing(["cache-a", "cache-b", "cache-c"])
ring.get("user:42")            # -> "cache-b"
ring.get_nodes("user:42", 2)   # primary + replica
```

## Test

```bash
pip install pytest && pytest
```

## License

MIT
