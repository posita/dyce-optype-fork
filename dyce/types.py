# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
# ======================================================================================

import re
from abc import abstractmethod
from collections.abc import Callable, Iterable, Iterator, Sequence
from decimal import Decimal
from fractions import Fraction
from operator import __getitem__, __index__
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    overload,
    runtime_checkable,
)

from beartype.typing import SupportsAbs, SupportsFloat, SupportsIndex, SupportsInt
from numerary.bt import beartype

if TYPE_CHECKING:
    # Warning: Deep typing voodoo ahead. See
    # <https://github.com/python/mypy/issues/11614>.
    from abc import ABCMeta as ProtocolMeta
    from typing import Protocol
else:
    from beartype.typing import Protocol

    ProtocolMeta = type(Protocol)

__all__ = ()


# ---- Types ---------------------------------------------------------------------------


_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_GetItemT = SupportsIndex | slice
_UnaryOperatorT = Callable[[_T_co], _T_co]
_BinaryOperatorT = Callable[[_T_co, _T_co], _T_co]
UnaryOperatorT = Callable[[_T_co], _T_co]
BinaryOperatorT = Callable[[_T_co, _T_co], _T_co]
Numberish = Union["RealishLike", "Realish"]


def _assert_isinstance(*num_ts: type, target_t: type) -> None:
    assert issubclass(target_t.__class__, ProtocolMeta), (
        f"{target_t.__class__} is not subclass of {Protocol}"
    )

    for num_t in num_ts:
        assert isinstance(num_t(1), target_t), f"{num_t!r}, {target_t!r}"


