"""Module exporting the ``ChainIter`` class. This module should no be imported directly, use
``from chainter import ChainIter`` instead."""
import functools as ftools
import itertools as itools
import typing as t
from itertools import chain as ichain

T = t.TypeVar("T")
U = t.TypeVar("U")
# Reserved for Output types
O = t.TypeVar("O")


class ChainIter(t.Generic[T]):
    """Util class allowing to chain transformation methods on an ``Iterable``.

    Methods are applied lazily until the ``ChainIter`` instance is consumed.
    """

    __slots__ = ("_iter",)

    def __init__(self, iterable: t.Iterable[T]) -> None:
        self._iter: t.Generator[T, None, None] = (x for x in iterable)

    def __iter__(self) -> "ChainIter[T]":
        return self

    def __next__(self) -> T:
        return next(self._iter)

    def collect(self) -> t.Tuple[T, ...]:
        """Consumes the iterable and returns it as a tuple.

        >>> ChainIter(range(3)).collect()
        (0, 1, 2)
        """
        return tuple(self._iter)

    def collect_frozenset(self) -> t.FrozenSet[T]:
        """Consumes the iterable and returns it as a set.

        >>> ChainIter(range(3)).collect_frozenset()
        frozenset({0, 1, 2})
        """
        return frozenset(self._iter)

    def collect_list(self) -> t.List[T]:
        """Consumes the iterable and returns it as a list.

        >>> ChainIter(range(3)).collect_list()
        [0, 1, 2]
        """
        return list(self._iter)

    def collect_set(self) -> t.Set[T]:
        """Consumes the iterable and returns it as a set.

        >>> ChainIter(range(3)).collect_set()
        {0, 1, 2}
        """
        return set(self._iter)

    def collect_with(self, fn: t.Callable[[t.Iterable[T]], O]) -> O:
        """Consumes the iterable by applying the function passed as a parameter to it.

        >>> ChainIter("abcd").map(lambda x: x.upper()).collect_with(".".join)
        'A.B.C.D'
        """
        return fn(self)

    def enumerate(self) -> "ChainIter[t.Tuple[int, T]]":
        """Returns a ``ChainIter`` of tuples in the format returned by the ``enumerate`` built-in.

        >>> ChainIter("abc").enumerate().collect()
        ((0, 'a'), (1, 'b'), (2, 'c'))
        """
        return ChainIter(enumerate(self))

    def filter(self, fn: t.Callable[[T], bool]) -> "ChainIter[T]":
        """Returns a ``ChainIter`` of elements filtered by the predicate passed as parameter.

        >>> (
        ...     ChainIter("abcd")
        ...         .enumerate()
        ...         .filter(lambda t: t[0] % 2 == 0)
        ...         .map(lambda t: t[1])
        ...         .collect()
        ... )
        ('a', 'c')
        """
        return ChainIter(filter(fn, self._iter))

    def filter_map(
        self, fn: t.Callable[[T], t.Union[O, None]]
    ) -> "ChainIter[O]":
        """Work like ``map`` , but filters out elements for which ``fn`` returns ``None``.

        >>> d = {1: "one", 2: "two", 4: "four"}
        >>> ChainIter(range(5)).filter_map(lambda x: d.get(x)).collect()
        ('one', 'two', 'four')
        """
        return ChainIter(
            result for elem in self._iter if (result := fn(elem)) is not None
        )

    def find(self, fn: t.Callable[[T], bool]) -> t.Optional[T]:
        """Returns the first elements for which ``fn`` returns true, or ``None`` otherwise.

        >>> ChainIter(range(5)).find(lambda x: x > 3)
        4

        >>> ChainIter(range(5)).find(lambda x: x < 0)
        """
        for elem in self._iter:
            if fn(elem):
                return elem

        return None

    def flat_map(self, fn: t.Callable[[T], t.Iterable[O]]) -> "ChainIter[O]":
        """Works like ``map``, but flattens nested structures.

        >>> ChainIter(("hello ", "world")).flat_map(str.upper).collect_with("".join)
        'HELLO WORLD'
        """
        return ChainIter(ichain.from_iterable(map(fn, self._iter)))

    def fold(self, fn: t.Callable[[O, T], O], initializer: O) -> O:
        """Same as reduce, but passez an initialzing element

        >>> ChainIter(range(4)).fold(lambda x, y: x + y, 10)
        16
        """
        return ftools.reduce(fn, self._iter, initializer)

    def map(self, fn: t.Callable[[T], O]) -> "ChainIter[O]":
        """Returns a ``ChainIter`` of elements with ``fn`` applied to them.

        >>> ChainIter("abc").map(str.upper).collect()
        ('A', 'B', 'C')
        """
        return ChainIter(map(fn, self._iter))

    def nth(self, n: int) -> t.Union[T, None]:
        """Returns the nth element of the iterable, if available. Indexes start at 0.

        >>> ChainIter("abc").nth(2)
        'c'

        >>> ChainIter("abc").nth(3)
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

        >>> ChainIter(range(4)).reduce(lambda x, y: x + y)
        6
        """
        return ftools.reduce(fn, self._iter)

    def take(self, n: int) -> "ChainIter[T]":
        """Returns a ``ChainIter`` yielding n elements of the current iterable.

        >>> ChainIter(range(10)).take(3).collect()
        (0, 1, 2)
        """
        return ChainIter(itools.islice(self._iter, n))

    def take_while(self, fn: t.Callable[[T], bool]) -> "ChainIter[T]":
        """Returns a ``ChainIter`` yielding elements while the passed predicate is true.

        >>> def inf():
        ...     x = 1
        ...     while True:
        ...         yield x
        ...         x *= 2

        >>> ChainIter(inf()).take_while(lambda x: x < 10).collect()
        (1, 2, 4, 8)
        """
        return ChainIter(itools.takewhile(fn, self._iter))

    def zip(self, other: t.Iterable[U]) -> "ChainIter[t.Tuple[T, U]]":
        """Zips up two iterators into a single ChainIter of pairs. Stops when the shortest
        iterable has been traversed.

        >>> ChainIter(range(5)).zip(range(3, 0, -1)).collect()
        ((0, 3), (1, 2), (2, 1))
        """
        return ChainIter(zip(self.__iter__(), other))

    def zip_longest(self, other: t.Iterable[U]) -> "ChainIter[t.Tuple[T, U]]":
        """Same as ``zip``, but stops when the longest of both iterables has been traversed.

        >>> ChainIter(range(5)).zip_longest(range(3, 0, -1)).collect()
        ((0, 3), (1, 2), (2, 1), (3, None), (4, None))
        """
        return ChainIter(itools.zip_longest(self.__iter__(), other))
