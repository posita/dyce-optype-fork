#!/usr/bin/env python
# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
# ======================================================================================

"""
Enumerate math operator result types for one or two Python types and emit
@typing.overload-decorated stub functions.

With a single TYPE, enumerates unary math operators. With two TYPEs, enumerates
binary math operators. In both cases, sample values are instantiated, operators are
applied at runtime, and the observed result types are used to generate stubs.

Example usage::

    helpers/gen-op-types.py int
    helpers/gen-op-types.py --op __neg__ --op __abs__ float
    helpers/gen-op-types.py int float
    helpers/gen-op-types.py --op __add__ --op __sub__ int fractions.Fraction
    helpers/gen-op-types.py --exclude-op __matmul__ --exclude-op __rmatmul__ decimal.Decimal int
"""

import argparse
import builtins
import importlib
import logging
import sys

__all__ = ()


# ---- Data ----------------------------------------------------------------------------


#: Unary math operator dunder names to enumerate by default.
_DEFAULT_UNARY_OPS = (
    "__neg__",
    "__pos__",
    "__abs__",
    "__invert__",
    "__trunc__",
    "__floor__",
    "__ceil__",
    "__round__",
)

#: Binary math operator dunder names to enumerate by default. Covers the standard
#: numeric protocol operators most likely to appear in type stubs and protocols.
_DEFAULT_BINARY_OPS = (
    "__add__",
    "__radd__",
    "__sub__",
    "__rsub__",
    "__mul__",
    "__rmul__",
    "__truediv__",
    "__rtruediv__",
    "__floordiv__",
    "__rfloordiv__",
    "__mod__",
    "__rmod__",
    "__pow__",
    "__rpow__",
    "__and__",
    "__rand__",
    "__or__",
    "__ror__",
    "__xor__",
    "__rxor__",
    "__lshift__",
    "__rlshift__",
    "__rshift__",
    "__rrshift__",
    "__matmul__",
    "__rmatmul__",
)

