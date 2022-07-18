# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
# ======================================================================================

from collections import Counter
from enum import IntEnum, auto
from fractions import Fraction

import pytest
from numerary import RealLike

from dyce import H, P
from dyce.evaluation import (
    Direction,
    HResult,
    KaronenCache,
    PResult,
    PWithSelection,
    _KOutcomeNode,
    _NHNode,
    expandable,
    explode,
    foreach,
    skipable_roll_gen,
    skipable_rolls_gen,
)
from dyce.h import HOrOutcomeT
from tests.test_p import _rwc_homogeneous_n_h_using_multinomial_coefficient

__all__ = ()


# ---- Tests ---------------------------------------------------------------------------


def test_skipable_roll_gen() -> None:
    cache = KaronenCache()
    candidates = (
        (8, H(6)),
        (8, H({1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2})),
        (8, H((2, 3, 3, 4, 4, 5))),
        (4, H({0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1})),
        (4, H({0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2})),
        (4, H({0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10})),
        (4, H({0: 10, 1: 9, 2: 8, 3: 7, 4: 6, 5: 5, 6: 4, 7: 3, 8: 2, 9: 1})),
        (4, H({0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 5, 6: 4, 7: 3, 8: 2, 9: 1})),
        (4, H({0: 2, 1: 4, 2: 6, 3: 8, 4: 10, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2})),
    )

    for n, h in candidates:
        for direction in Direction:
            skipable_roll_gen_res = Counter(
                {
                    tuple(sorted(Counter(roll).elements())): total
                    for roll, total in skipable_roll_gen(
                        n,
                        h,
                        direction=direction,
                        include_partial_rolls=False,
                        cache=cache,
                    )
                }
            )
            rolls_with_counts_res = Counter(
                {
                    roll: count
                    for roll, count in _rwc_homogeneous_n_h_using_multinomial_coefficient(
                        n, h
                    )
                }
            )
            assert skipable_roll_gen_res == rolls_with_counts_res


def test_skipable_roll_gen_empty() -> None:
    for direction in Direction:
        for n, h in (
            (0, H({})),
            (100, H({})),
            (0, H(100)),
        ):
            assert tuple(skipable_roll_gen(n, h, direction=direction)) == (((), 1),)


def test_skipable_roll_gen_cull() -> None:
    cache = KaronenCache()
    n = 4
    h = H(3)

    first_n = [
        ((), 81),
        ((1, 1, 1, 1), 1),
        ((1, 1, 1), 8),
        ((1, 1), 24),
        ((1,), 32),
        ((1, 1, 1, 2), 4),
        ((1, 1, 2, 2), 6),
        ((1, 2, 2, 2), 4),
        ((2, 2, 2, 2), 1),
        ((1, 1, 1, 3), 4),
        ((1, 1, 2, 3), 12),
        ((1, 1, 3, 3), 6),
        ((1, 2, 2, 3), 12),
        ((1, 2, 3, 3), 12),
        ((1, 3, 3, 3), 4),
        ((2, 2, 2, 3), 4),
        ((2, 2, 3, 3), 6),
        ((2, 3, 3, 3), 4),
        ((3, 3, 3, 3), 1),
    ]

    g = skipable_roll_gen(n, h, direction=Direction.LEAST_TO_GREATEST, cache=cache)
    assert [next(g) for _ in range(len(first_n))] == first_n

    g = skipable_roll_gen(n, h, direction=Direction.LEAST_TO_GREATEST, cache=cache)
    assert next(g) == ((), 81)
    assert next(g) == ((1, 1, 1, 1), 1)
    assert next(g) == ((1, 1, 1), 8)
    assert next(g) == ((1, 1), 24)
    g.send(True)
    assert next(g) == ((1,), 32)
    g.send(True)
    assert next(g) == ((1, 1, 1, 2), 4)

    assert next(g) == ((2, 2, 2, 2), 1)
    assert next(g) == ((1, 1, 1, 3), 4)

    assert next(g) == ((2, 2, 2, 3), 4)
    assert next(g) == ((2, 2, 3, 3), 6)
    assert next(g) == ((2, 3, 3, 3), 4)
    assert next(g) == ((3, 3, 3, 3), 1)

    with pytest.raises(StopIteration):
        next(g)

    g = skipable_roll_gen(10, H(10), direction=Direction.GREATEST_TO_LEAST, cache=cache)
    assert next(g) == ((), 10000000000)
    g.send(True)

    with pytest.raises(StopIteration):
        next(g)

    g = skipable_roll_gen(2, H(3), direction=Direction.GREATEST_TO_LEAST, cache=cache)
    assert next(g) == ((), 9)
    assert next(g) == ((3, 3), 1)
    assert next(g) == ((3,), 4)
    g.send(True)

    assert next(g) == ((2, 2), 1)

    assert next(g) == ((1, 2), 2)
    assert next(g) == ((1, 1), 1)

    with pytest.raises(StopIteration):
        next(g)


