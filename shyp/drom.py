"""
Dromedaries!
"""


from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, List, TypeVar, cast


A = TypeVar("A", contravariant=True)
R = TypeVar("R", covariant=True)
newA = TypeVar("newA", contravariant=True)
newR = TypeVar("newR", covariant=True)

C = TypeVar("C", bound=Callable[..., object])


def deferrent(method: C) -> C:
    """
    Allows one to override Python's default `>>` operator resolution by forcing it to
    use the right operand's reversed-direction implementation even if the left operand
    has a direct-direction implementation already

    The way it's used in this module is that it marks the `chainl` method of `BaseDrom`
    or a `BaseDrom` subclass as _deferring_ to the `chainr` method of the `right` other
    when chaining, if the latter is defined

    Does this by adding a `._deferrent` metadata attribute to the function, which the
    implementation of `__rshift__` provided by `BaseDrom` will check for

    You can mark `chainr` as deferrent too. If both the left class's `chainl` is
    deferrent as well as the right class's `chainr`, we revert to Python's normal
    operator resolution (stick to the left class's `chainl`)

    `BaseDrom`'s `chainl` method is marked as `@deferrent`, so anytime you implement
    `chainr` on its subclass, it'll override `BaseDrom`'s `chainl`. For example,
    `Caravan` implements `chainr`, so the following:

    ```
    my_base_drom >> my_caravan
    ```

    will evaluate to `my_caravan.chainr(my_base_drom)` and not
    `my_base_drom.chainl(my_caravan)`.
    """

    setattr(method, "_deferrent", True)
    return method


def is_deferrent(method: Callable[..., object]) -> bool:
    """
    Checks whether `@deferrent` was set (wraps the unsafe `hasattr` stuff)
    """
    return hasattr(method, "_deferrent") and getattr(method, "_deferrent")


class BaseDrom(Generic[A, R], ABC):
    """
    Base class for droms, a type of callable which can be chained together with others
    """

    @abstractmethod
    def run(self, arg: A) -> R:
        """
        Execute the command that this drom represents
        """
        ...

    @deferrent
    def chainl(self, right: "BaseDrom[R, newR]") -> "Caravan[A, newR]":
        """
        Chain this drom on the left with another drom

        Order: self >> right
        """
        return Caravan(self, [], right)

    @deferrent
    def chainr(self, left: "BaseDrom[newA, A]") -> "Caravan[newA, R]":
        """
        Chain this drom on the right with another drom

        Order: left >> self
        """
        return Caravan(left, [], self)

    def __ror__(self, lother: A) -> R:
        return self.run(lother)

    def __call__(self, arg: A) -> R:
        return self.run(arg)

    def __rshift__(self, other: "BaseDrom[R, newR]") -> "Caravan[A, newR]":

        if is_deferrent(self.chainl) and not is_deferrent(other.chainr):
            return other.chainr(self)
        else:
            return self.chainl(other)

    def __rrshift__(self, other: "BaseDrom[newA, A]") -> "Caravan[newA, R]":

        return self.chainr(other)


class Caravan(BaseDrom[A, R]):
    """
    A `Drom` composed of a chain of sequentially evaluated sub-`Drom`s
    """

    def __init__(
        self,
        first: BaseDrom[A, Any],
        mids: List[BaseDrom[Any, Any]],
        last: BaseDrom[Any, R],
    ):
        """
        The first and last droms are declared separately for static typing reasons.
        This constructor probably shouldn't be called manually anyway.
        """

        self._alldroms = [first] + mids + [last]
        self._first = first
        self._mids = mids
        self._last = last

    # implementation
    def run(self, arg: A) -> R:

        nextval: Any = arg

        for drom in self.droms:
            nextval = drom.run(nextval)

        return cast(R, nextval)

    # override
    def chainl(self, right: "BaseDrom[R, newR]") -> "Caravan[A, newR]":

        if isinstance(right, Caravan):
            return Caravan(self.first, self.droms[1:] + right.droms[:-1], right.last)
        else:
            return Caravan(self.first, self.droms[1:], right)

    # override
    def chainr(self, left: "BaseDrom[newA, A]") -> "Caravan[newA, R]":

        if isinstance(left, Caravan):
            return Caravan(left.first, left.droms[1:] + self.droms[:-1], self.last)
        else:
            return Caravan(left, self.droms[:-1], self.last)

    @property
    def droms(self) -> List[BaseDrom[Any, Any]]:
        """
        All droms in this caravan
        """
        return self._alldroms

    @property
    def first(self) -> BaseDrom[A, Any]:
        """
        The first drom in this caravan
        """
        return self._first

    @property
    def last(self) -> BaseDrom[Any, R]:
        """
        The last drom in this caravan
        """
        return self._last

    @property
    def mids(self) -> List[BaseDrom[Any, Any]]:
        """
        Every drom in this caravan but the first and last
        """
        return self._mids

    def __len__(self) -> int:
        return len(self._alldroms)


class DynDrom(BaseDrom[A, R]):
    """
    Drom defined dynamically via a function
    """

    def __init__(self, func: Callable[[A], R]):
        self.func = func

    # implementation
    def run(self, arg: A) -> R:
        return self.func(arg)