@runtime_checkable
class RealishLike(SupportsAbs[Any], Protocol, metaclass=ProtocolMeta):
    @abstractmethod
    def __float__(self) -> float: ...

    # Complex methods
    @abstractmethod
    def __add__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __radd__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __sub__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rsub__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __mul__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rmul__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __truediv__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rtruediv__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __neg__(self) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __pos__(self) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __pow__(self, exponent: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rpow__(self, exponent: Any, /) -> Any: ...  # noqa: ANN401

    # Real methods
    @abstractmethod
    def __lt__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __le__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __ge__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __gt__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __floordiv__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rfloordiv__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __mod__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rmod__(self, other: Any, /) -> Any: ...  # noqa: ANN401


_assert_isinstance(int, float, bool, Decimal, Fraction, target_t=RealishLike)


@runtime_checkable
class Realish(SupportsAbs["Realish"], SupportsFloat, Protocol, metaclass=ProtocolMeta):
    # Complex methods
    @abstractmethod
    def __add__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __radd__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __sub__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __rsub__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __mul__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __rmul__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __truediv__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __rtruediv__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __neg__(self) -> "Realish": ...
    @abstractmethod
    def __pos__(self) -> "Realish": ...
    @abstractmethod
    def __pow__(self, exponent: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __rpow__(self, exponent: Union["Realish", RealishLike], /) -> "Realish": ...

    # Real methods
    @abstractmethod
    def __lt__(self, other: Union["Realish", RealishLike], /) -> bool: ...
    @abstractmethod
    def __le__(self, other: Union["Realish", RealishLike], /) -> bool: ...
    @abstractmethod
    def __ge__(self, other: Union["Realish", RealishLike], /) -> bool: ...
    @abstractmethod
    def __gt__(self, other: Union["Realish", RealishLike], /) -> bool: ...
    @abstractmethod
    def __floordiv__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __rfloordiv__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __mod__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...
    @abstractmethod
    def __rmod__(self, other: Union["Realish", RealishLike], /) -> "Realish": ...


_assert_isinstance(int, float, bool, Decimal, Fraction, target_t=Realish)


@runtime_checkable
class IntegralishLike(
    SupportsAbs[Any],
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    Protocol,
    metaclass=ProtocolMeta,
):
    # Complex methods
    @abstractmethod
    def __add__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __radd__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __sub__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rsub__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __mul__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rmul__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __truediv__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rtruediv__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __neg__(self) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __pos__(self) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __pow__(self, exponent: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rpow__(self, exponent: Any, /) -> Any: ...  # noqa: ANN401

    # Real methods
    @abstractmethod
    def __lt__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __le__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __ge__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __gt__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __floordiv__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rfloordiv__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __mod__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rmod__(self, other: Any, /) -> Any: ...  # noqa: ANN401

    # Integral methods
    @abstractmethod
    def __lshift__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rlshift__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rshift__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rrshift__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __and__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rand__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __xor__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __rxor__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __or__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __ror__(self, other: Any, /) -> Any: ...  # noqa: ANN401
    @abstractmethod
    def __invert__(self) -> Any: ...  # noqa: ANN401


_assert_isinstance(int, bool, target_t=IntegralishLike)


@runtime_checkable
class Integralish(
    SupportsAbs["Integralish"],
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    Protocol,
    metaclass=ProtocolMeta,
):
    # Complex methods
    @overload
    @abstractmethod
    def __add__(self, other: Realish | RealishLike, /) -> Realish: ...
    @overload
    @abstractmethod
    def __add__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @overload
    @abstractmethod
    def __radd__(self, other: Realish | RealishLike, /) -> Realish: ...
    @overload
    @abstractmethod
    def __radd__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @overload
    @abstractmethod
    def __sub__(self, other: Realish | RealishLike, /) -> Realish: ...
    @overload
    @abstractmethod
    def __sub__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @overload
    @abstractmethod
    def __rsub__(self, other: Realish | RealishLike, /) -> Realish: ...
    @overload
    @abstractmethod
    def __rsub__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @overload
    @abstractmethod
    def __mul__(self, other: Realish | RealishLike, /) -> Realish: ...
    @overload
    @abstractmethod
    def __mul__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @overload
    @abstractmethod
    def __rmul__(self, other: Union[Realish, RealishLike], /) -> Realish: ...
    @overload
    @abstractmethod
    def __rmul__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __truediv__(
        self, other: Union["Integralish", IntegralishLike, Realish, RealishLike], /
    ) -> Realish: ...
    @abstractmethod
    def __rtruediv__(
        self, other: Union["Integralish", IntegralishLike, Realish, RealishLike], /
    ) -> Realish: ...
    @abstractmethod
    def __neg__(self) -> "Integralish": ...
    @abstractmethod
    def __pos__(self) -> "Integralish": ...
    @overload
    @abstractmethod
    def __pow__(self, exponent: Realish | RealishLike, /) -> Realish: ...
    @overload
    @abstractmethod
    def __pow__(
        self, exponent: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @overload
    @abstractmethod
    def __rpow__(self, exponent: Realish | RealishLike, /) -> Realish: ...
    @overload
    @abstractmethod
    def __rpow__(
        self, exponent: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...

    # Real methods
    @abstractmethod
    def __lt__(self, other: Numberish, /) -> bool: ...
    @abstractmethod
    def __le__(self, other: Numberish, /) -> bool: ...
    @abstractmethod
    def __ge__(self, other: Numberish, /) -> bool: ...
    @abstractmethod
    def __gt__(self, other: Numberish, /) -> bool: ...
    @abstractmethod
    def __floordiv__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __rfloordiv__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __mod__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __rmod__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...

    # Integral methods
    @abstractmethod
    def __lshift__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __rlshift__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __rshift__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __rrshift__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __and__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __rand__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __xor__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __rxor__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __or__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __ror__(
        self, other: Union["Integralish", IntegralishLike], /
    ) -> "Integralish": ...
    @abstractmethod
    def __invert__(self) -> "Integralish": ...


_assert_isinstance(int, bool, target_t=Integralish)


# ---- Functions -----------------------------------------------------------------------


@beartype
def as_int(val: SupportsInt) -> int:
    r"""
    Helper function to losslessly coerce *val* into an ``#!python int``. Raises
    ``#!python TypeError`` if that cannot be done.
    """
    int_val = int(val)

    if int_val != val:
        raise TypeError(f"cannot (losslessly) coerce {val} to an int")

    return int_val


def as_integralish(o: IntegralishLike | Integralish) -> Integralish:
    if isinstance(o, Integralish):
        return o
    else:
        raise TypeError  # TODO(posita): add error message


@beartype
def as_integralish_ratio(
    operand: RealishLike | Realish,
) -> tuple[Integralish, Integralish]:
    r"""
    Helper function that extracts the numerator from *operand* including resolving
    non-compliant rational implementations that don't implement ``as_integer_ratio`` or
    implement ``numerator`` as a method rather than a property.

    ``` python
    >>> from dyce.types import as_integralish_ratio
    >>> from fractions import Fraction
    >>> as_integralish_ratio(Fraction(22, 7))
    (22, 7)

    ```
    """
    if hasattr(operand, "as_integer_ratio") and callable(operand.as_integer_ratio):
        return operand.as_integer_ratio()

    numerator: Integralish
    denominator: Integralish

    if hasattr(operand, "numerator") and hasattr(operand, "denominator"):
        if callable(operand.numerator):
            numerator = operand.numerator()
        else:
            numerator = operand.numerator

        if callable(operand.denominator):
            denominator = operand.denominator()
        else:
            denominator = operand.denominator

        return (numerator, denominator)

    raise TypeError(f"{operand!r} ({type(operand)}) is not rational")


def as_realish(o: RealishLike) -> Realish:
    if isinstance(o, Realish):
        return o
    else:
        raise TypeError  # TODO(posita): add error message


@beartype
def getitems(seq: Sequence[_T], keys: Iterable[_GetItemT]) -> Iterator[_T]:
    for key in keys:
        if isinstance(key, slice):
            yield from __getitem__(seq, key)
        else:
            # TODO(posita): See <https://github.com/astral-sh/ty/issues/3037>
            yield __getitem__(seq, __index__(key))  # ty: ignore [no-matching-overload]


@beartype
def is_even(outcome: SupportsInt) -> bool:
    return as_int(outcome) % 2 == 0


@beartype
def is_odd(outcome: SupportsInt) -> bool:
    return as_int(outcome) % 2 != 0


@beartype
def natural_key(val: object) -> tuple[int | str, ...]:
    return tuple(int(s) if s.isdigit() else s for s in re.split(r"(\d+)", str(val)))


@beartype
def sorted_outcomes(vals: Iterable[_T]) -> list[_T]:
    vals = list(vals)

    try:
        vals.sort()
    except TypeError:
        # This is for outcomes that don't support direct comparisons, like symbolic
        # representations
        vals.sort(key=natural_key)

    return vals