PARSER = argparse.ArgumentParser(
    prog="gen-op-types.py",
    description=(
        "Enumerate math operator result types for one or two Python types "
        "and emit @typing.overload-decorated stub functions."
    ),
    epilog=(
        "TYPE arguments are resolved as Python import paths. Built-in types such as "
        '"int" and "float" are looked up directly; dotted paths like '
        '"decimal.Decimal" or "fractions.Fraction" are imported from their respective '
        "modules. The tool instantiates a sample value of each type, applies each "
        "operator, observes the runtime result type, and emits @typing.overload stubs. "
        "Operators that raise TypeError or are not defined on the type are silently "
        "skipped unless --log-level DEBUG is set."
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
PARSER.add_argument(
    "type1",
    metavar="TYPE1",
    help=(
        "operand type (unary mode) or left operand type (binary mode) "
        "as a Python import path "
        '(e.g., "int", "decimal.Decimal")'
    ),
)
PARSER.add_argument(
    "type2",
    metavar="TYPE2",
    nargs="?",
    default=None,
    help=(
        "right operand type as a Python import path; "
        "when provided, binary operators are enumerated instead of unary ones "
        '(e.g., "float", "fractions.Fraction")'
    ),
)
PARSER.add_argument(
    "--op",
    metavar="OP",
    help=(
        "include only operator OP in the enumeration; may be specified multiple times; "
        'OP should be a dunder method name (e.g., "__add__", "__neg__"); '
        f"default: all {len(_DEFAULT_UNARY_OPS)} standard unary operators (single TYPE) "
        f"or all {len(_DEFAULT_BINARY_OPS)} standard binary operators (two TYPEs)"
    ),
    action="append",
    default=[],
    dest="ops",
)
PARSER.add_argument(
    "--exclude-op",
    metavar="OP",
    help=(
        "exclude operator OP from the enumeration; may be specified multiple times; "
        "takes precedence over --op"
    ),
    action="append",
    default=[],
    dest="exclude_ops",
)
PARSER.add_argument(
    "--left-value",
    metavar="EXPR",
    help=(
        "Python expression to evaluate as the TYPE1 sample value; "
        "the simple (unqualified) name of TYPE1 is available as a local; "
        'default: "TYPE1(1)" (i.e., the type called with 1)'
    ),
    default=None,
    dest="left_value_expr",
)
PARSER.add_argument(
    "--right-value",
    metavar="EXPR",
    help=(
        "Python expression to evaluate as the TYPE2 sample value (binary mode only); "
        "the simple (unqualified) name of TYPE2 is available as a local; "
        'default: "TYPE2(1)" (i.e., the type called with 1)'
    ),
    default=None,
    dest="right_value_expr",
)
PARSER.add_argument(
    "--log-level",
    metavar="LEVEL",
    help="set logging verbosity to LEVEL (default: WARNING)",
    choices=["CRITICAL", "DEBUG", "ERROR", "INFO", "WARNING"],
    default="WARNING",
)


# ---- Functions -----------------------------------------------------------------------


def resolve_type(type_path: str) -> type:
    """Resolve a type from a dotted Python import path.

    Built-in names (e.g. ``"int"``, ``"float"``) are looked up in :mod:`builtins`.
    Dotted paths (e.g. ``"decimal.Decimal"``) are split on the last dot and the
    leading portion is imported as a module.
    """
    builtin = getattr(builtins, type_path, None)

    if isinstance(builtin, type):
        return builtin

    if "." in type_path:
        module_name, _, attr_name = type_path.rpartition(".")

        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise SystemExit(f"error: cannot import {module_name!r}: {exc}") from exc

        t = getattr(module, attr_name, None)

        if t is None:
            raise SystemExit(
                f"error: module {module_name!r} has no attribute {attr_name!r}"
            )

        if not isinstance(t, type):
            raise SystemExit(
                f"error: {type_path!r} resolved to {t!r}, which is not a type"
            )

        return t

    raise SystemExit(
        f"error: cannot resolve {type_path!r} as a built-in or dotted import path"
    )


def make_sample(t: type, expr: str | None) -> object:
    """Return a sample instance of *t*.

    If *expr* is ``None``, returns ``t(1)``.  Otherwise evaluates *expr* with
    the unqualified name of *t* bound in the local namespace, e.g. for
    ``decimal.Decimal`` the name ``Decimal`` is available.
    """
    if expr is None:
        return t(1)

    return eval(expr, {t.__name__: t})  # noqa: S307 — intentional developer tool


def format_type(t: type) -> str:
    """Return a fully-qualified annotation string for *t*.

    Built-in types are returned by their bare name (e.g. ``"int"``); all
    others include the module (e.g. ``"decimal.Decimal"``).
    """
    if t.__module__ == "builtins":
        return t.__qualname__

    return f"{t.__module__}.{t.__qualname__}"


def select_ops(
    requested: list[str],
    excluded: list[str],
    default: tuple[str, ...],
) -> list[str]:
    """Return the operator list after applying --op / --exclude-op filters."""
    ops = list(requested) if requested else list(default)
    excluded_set = set(excluded)
    return [op for op in ops if op not in excluded_set]


def find_op(t: type, op: str) -> object | None:
    """Look up *op* in *t*'s MRO, excluding :class:`object`.

    Methods that exist only on :class:`object` (e.g. ``__or__`` added in
    Python 3.10 for PEP 604 union-type syntax) are not meaningful math
    operators and should be treated as absent.
    """
    for base in t.__mro__:
        if base is object:
            continue

        if op in base.__dict__:
            return base.__dict__[op]

    return None


def try_unary(t: type, op: str, val: object) -> type | None:
    """Apply unary *op* to *val* and return the result type, or ``None`` if unsupported."""
    method = find_op(t, op)

    if method is None:
        logging.debug("skipping %s.%s: not defined", t.__name__, op)
        return None

    try:
        result = method(val)
    except Exception as exc:
        logging.debug("skipping %s.%s: %s", t.__name__, op, exc)
        return None

    return type(result)


def try_binary(
    t1: type,
    op: str,
    lval: object,
    rval: object,
) -> type | None:
    """Apply binary *op* as ``t1.op(lval, rval)`` and return the result type.

    Returns ``None`` if the operator is not defined on *t1*, raises an
    exception, or returns :data:`NotImplemented`.
    """
    method = find_op(t1, op)

    if method is None:
        logging.debug("skipping %s.%s: not defined", t1.__name__, op)
        return None

    try:
        result = method(lval, rval)
    except Exception as exc:
        logging.debug("skipping %s.%s: %s", t1.__name__, op, exc)
        return None

    if result is NotImplemented:
        logging.debug("skipping %s.%s: returned NotImplemented", t1.__name__, op)
        return None

    return type(result)


def build_unary_stubs(
    t1: type,
    ops: list[str],
    lval: object,
) -> tuple[list[str], set[str]]:
    """Build ``@typing.overload`` stub lines for unary operators on *t1*.

    Returns a tuple of ``(stub_lines, needed_modules)`` where *needed_modules*
    is the set of non-builtin module names that must be imported.
    """
    stub_lines: list[str] = []
    needed_modules: set[str] = set()
    t1name = format_type(t1)

    if "." in t1name:
        needed_modules.add(t1name.rsplit(".", 1)[0])

    for op in ops:
        result_type = try_unary(t1, op, lval)

        if result_type is None:
            continue

        rname = format_type(result_type)

        if "." in rname:
            needed_modules.add(rname.rsplit(".", 1)[0])

        stub_lines.append("@typing.overload")
        stub_lines.append(f"def {op}(self: {t1name}) -> {rname}: ...")

    return stub_lines, needed_modules


def build_binary_stubs(
    t1: type,
    t2: type,
    ops: list[str],
    lval: object,
    rval: object,
) -> tuple[list[str], set[str]]:
    """Build ``@typing.overload`` stub lines for binary operators on *t1* with *t2*.

    For each operator, calls ``t1.op(lval, rval)`` to observe the result type.
    The resulting stubs describe ``self`` as *t1* and ``other`` as *t2*.

    Returns a tuple of ``(stub_lines, needed_modules)`` where *needed_modules*
    is the set of non-builtin module names that must be imported.
    """
    stub_lines: list[str] = []
    needed_modules: set[str] = set()
    t1name = format_type(t1)
    t2name = format_type(t2)

    for tname in (t1name, t2name):
        if "." in tname:
            needed_modules.add(tname.rsplit(".", 1)[0])

    for op in ops:
        result_type = try_binary(t1, op, lval, rval)

        if result_type is None:
            continue

        rname = format_type(result_type)

        if "." in rname:
            needed_modules.add(rname.rsplit(".", 1)[0])

        stub_lines.append("@typing.overload")
        stub_lines.append(f"def {op}(self: {t1name}, other: {t2name}) -> {rname}: ...")

    return stub_lines, needed_modules


def main(*args: str) -> int:
    parsed_args = PARSER.parse_args(args) if args else PARSER.parse_args()
    logging.getLogger().setLevel(parsed_args.log_level)

    # --- Resolve types ---
    t1 = resolve_type(parsed_args.type1)
    t2 = resolve_type(parsed_args.type2) if parsed_args.type2 is not None else None

    # --- Select operators ---
    default_ops = _DEFAULT_BINARY_OPS if t2 is not None else _DEFAULT_UNARY_OPS
    ops = select_ops(parsed_args.ops, parsed_args.exclude_ops, default_ops)

    # --- Build sample values ---
    try:
        lval = make_sample(t1, parsed_args.left_value_expr)
    except Exception as exc:
        print(
            f"error: failed to create sample value for {parsed_args.type1!r}: {exc}",
            file=sys.stderr,
        )
        return 1

    if t2 is not None:
        try:
            rval = make_sample(t2, parsed_args.right_value_expr)
        except Exception as exc:
            print(
                f"error: failed to create sample value for {parsed_args.type2!r}: {exc}",
                file=sys.stderr,
            )
            return 1

    # --- Generate stubs ---
    if t2 is None:
        stub_lines, needed_modules = build_unary_stubs(t1, ops, lval)
        header = f"# Unary operators: {format_type(t1)}"
    else:
        stub_lines, needed_modules = build_binary_stubs(t1, t2, ops, lval, rval)
        header = f"# Binary operators: {format_type(t1)} (left) \u00d7 {format_type(t2)} (right)"

    # --- Emit output ---
    print("import typing")

    for mod in sorted(needed_modules):
        print(f"import {mod}")

    print()
    print(header)

    for i, line in enumerate(stub_lines):
        # Blank line before each decorator (every other line starting at index 0),
        # except before the very first one.
        if i > 0 and line.startswith("@"):
            print()

        print(line)

    return 0


# ---- Initialization ------------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