def test_skipable_rolls_gen() -> None:
    cache = KaronenCache()
    candidates = (
        (4 @ P(4),),
        (P(2), P(3)),
        (2 @ P(3), 3 @ P(4)),
    )

    for ps in candidates:
        for direction in Direction:
            n_h_node_rolls_gen: Counter[tuple[RealLike, ...]] = Counter()
            max_values = sum(len(p) for p in ps)

            for p_roll_dict_counts in skipable_rolls_gen(
                *ps, direction=direction, cache=cache
            ):
                aggregate_roll: list[RealLike] = []
                aggregate_count = 1

                for p, roll_dict, count in p_roll_dict_counts:
                    num_values = len(roll_dict)
                    assert num_values <= len(p), "more values than histograms"

                    if num_values < len(p):
                        break

                    aggregate_roll.extend(Counter(roll_dict).elements())
                    aggregate_count *= count

                if len(aggregate_roll) == max_values:
                    n_h_node_rolls_gen.update(
                        {tuple(sorted(aggregate_roll)): aggregate_count}
                    )

            p_rolls_with_counts: Counter[tuple[RealLike, ...]] = Counter()

            for roll, count in (P(*ps)).rolls_with_counts():
                p_rolls_with_counts.update({roll: count})

            assert n_h_node_rolls_gen == p_rolls_with_counts, f"{direction}"


def test_skipable_rolls_gen_empty() -> None:
    for direction in Direction:
        assert tuple(skipable_rolls_gen(direction=direction)) == ()
        assert tuple(skipable_rolls_gen(P(), direction=direction)) == (((P(), (), 1),),)
        assert tuple(skipable_rolls_gen(P(), P(), direction=direction)) == (
            ((P(), (), 1), (P(), (), 1)),
        )


