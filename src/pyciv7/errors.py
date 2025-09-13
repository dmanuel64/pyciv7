"""
Custom exceptions for `pyciv7`.
"""

from warnings import deprecated


class TranspileError(Exception):
    """
    A Transcrypt transpilation error occurred.
    """


@deprecated('"ModDirSerializationError" is deprecated and unused')
class ModDirSerializationError(Exception):
    """
    The mod directory could not be serialized.
    """


class ModExistsError(Exception):
    """
    The mod already exists.
    """


class TranscryptEnvironmentError(Exception):
    """
    The function can only be used in a Transcrypt environment.
    """


class ModNotFoundError(Exception):
    """
    The mod could not be found.
    """


class ModinfoCompatibilityError(Exception):
    """
    The model is not compatible with Civilization 7's `.modinfo` files.
    """


class JavaScriptCompatibilityError(ModinfoCompatibilityError):
    """
    The provided instance is not a valid `.js` file.
    """


class SQLCompatibilityError(ModinfoCompatibilityError):
    """
    The provided instance is not a valid `.sql` or `.xml` file.
    """


class RelativePathRequired(ModinfoCompatibilityError):
    """
    A relative POSIX path is required.
    """
