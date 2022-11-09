"""Module exporting the ``ChainIt`` class. This module should no be imported directly, use
``from chainter import ChainIt`` instead."""
import functools as ftools
import itertools as itools
import typing as t
from itertools import chain as ichain

T = t.TypeVar("T")
U = t.TypeVar("U")
# Reserved for Output types
O = t.TypeVar("O")


class ChainIt(t.Generic[T]):
    """Util class allowing to chain transformation methods on an ``Iterable``.

    Methods are applied lazily until the ``ChainIt`` instance is consumed.
    """

    __slots__ = ("_iter",)

    def __init__(self, iterable: t.Iterable[T]) -> None:
        self._iter: t.Generator[T, None, None] = (x for x in iterable)

    def __iter__(self) -> "ChainIt[T]":
        return self

    def __next__(self) -> T:
        return next(self._iter)

    def collect(self) -> t.Tuple[T, ...]:
        """Consumes the iterable and returns it as a tuple.

        >>> ChainIt(range(3)).collect()
        (0, 1, 2)
        """
        return tuple(self._iter)

    def collect_frozenset(self) -> t.FrozenSet[T]:
        """Consumes the iterable and returns it as a set.

        >>> ChainIt(range(3)).collect_frozenset()
        frozenset({0, 1, 2})
        """
        return frozenset(self._iter)

    def collect_list(self) -> t.List[T]:
        """Consumes the iterable and returns it as a list.

        >>> ChainIt(range(3)).collect_list()
        [0, 1, 2]
        """
        return list(self._iter)

    def collect_set(self) -> t.Set[T]:
        """Consumes the iterable and returns it as a set.

        >>> ChainIt(range(3)).collect_set()
        {0, 1, 2}
        """
        return set(self._iter)

    def collect_with(self, fn: t.Callable[[t.Iterable[T]], O]) -> O:
        """Consumes the iterable by applying the function passed as a parameter to it.

        >>> ChainIt("abcd").map(lambda x: x.upper()).collect_with(".".join)
        'A.B.C.D'
        """
        return fn(self)

    def enumerate(self) -> "ChainIt[t.Tuple[int, T]]":
        """Returns a ``ChainIt`` of tuples in the format returned by the ``enumerate`` built-in.

        >>> ChainIt("abc").enumerate().collect()
        ((0, 'a'), (1, 'b'), (2, 'c'))
        """
        return ChainIt(enumerate(self))

    def filter(self, fn: t.Callable[[T], bool]) -> "ChainIt[T]":
        """Returns a ``ChainIt`` of elements filtered by the predicate passed as parameter.

        >>> (
        ...     ChainIt("abcd")
        ...         .enumerate()
        ...         .filter(lambda t: t[0] % 2 == 0)
        ...         .map(lambda t: t[1])
        ...         .collect()
        ... )
        ('a', 'c')
        """
        return ChainIt(filter(fn, self._iter))

    def filter_map(self, fn: t.Callable[[T], t.Union[O, None]]) -> "ChainIt[O]":
        """Work like ``map`` , but filters out elements for which ``fn`` returns ``None``.

        >>> d = {1: "one", 2: "two", 4: "four"}
        >>> ChainIt(range(5)).filter_map(lambda x: d.get(x)).collect()
        ('one', 'two', 'four')
        """
        return ChainIt(result for elem in self._iter if (result := fn(elem)) is not None)

    def find(self, fn: t.Callable[[T], bool]) -> t.Optional[T]:
        """Returns the first elements for which ``fn`` returns true, or ``None`` otherwise.

        >>> ChainIt(range(5)).find(lambda x: x > 3)
        4

        >>> ChainIt(range(5)).find(lambda x: x < 0)
        """
        for elem in self._iter:
            if fn(elem):
                return elem

        return None

    def flat_map(self, fn: t.Callable[[T], t.Iterable[O]]) -> "ChainIt[O]":
        """Works like ``map``, but flattens nested structures.

        >>> ChainIt(("hello ", "world")).flat_map(str.upper).collect_with("".join)
        'HELLO WORLD'
        """
        return ChainIt(ichain.from_iterable(map(fn, self._iter)))

    def fold(self, fn: t.Callable[[O, T], O], initializer: O) -> O:
        """Same as reduce, but passez an initialzing element

        >>> ChainIt(range(4)).fold(lambda x, y: x + y, 10)
        16
        """
        return ftools.reduce(fn, self._iter, initializer)

    def map(self, fn: t.Callable[[T], O]) -> "ChainIt[O]":
        """Returns a ``ChainIt`` of elements with ``fn`` applied to them.

        >>> ChainIt("abc").map(str.upper).collect()
        ('A', 'B', 'C')
        """
        return ChainIt(map(fn, self._iter))

    def nth(self, n: int) -> t.Union[T, None]:
        """Returns the nth element of the iterable, if available. Indexes start at 0.

        >>> ChainIt("abc").nth(2)
        'c'

        >>> ChainIt("abc").nth(3)
        """
        if n < 0:
            return None
        # internal iteration is faster
        for idx, elem in enumerate(self._iter):
            if idx == n:
                return elem

        return None

    def reduce(self, fn: t.Callable[[T, T], T]) -> T:
        """Reduces the iterable to a single element, by repeatedly applying ``fn``.

        >>> ChainIt(range(4)).reduce(lambda x, y: x + y)
        6
        """
        return ftools.reduce(fn, self._iter)

    def take(self, n: int) -> "ChainIt[T]":
        """Returns a ``ChainIt`` yielding n elements of the current iterable.

        >>> ChainIt(range(10)).take(3).collect()
        (0, 1, 2)
        """
        return ChainIt(itools.islice(self._iter, n))

    def take_while(self, fn: t.Callable[[T], bool]) -> "ChainIt[T]":
        """Returns a ``ChainIt`` yielding elements while the passed predicate is true.

        >>> def inf():
        ...     x = 1
        ...     while True:
        ...         yield x
        ...         x *= 2

        >>> ChainIt(inf()).take_while(lambda x: x < 10).collect()
        (1, 2, 4, 8)
        """
        return ChainIt(itools.takewhile(fn, self._iter))

    def zip(self, other: t.Iterable[U]) -> "ChainIt[t.Tuple[T, U]]":
        """Zips up two iterators into a single ChainIt of pairs. Stops when the shortest
        iterable has been traversed.

        >>> ChainIt(range(5)).zip(range(3, 0, -1)).collect()
        ((0, 3), (1, 2), (2, 1))
        """
        return ChainIt(zip(iter(self), other))

    def zip_longest(self, other: t.Iterable[U]) -> "ChainIt[t.Tuple[T, U]]":
        """Same as ``zip``, but stops when the longest of both iterables has been traversed.

        >>> ChainIt(range(5)).zip_longest(range(3, 0, -1)).collect()
        ((0, 3), (1, 2), (2, 1), (3, None), (4, None))
        """
        return ChainIt(itools.zip_longest(iter(self), other))
