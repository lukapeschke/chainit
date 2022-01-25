# chainit

Documentation available here: https://lukapeschke.github.io/chainit/

This library provides the `ChainIt` class, a wrapper around stdlib's
[itertools](https://docs.python.org/3/library/itertools.html) module, allowing to chain
operations on iterables, resulting in easier-to-read code.

```python
import typing as t

def fib() -> t.Iterable[int]:
    a, b = 0, 1
    while True:
        yield a
        next_ = a + b
        a = b
        b = next_

# Allows to write things like this...
(
    ChainIt(fib())
    .filter(lambda x: x % 2 == 0)
    .map(lambda x: x // 2)
    .flat_map(range)
    .take_while(lambda x: x < 6)
    .collect_list()
)

# ...rather than like this
from itertools import chain as ichain, islice, takewhile

list(
    takewhile(
        lambda x: x < 6,
        ichain.from_iterable(
            map(lambda x: range(x // 2), filter(lambda x: x % 2 == 0, fib()))
        ),
    )
)
```

## Installation

```
pip install chainit
```

## Examples

### Decorator

In addition to `ChainIt`, the library provides a `chainit` decorator. It makes a function returning
an iterable return a `ChainIt` instead:

```python
@chainit
def fac():
    n = 0
    fac = 1
    while True:
        yield fac
        n += 1
        fac *= n

assert fac().enumerate().take(5).collect() == ((0, 1), (1, 1), (2, 2), (3, 6), (4, 24))
```

### Using a `ChainIt` instance as an iterable

```python
assert list(fac().take(3)) == [1, 1, 2]

for idx, x in fac().enumerate():
    if idx > 3:
        break
    print(x)
```
