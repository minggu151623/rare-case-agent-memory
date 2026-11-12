"""Check the finite FIFO absence expression by exact weighted enumeration."""

from fractions import Fraction
from itertools import product
from math import comb


def absence_formula(initial, attempts, focal, other):
    capacity = len(initial)
    last_focal = max((i for i, value in enumerate(initial, 1) if value), default=0)
    rate = focal + other
    if not rate:
        return Fraction(not last_focal)
    nonfocal_share = other / rate
    return sum(
        comb(attempts, admitted) * rate**admitted * (1 - rate)**(attempts - admitted)
        * nonfocal_share**min(admitted, capacity)
        for admitted in range(last_focal, attempts + 1)
    )


def enumerate_states(initial, attempts, focal, other):
    states = {initial: Fraction(1)}
    for _ in range(attempts):
        following = {}
        for state, weight in states.items():
            transitions = ((state, 1 - focal - other),
                           ((*state[1:], 0), other),
                           ((*state[1:], 1), focal))
            for target, chance in transitions:
                following[target] = following.get(target, Fraction(0)) + weight * chance
        states = following
    return states.get((0,) * len(initial), Fraction(0))


def main():
    cases = 0
    for capacity in range(1, 5):
        for initial in product((0, 1), repeat=capacity):
            for attempts in range(7):
                for focal_quarters in range(5):
                    for other_quarters in range(5 - focal_quarters):
                        focal, other = Fraction(focal_quarters, 4), Fraction(other_quarters, 4)
                        expected = absence_formula(initial, attempts, focal, other)
                        actual = enumerate_states(initial, attempts, focal, other)
                        if expected != actual:
                            raise AssertionError((initial, attempts, focal, other, expected, actual))
                        cases += 1
    print(f"{cases} exact finite-time FIFO absence checks passed")


if __name__ == "__main__":
    main()
