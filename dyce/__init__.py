# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
# ======================================================================================

from .evaluation import *  # noqa: F403
from .h import *  # noqa: F403
from .p import *  # noqa: F403
from .r import *  # noqa: F403
from .types import *  # noqa: F403

__all__ = ()

_VersionT = (
    tuple[int, int, int]
    | tuple[int, int, int, str]
    | tuple[int, int, int, str, str]
    | tuple[int, int, int, str, str, str]
)

__version__: _VersionT
__vers_str__: str

try:
    from ._version import (  # type: ignore [import-not-found, no-redef, unused-ignore] # ty: ignore # ty: ignore [unused-ignore-comment]
        __vers_str__ as __vers_str__,
    )
    from ._version import (  # type: ignore [import-not-found, no-redef, unused-ignore] # ty: ignore # ty: ignore [unused-ignore-comment]
        __version__ as __version__,
    )
except ImportError:
    __version__ = (0, 0, 0, "post0", "unknown", "d00000000")  # ty: ignore [conflicting-declarations]
    __vers_str__ = "0.0.0.post0+unknown.d00000000"  # ty: ignore [conflicting-declarations]
