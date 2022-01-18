"""Module exporting the ``chainiter`` decorator. This module should no be imported directly, use
``from chainter import chainter`` instead."""
import functools as ftools
import typing as t

from .klass import ChainIter

T = t.TypeVar("T")


def chainiter(fn: t.Callable[..., t.Iterable[T]]) -> t.Callable[..., ChainIter[T]]:
    """Utility decorator allowing to make a function returning an Iterable return a ChainIter.

    >>> @chainiter
    ... def hello_gen():
    ...     for c in "HeLlO":
    ...         yield c

    >>> hello_gen().filter(lambda c: c.isupper()).collect_with("".join)
    'HLO'
    """

    @ftools.wraps(fn)
    def wrapper(*args: t.Any, **kwargs: t.Any) -> ChainIter[T]:
        return ChainIter(fn(*args, **kwargs))

    return wrapper