def test_skipable_rolls_gen_cull() -> None:
    cache = KaronenCache()
    p_2d3 = 2 @ P(3)
    p_3d4 = 3 @ P(4)
    ps = p_2d3, p_3d4

    first_n = [
        ((p_2d3, (), 9), (p_3d4, (), 64)),
        ((p_2d3, (), 9), (p_3d4, (4, 4, 4), 1)),
        ((p_2d3, (), 9), (p_3d4, (4, 4), 9)),
        ((p_2d3, (), 9), (p_3d4, (4,), 27)),
        ((p_2d3, (3, 3), 1), (p_3d4, (4, 4, 4), 1)),
        ((p_2d3, (3,), 4), (p_3d4, (4, 4, 4), 1)),
        ((p_2d3, (3, 3), 1), (p_3d4, (3, 4, 4), 3)),
        ((p_2d3, (3, 3), 1), (p_3d4, (4, 4), 6)),
        ((p_2d3, (3,), 4), (p_3d4, (3, 4, 4), 3)),
        ((p_2d3, (3,), 4), (p_3d4, (4, 4), 6)),
        ((p_2d3, (), 4), (p_3d4, (3, 4, 4), 3)),
        ((p_2d3, (3, 3), 1), (p_3d4, (3, 3, 4), 3)),
        ((p_2d3, (3, 3), 1), (p_3d4, (3, 4), 12)),
        ((p_2d3, (3, 3), 1), (p_3d4, (4,), 12)),
        ((p_2d3, (3,), 4), (p_3d4, (3, 3, 4), 3)),
        ((p_2d3, (3,), 4), (p_3d4, (3, 4), 12)),
        ((p_2d3, (3,), 4), (p_3d4, (4,), 12)),
        ((p_2d3, (), 4), (p_3d4, (3, 3, 4), 3)),
    ]

    g = skipable_rolls_gen(*ps, direction=Direction.GREATEST_TO_LEAST, cache=cache)
    assert [next(g) for _ in range(len(first_n))] == first_n

    g = skipable_rolls_gen(*ps, direction=Direction.GREATEST_TO_LEAST, cache=cache)

    assert next(g) == ((p_2d3, (), 9), (p_3d4, (), 64))
    assert next(g) == ((p_2d3, (), 9), (p_3d4, (4, 4, 4), 1))
    assert next(g) == ((p_2d3, (), 9), (p_3d4, (4, 4), 9))
    g.send(True)
    assert next(g) == ((p_2d3, (), 9), (p_3d4, (4,), 27))
    g.send(True)
    assert next(g) == (
        (p_2d3, (3, 3), 1),
        (p_3d4, (4, 4, 4), 1),
    )
    assert next(g) == ((p_2d3, (3,), 4), (p_3d4, (4, 4, 4), 1))

    assert next(g) == ((p_2d3, (3, 3), 1), (p_3d4, (3, 3, 3), 1))
    assert next(g) == ((p_2d3, (3, 3), 1), (p_3d4, (3, 3), 6))
    assert next(g) == ((p_2d3, (3, 3), 1), (p_3d4, (3,), 12))
    assert next(g) == ((p_2d3, (3, 3), 1), (p_3d4, (), 8))
    assert next(g) == ((p_2d3, (3,), 4), (p_3d4, (3, 3, 3), 1))
    assert next(g) == ((p_2d3, (3,), 4), (p_3d4, (3, 3), 6))
    assert next(g) == ((p_2d3, (3,), 4), (p_3d4, (3,), 12))
    assert next(g) == ((p_2d3, (3,), 4), (p_3d4, (), 8))
    assert next(g) == ((p_2d3, (), 4), (p_3d4, (3, 3, 3), 1))
    assert next(g) == ((p_2d3, (), 4), (p_3d4, (3, 3), 6))
    assert next(g) == ((p_2d3, (), 4), (p_3d4, (3,), 12))

    p_10d10 = 10 @ P(10)
    g = skipable_rolls_gen(p_10d10, direction=Direction.LEAST_TO_GREATEST, cache=cache)
    assert next(g) == ((p_10d10, (), 10000000000),)
    g.send(True)

    with pytest.raises(StopIteration):
        next(g)

    p_d3 = P(3)
    g = skipable_rolls_gen(
        p_d3, p_d3, direction=Direction.LEAST_TO_GREATEST, cache=cache
    )
    assert next(g) == ((p_d3, (), 3), (p_d3, (), 3))
    assert next(g) == ((p_d3, (1,), 1), (p_d3, (1,), 1))
    assert next(g) == ((p_d3, (1,), 1), (p_d3, (), 2))
    g.send(True)
    assert next(g) == ((p_d3, (), 2), (p_d3, (1,), 1))
    g.send(True)
    assert next(g) == ((p_d3, (2,), 1), (p_d3, (2,), 1))
    assert next(g) == ((p_d3, (2,), 1), (p_d3, (), 1))
    g.send(True)
    assert next(g) == ((p_d3, (), 1), (p_d3, (2,), 1))
    g.send(True)
    assert next(g) == ((p_d3, (3,), 1), (p_d3, (3,), 1))

    with pytest.raises(StopIteration):
        next(g)


