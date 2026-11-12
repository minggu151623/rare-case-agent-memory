"""Deterministic task pools for the E001a feasibility pilot."""

from dataclasses import asdict, dataclass, replace
from itertools import permutations
from random import Random

from src.planning import Edge, Task, shortest_distance

FAMILIES = ("ungated", "key_detour", "unreachable")
RARE = FAMILIES[1:]
REFERENCE_WEIGHTS = (80, 10, 10)


@dataclass(frozen=True)
class Case:
    id: str
    family: str
    task: Task

    def prompt_record(self) -> dict:
        return {"id": self.id, **asdict(self.task)}


def structural_key(task: Task) -> tuple:
    """Canonicalize the directed graph up to node renaming."""
    fixed = list(dict.fromkeys((task.start, task.goal, task.key_at)))
    fixed = [node for node in fixed if node is not None]
    nodes = {node for edge in task.edges for node in (edge.source, edge.destination)}
    free = sorted(nodes.difference(fixed))
    representations = []
    for order in permutations(free):
        labels = {node: index for index, node in enumerate((*fixed, *order))}
        edges = tuple(sorted(
            (labels[edge.source], labels[edge.destination], edge.requires_key)
            for edge in task.edges
        ))
        representations.append(edges)
    return len(fixed) + len(free), task.key_at is not None, min(representations)


def generate(family: str, rng: Random) -> Task:
    nodes = ("A", "B", "C", "D", "E", "F")
    start, goal, key = "A", "B", "C"
    if family == "ungated":
        key = None
        base = (Edge("A", "C"), Edge("C", "D"), Edge("D", "E"), Edge("E", "B"))
    elif family == "key_detour":
        base = (Edge("A", "D"), Edge("D", "C"), Edge("C", "D"), Edge("D", "B", True))
    elif family == "unreachable":
        base = (Edge("A", "D"), Edge("D", "B", True), Edge("C", "E"))
    else:
        raise ValueError(f"Unknown family: {family}")

    occupied = {(edge.source, edge.destination) for edge in base}
    extra = [Edge(a, b) for a, b in permutations(nodes, 2) if (a, b) not in occupied]
    for _ in range(1000):
        edges = list(base) + rng.sample(extra, 7 - len(base))
        if len({node for edge in edges for node in (edge.source, edge.destination)}) != 6:
            continue
        rng.shuffle(edges)
        task = Task(start, goal, tuple(edges), key)
        distance = shortest_distance(task)
        if family == "unreachable":
            # The unlocked base path is present by construction.
            if distance is None:
                return task
        elif distance == 4 and (
            key is None or shortest_distance(replace(task, key_at=None)) is None
        ):
            return task
    raise RuntimeError(f"Could not generate {family}")


def make_pools(seed: int, rounds: int) -> tuple:
    rng = Random(seed)
    seen = set()

    def pool(prefix: str, families: tuple[str, ...]) -> list[Case]:
        cases = []
        for index, family in enumerate(families):
            for _ in range(1000):
                task = generate(family, rng)
                key = structural_key(task)
                if key not in seen:
                    seen.add(key)
                    cases.append(Case(f"{prefix}{index}", family, task))
                    break
            else:
                raise RuntimeError(f"Could not generate unique {family} graph")
        rng.shuffle(cases)
        return cases

    initial = pool("i", (FAMILIES[0],) * 4 + RARE)
    menus = [pool(f"m{round_}-", FAMILIES * 3) for round_ in range(rounds)]
    supplements = [pool(f"s{round_}-", FAMILIES) for round_ in range(rounds)]
    holdout = pool("h", FAMILIES * 2)
    return initial, menus, supplements, holdout
