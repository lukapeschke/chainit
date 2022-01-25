"""
Module exporting the ``chainit`` decorator. This module should no be imported
directly, use ``from chainit import chainit`` instead."""
import functools as ftools
import typing as t

from .klass import ChainIt

T = t.TypeVar("T")


def chainit(fn: t.Callable[..., t.Iterable[T]]) -> t.Callable[..., ChainIt[T]]:
    """Utility decorator allowing to make a function returning an Iterable return a ChainIt.

    >>> @chainit
    ... def hello_gen():
    ...     for c in "HeLlO":
    ...         yield c

    >>> hello_gen().filter(lambda c: c.isupper()).collect_with("".join)
    'HLO'
    """

    @ftools.wraps(fn)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> ChainIt[T]:
        return ChainIt(fn(*args, **kwargs))

    return wrapper