def test_karonen_cache() -> None:
    n = 4
    h = H(6)
    cache = KaronenCache()
    assert (n, h) not in cache

    n_h_node = cache[n, h]
    assert (n, h) in cache
    assert n_h_node == _NHNode(n, h)


def test_karonen_cache_empty() -> None:
    cache = KaronenCache()
    assert (0, H({})) not in cache

    n_h_node_empty = cache[0, H({})]
    assert n_h_node_empty == _NHNode(0, H({}))

    n = 100
    assert cache[n, H({})] is n_h_node_empty
    assert (n, H({})) not in cache

    h = H(100)
    assert cache[0, h] is n_h_node_empty
    assert (0, h) not in cache


def test_karonen_cache_h_equivalence() -> None:
    n = 4
    h2 = H({i: 10 for i in range(3, 0, -1)})
    h = h2.lowest_terms()
    assert h2 is not h

    cache = KaronenCache()
    assert (n, h) not in cache
    assert (n, h2) not in cache

    h2_n_node = cache[n, h2]
    assert (n, h) in cache
    assert (n, h2) in cache

    n_h_node = cache[n, h]
    assert h2_n_node is n_h_node
    assert h2_n_node.h.lowest_terms() is h2_n_node.h


def test_karonen_cache_n_negative() -> None:
    n = -1
    h = H(6)
    cache = KaronenCache()

    with pytest.raises(ValueError):
        cache[n, h]

    assert (n, h) not in cache


def test_expandable_equivalence_heterogeneous_pool() -> None:
    d4 = H(4)
    d6 = H(6) + 4
    p_3d42d6 = P(d4, d4, d4, d6, d6)

    @expandable
    def roll_sum(result: PResult):
        return sum(result.roll)

    assert roll_sum(p_3d42d6) == H(
        (sum(roll), count) for roll, count in p_3d42d6.rolls_with_counts()
    )

    head_sum = H((sum(roll[:3]), count) for roll, count in p_3d42d6.rolls_with_counts())

    assert head_sum == H(
        (sum(roll), count) for roll, count in p_3d42d6.rolls_with_counts(slice(None, 3))
    )

    assert head_sum == H(
        (sum(roll), count)
        for roll, count in p_3d42d6.rolls_with_counts(slice(None, -2))
    )

    @expandable
    def roll_sum_head_p(result: PResult):
        return sum(result.roll[:3])

    assert roll_sum_head_p(p_3d42d6) == head_sum

    @expandable
    def roll_sum_head_p_with_selection(result: PResult):
        return sum(result.roll)

    assert (
        roll_sum_head_p_with_selection(PWithSelection(p_3d42d6, (0, 1, 2)))
        == roll_sum_head_p_with_selection(PWithSelection(p_3d42d6, (-5, -4, -3)))
        == head_sum
    )

    tail_sum = H(
        (sum(roll[-3:]), count) for roll, count in p_3d42d6.rolls_with_counts()
    )

    assert tail_sum == H(
        (sum(roll), count)
        for roll, count in p_3d42d6.rolls_with_counts(slice(-3, None))
    )

    assert tail_sum == H(
        (sum(roll), count) for roll, count in p_3d42d6.rolls_with_counts(slice(2, None))
    )

    @expandable
    def roll_sum_tail_p(result: PResult):
        return sum(result.roll[-3:])

    assert roll_sum_tail_p(p_3d42d6) == tail_sum

    @expandable
    def roll_sum_tail_p_with_selection(result: PResult):
        return sum(result.roll)

    assert (
        roll_sum_tail_p_with_selection(PWithSelection(p_3d42d6, (-3, -2, -1)))
        == roll_sum_tail_p_with_selection(PWithSelection(p_3d42d6, (2, 3, 4)))
        == tail_sum
    )

    mid_sum = H(
        (sum(roll[1:-1]), count) for roll, count in p_3d42d6.rolls_with_counts()
    )

    assert mid_sum == H(
        (sum(roll), count) for roll, count in p_3d42d6.rolls_with_counts(slice(1, -1))
    )

    @expandable
    def roll_sum_mid_p(result: PResult):
        return sum(result.roll[1:-1])

    assert roll_sum_mid_p(p_3d42d6) == mid_sum

    @expandable
    def roll_sum_mid_p_with_selection(result: PResult):
        return sum(result.roll)

    assert (
        roll_sum_mid_p_with_selection(PWithSelection(p_3d42d6, (slice(1, -1),)))
        == mid_sum
    )

    window_sum = H(
        (sum(roll[1::2]), count) for roll, count in p_3d42d6.rolls_with_counts()
    )

    assert window_sum == H(
        (sum(roll), count)
        for roll, count in p_3d42d6.rolls_with_counts(slice(1, None, 2))
    )

    @expandable
    def roll_sum_skip_p(result: PResult):
        return sum(result.roll[1::2])

    assert roll_sum_skip_p(p_3d42d6) == window_sum

    @expandable
    def roll_sum_skip_p_with_selection(result: PResult):
        return sum(result.roll)

    assert (
        roll_sum_skip_p_with_selection(PWithSelection(p_3d42d6, (slice(1, None, 2),)))
        == window_sum
    )

    window_sum = H(
        (roll[2] + roll[4], count) for roll, count in p_3d42d6.rolls_with_counts()
    )

    assert window_sum == H(
        (roll[0] + roll[2], count)
        for roll, count in p_3d42d6.rolls_with_counts(slice(2, 6))
    )

    @expandable
    def roll_sum_window_p(result: PResult):
        return result.roll[2] + result.roll[4]

    assert roll_sum_window_p(p_3d42d6) == window_sum

    @expandable
    def roll_sum_window_p_with_selection(result: PResult):
        return result.roll[0] + result.roll[2]

    assert (
        roll_sum_window_p_with_selection(PWithSelection(p_3d42d6, (slice(2, 6),)))
        == window_sum
    )


