from collections import defaultdict

messages: dict[str, list[dict]] = defaultdict(list)
blocked: set[str] = set()
reports: list[dict] = []
