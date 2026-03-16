# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
# ======================================================================================

from decimal import Decimal
from fractions import Fraction

import pytest

from dyce.types import (
    Integralish,
    IntegralishLike,
    Realish,
    RealishLike,
    as_integralish,
    as_integralish_ratio,
    as_realish,
    is_even,
    is_odd,
)

__all__ = ()


# ---- Tests ---------------------------------------------------------------------------


def test_as_integralish() -> None:
    i: IntegralishLike

    for i in (
        True,
        1,
    ):
        assert isinstance(as_integralish(i), Integralish)

    with pytest.raises(TypeError):
        as_integralish(Decimal(1))  # type: ignore [arg-type]

    with pytest.raises(TypeError):
        as_integralish(Fraction(1, 2))  # type: ignore [arg-type]

    with pytest.raises(TypeError):
        as_realish("asdf")  # type: ignore [arg-type]


def test_as_integralish_numpy() -> None:
    np = pytest.importorskip("numpy", reason="requires numpy")
    i: IntegralishLike

    for i in (
        np.bool(1),
        np.int64(1),
    ):
        assert isinstance(as_integralish(i), Integralish)

    with pytest.raises(TypeError):
        as_integralish(np.float64(1))


def test_as_integralish_sympy() -> None:
    sympy = pytest.importorskip("sympy", reason="requires sympy")
    i: IntegralishLike

    for i in (sympy.Integer(1),):
        assert isinstance(as_integralish(i), Integralish)

    with pytest.raises(TypeError):
        as_integralish(sympy.Rational(1, 2))

    with pytest.raises(TypeError):
        as_integralish(sympy.Float(1))


def test_as_integralish_ratio() -> None:
    assert as_integralish_ratio(2) == (2, 1)
    assert as_integralish_ratio(2.0) == (2, 1)
    assert as_integralish_ratio(Decimal("2.0")) == (2, 1)

    with pytest.raises(TypeError):
        as_integralish_ratio("asdf")  # type: ignore [arg-type]


def test_as_integralish_ratio_numpy() -> None:
    np = pytest.importorskip("numpy", reason="requires numpy")
    assert as_integralish_ratio(np.int64(2)) == (2, 1)
    assert as_integralish_ratio(np.float64(2)) == (2, 1)

    with pytest.raises(TypeError):
        as_integralish_ratio(np.bool(True))


def test_as_integralish_ratio_sympy() -> None:
    sympy = pytest.importorskip("sympy", reason="requires sympy")
    assert as_integralish_ratio(sympy.Integer(2)) == (2, 1)
    assert as_integralish_ratio(sympy.Rational(22, 7)) == (22, 7)

    with pytest.raises(TypeError):
        as_integralish_ratio(sympy.Float(2))


def test_as_realish() -> None:
    i: RealishLike

    for i in (
        True,
        1,
        Decimal(1),
        Fraction(1),
    ):
        assert isinstance(as_realish(i), Realish)

    with pytest.raises(TypeError):
        as_realish("asdf")  # type: ignore [arg-type]


def test_as_realish_numpy() -> None:
    np = pytest.importorskip("numpy", reason="requires numpy")
    i: RealishLike

    for i in (
        np.bool(1),
        np.float64(1),
        np.int64(1),
    ):
        assert isinstance(as_realish(i), Realish)


def test_as_realish_sympy() -> None:
    sympy = pytest.importorskip("sympy", reason="requires sympy")
    i: RealishLike

    for i in (
        sympy.Rational(1, 2),
        sympy.Float(1),
    ):
        assert isinstance(as_realish(i), Realish)


def test_is_even() -> None:
    assert is_even(0)
    assert not is_even(1)


def test_is_even_numpy() -> None:
    np = pytest.importorskip("numpy", reason="requires numpy")
    assert is_even(np.int64(0))
    assert not is_even(np.int64(1))


def test_is_even_sympy() -> None:
    sympy = pytest.importorskip("sympy", reason="requires sympy")
    assert is_even(sympy.sympify(0))
    assert not is_even(sympy.sympify(1))


def test_is_odd() -> None:
    assert is_odd(1)
    assert not is_odd(0)


def test_is_odd_numpy() -> None:
    np = pytest.importorskip("numpy", reason="requires numpy")
    assert is_odd(np.int64(1))
    assert not is_odd(np.int64(0))


def test_is_odd_sympy() -> None:
    sympy = pytest.importorskip("sympy", reason="requires sympy")
    assert is_odd(sympy.sympify(1))
    assert not is_odd(sympy.sympify(0))