def test_expandable_equivalence_homogeneous_pool() -> None:
    d4 = H(4)
    d4_6 = 6 @ d4
    p_6d4 = 6 @ P(d4)

    assert H((sum(roll), count) for roll, count in p_6d4.rolls_with_counts()) == d4_6

    @expandable
    def roll_sum(result: PResult):
        return sum(result.roll)

    assert roll_sum(p_6d4) == d4_6

    head_sum = p_6d4.h(0, 1, 2)
    assert (
        H((sum(roll[:3]), count) for roll, count in p_6d4.rolls_with_counts())
        == head_sum
    )
    assert (
        H((sum(roll), count) for roll, count in p_6d4.rolls_with_counts(slice(None, 3)))
        == head_sum
    )

    @expandable
    def roll_sum_head_p(result: PResult):
        return sum(result.roll[:3])

    assert roll_sum_head_p(p_6d4) == head_sum

    @expandable
    def roll_sum_head_p_with_selection(result: PResult):
        return sum(result.roll)

    assert roll_sum_head_p_with_selection(PWithSelection(p_6d4, (0, 1, 2))) == head_sum

    tail_sum = p_6d4.h(-3, -2, -1)
    assert (
        H((sum(roll[-3:]), count) for roll, count in p_6d4.rolls_with_counts())
        == tail_sum
    )
    assert (
        H(
            (sum(roll), count)
            for roll, count in p_6d4.rolls_with_counts(slice(-3, None))
        )
        == tail_sum
    )

    @expandable
    def roll_sum_tail_p(result: PResult):
        return sum(result.roll[-3:])

    assert roll_sum_tail_p(p_6d4) == tail_sum

    @expandable
    def roll_sum_tail_p_with_selection(result: PResult):
        return sum(result.roll)

    assert (
        roll_sum_tail_p_with_selection(PWithSelection(p_6d4, (-3, -2, -1))) == tail_sum
    )

    mid_sum = p_6d4.h(slice(1, -1))
    assert (
        H((sum(roll[1:-1]), count) for roll, count in p_6d4.rolls_with_counts())
        == mid_sum
    )
    assert (
        H((sum(roll), count) for roll, count in p_6d4.rolls_with_counts(slice(1, -1)))
        == mid_sum
    )

    @expandable
    def roll_sum_mid_p(result: PResult):
        return sum(result.roll[1:-1])

    assert roll_sum_mid_p(p_6d4) == mid_sum

    @expandable
    def roll_sum_mid_p_with_selection(result: PResult):
        return sum(result.roll)

    assert (
        roll_sum_mid_p_with_selection(PWithSelection(p_6d4, (slice(1, -1),))) == mid_sum
    )

    skip_sum = p_6d4.h(slice(1, None, 2))
    assert (
        H((sum(roll[1::2]), count) for roll, count in p_6d4.rolls_with_counts())
        == skip_sum
    )
    assert (
        H(
            (sum(roll), count)
            for roll, count in p_6d4.rolls_with_counts(slice(1, None, 2))
        )
        == skip_sum
    )

    @expandable
    def roll_sum_skip_p(result: PResult):
        return sum(result.roll[1::2])

    assert roll_sum_skip_p(p_6d4) == skip_sum

    @expandable
    def roll_sum_skip_p_with_selection(result: PResult):
        return sum(result.roll)

    assert (
        roll_sum_skip_p_with_selection(PWithSelection(p_6d4, (slice(1, None, 2),)))
        == skip_sum
    )

    window_sum = p_6d4.h(2, 4)
    assert (
        H((roll[2] + roll[4], count) for roll, count in p_6d4.rolls_with_counts())
        == window_sum
    )
    assert (
        H(
            (roll[0] + roll[2], count)
            for roll, count in p_6d4.rolls_with_counts(slice(2, 5))
        )
        == window_sum
    )

    @expandable
    def roll_sum_window_p(result: PResult):
        return result.roll[2] + result.roll[4]

    assert roll_sum_window_p(p_6d4) == window_sum

    @expandable
    def roll_sum_window_p_with_selection(result: PResult):
        return result.roll[0] + result.roll[2]

    assert (
        roll_sum_window_p_with_selection(PWithSelection(p_6d4, (slice(2, 5),)))
        == window_sum
    )


