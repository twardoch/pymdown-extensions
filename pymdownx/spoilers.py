"""Deprecated name for details."""

import warnings

from . import details
from .util import PymdownxDeprecationWarning


def makeExtension(*args, **kwargs):
    """Return extension."""

    warnings.warn(
        "'Spoilers' has been renamed to 'Details'. Please use 'Details' as 'Spoilers' has been deprecated."
        "\n'Spoilers' will be removed in the future in favor of 'Details'\n",
        PymdownxDeprecationWarning,
    )

    return details.DetailsExtension(*args, **kwargs)
