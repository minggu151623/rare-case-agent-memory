"""Exact solver and answer scorer for a unit-cost planning domain."""

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Edge:
    source: str
    destination: str
    requires_key: bool = False


@dataclass(frozen=True)
class Task:
    start: str
    goal: str
    edges: tuple[Edge, ...]
    key_at: str | None = None


def shortest_path(task: Task) -> tuple[str, ...] | None:
    """Return an optimal path, or None if the goal is unreachable."""
    outgoing: dict[str, list[Edge]] = {}
    for edge in task.edges:
        outgoing.setdefault(edge.source, []).append(edge)

    initial = (task.start, task.start == task.key_at)
    queue = deque([(initial, (task.start,))])
    visited = {initial}

    while queue:
        (location, has_key), path = queue.popleft()
        if location == task.goal:
            return path

        for edge in outgoing.get(location, ()):
            if edge.requires_key and not has_key:
                continue
            state = (edge.destination, has_key or edge.destination == task.key_at)
            if state not in visited:
                visited.add(state)
                queue.append((state, (*path, edge.destination)))
    return None


def shortest_distance(task: Task) -> int | None:
    """Return the minimum number of moves, or None if the goal is unreachable."""
    path = shortest_path(task)
    return None if path is None else len(path) - 1


def is_correct(task: Task, answer: object) -> bool:
    """Check a JSON-compatible answer of the form {"path": [...]} or
    {"unreachable": true}.
    """
    if not isinstance(answer, dict):
        return False

    if answer.keys() == {"unreachable"}:
        return answer["unreachable"] is True and shortest_distance(task) is None
    if answer.keys() != {"path"}:
        return False

    path = answer["path"]
    if not isinstance(path, list) or not path:
        return False
    if not all(isinstance(node, str) for node in path):
        return False
    if path[0] != task.start or path[-1] != task.goal:
        return False

    has_key = task.start == task.key_at
    for source, destination in zip(path, path[1:]):
        if not any(
            edge.source == source and edge.destination == destination
            and (has_key or not edge.requires_key)
            for edge in task.edges
        ):
            return False
        has_key = has_key or destination == task.key_at

    return len(path) - 1 == shortest_distance(task)