def test_n_h_node_h_not_lowest_terms() -> None:
    n = 4
    h = H({1: 2})

    with pytest.raises(ValueError):
        _NHNode(n, h)


def test_n_h_node_n_negative() -> None:
    n = -1
    h = H(6)

    with pytest.raises(ValueError):
        _NHNode(n, h)


def test_n_h_node_outcomes() -> None:
    n = 2
    h = H(3)

    n_h_node = _NHNode(n, h)
    assert list(n_h_node._outcome_k_nodes(Direction.LEAST_TO_GREATEST)) == [
        _KOutcomeNode(
            k=2,
            outcome=1,
            prob=Fraction(1, 9),
            n_remaining=0,
            h_remaining=H({2: 1, 3: 1}),
        ),
        _KOutcomeNode(
            k=1,
            outcome=1,
            prob=Fraction(4, 9),
            n_remaining=1,
            h_remaining=H({2: 1, 3: 1}),
        ),
        _KOutcomeNode(
            k=0,
            outcome=1,
            prob=Fraction(4, 9),
            n_remaining=2,
            h_remaining=H({2: 1, 3: 1}),
        ),
    ]
    assert list(n_h_node._outcome_k_nodes(Direction.GREATEST_TO_LEAST)) == [
        _KOutcomeNode(
            k=2,
            outcome=3,
            prob=Fraction(1, 9),
            n_remaining=0,
            h_remaining=H({1: 1, 2: 1}),
        ),
        _KOutcomeNode(
            k=1,
            outcome=3,
            prob=Fraction(4, 9),
            n_remaining=1,
            h_remaining=H({1: 1, 2: 1}),
        ),
        _KOutcomeNode(
            k=0,
            outcome=3,
            prob=Fraction(4, 9),
            n_remaining=2,
            h_remaining=H({1: 1, 2: 1}),
        ),
    ]


