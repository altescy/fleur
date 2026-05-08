from typing import Final, get_args

from .types import _ColorKeyword

COLOR_KEYWORDS: Final[set[_ColorKeyword]] = set(get_args(_ColorKeyword))