def test_n_h_node_outcomes_lowest_terms() -> None:
    n = 2

    for n_h_node in (
        _NHNode(n, H((1, 2, 2, 3, 3))),
        _NHNode(n, H((1, 1, 2, 2, 3))),
    ):
        for direction in Direction:
            outcome_k_nodes = list(n_h_node._outcome_k_nodes(direction))

            for outcome_k_node in outcome_k_nodes:
                assert (
                    outcome_k_node.h_remaining.lowest_terms()
                    is outcome_k_node.h_remaining
                )


def test_expandable_sentinel_default() -> None:
    default_sentinel = H({0: 1})
    d6 = H(6)

    @expandable
    def func(result: HResult) -> HOrOutcomeT:
        return result.outcome * 2 + func(result.h)

    assert func(d6, limit=0) == default_sentinel
    assert func(d6, limit=1) == d6 * 2 + default_sentinel
    assert func(d6, limit=2) == d6 * 2 + d6 * 2 + default_sentinel


def test_expandable_sentinel_h() -> None:
    sentinel = H({-2: 1})
    d6 = H(6)

    @expandable(sentinel=sentinel)
    def func(result: HResult) -> HOrOutcomeT:
        return result.outcome * func(result.h)

    assert func(d6, limit=0) == sentinel
    assert func(d6, limit=1) == d6 * sentinel
    assert func(d6, limit=2) == d6 * d6 * sentinel


def test_expandable_sentinel_with_recursion_error() -> None:
    d1 = H(1)

    @expandable(sentinel=H({0: 1}))
    def func(result: HResult) -> HOrOutcomeT:
        return func(result.h) + 1

    # Sentinel raises a RecursionError
    assert func(d1, limit=1) == H({1: 1})

    # 50 is meant to capture the depth beyond which func hits its RecursionError. This
    # is probably more like 200-500, depending on the environment.
    assert func(d1, limit=-1).gt(H({50: 1})) == H({True: 1})


def test_expandable_multiple_args_kw() -> None:
    d6 = H(6)
    d8 = H(8)
    d10 = H(10)
    p_2d8 = 2 @ P(d8)

    @expandable
    def func(d6: HResult, p_2d8: PResult, d10: HResult) -> HOrOutcomeT:
        assert d6.outcome in d6

        for d8_outcome in p_2d8.roll:
            assert d8_outcome in d8

        assert d10.outcome in d10

        return d6.outcome + sum(p_2d8.roll) + d10.outcome

    res = d6 + p_2d8 + d10
    assert func(d6, p_2d8, d10) == res
    assert func(d6, p_2d8, d10=d10) == res
    assert func(d6, p_2d8=p_2d8, d10=d10) == res
    assert func(d6=d6, p_2d8=p_2d8, d10=d10) == res


def test_expandable_accommodates_h_with_zero_total() -> None:
    class Result(IntEnum):
        ONES = auto()
        FIVES_OR_SIXES = auto()

    def func(p_result: PResult) -> H:
        c = Counter(p_result.roll)

        return H({Result.ONES: c[1], Result.FIVES_OR_SIXES: c[5] + c[6]})

    assert foreach(func, p_result=4 @ P(6)) == H(
        {Result.ONES: 1, Result.FIVES_OR_SIXES: 2}
    )


def test_explode_single_sided_die_integral_limit() -> None:
    def is_even_predicate(h_result: HResult):
        return h_result.outcome % 2 == 0

    assert explode(H({3: 1}), is_even_predicate, limit=5) == H({3: 1})
    assert explode(H({2: 1}), is_even_predicate, limit=5) == H({12: 1})
    assert explode(H({0: 1}), is_even_predicate, limit=5) == H({0: 1})
    assert explode(H({-2: 1}), is_even_predicate, limit=5) == H({-12: 1})
    assert explode(H({-3: 1}), is_even_predicate, limit=5) == H({-3: 1})
