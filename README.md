# shyp

Provides a nice interface for doing everyday sysadmin tasks, especially from the REPL or
other dynamic runtime

Python's highly structured runtime environment and its general expressiveness make it
ideal for everyday systems administration tasks, but unfortunately, that same structure
makes it harder to quickly accomplish everyday tasks. There is more mental friction due
to the need to import different packages, convert between data structures, and store
intermediate variables in function calls.

`shyp` aims to fix some of these problems by leveraging Python's overridable operators
to give you a nice interface reminiscent of Unix piping. A two-stage evaluation system
called "bactries" mimics the Unix-style separation of *options*, passed on the command
line, and *inputs/outputs*, passed through the standard streams.


## Camels

A bactry (named after the two-humped Bactian camel), or bact for short, is, in technical
terms, an order-2 curried function whose second evaluation takes only one value. Its
type would thus be:

```python
Callable[..., Callable[[A], R]]
```

To run a bact, you would have to "call it twice", hence the name:

```python
foo(value1, param2=value2)(bar)
```

The reason why such a construct is useful is that by constraining the input and output
values of the second evaluation, we may "pre-evaluate" a large number of bactries and
then provide utilities for _chaining them_ together:

```python
my_final_value = my_initial_value | foo(value1) >> bar() >> baz(value2, value3) >> qux()
```

The result of only applying the single evaluation is called a dromedary, and chaining
together many dromedaries is a caravan :)

What's the point? The point is to replicate the great advantages of Unix-style command
piping:

1. The notation naturally reflects the flow of data from one command to the next, unlike
   function evaluation, which gets it backwards (blame Euler) and is altogether clunky
2. Configuration of the commands uses a separate notation from the principle input
   (command line flags versus standard streams)

Unfortunately, due to the way Python works, you don't get another of the great
advantages of Unix piping: scalability on large input streams. Maybe a future version
can make use of async/await together with C extensions to get around GIL.

For Unix OSes, all data is exchanged as byte streams exchanged through file descriptors.
This is a great approach for a low-level, unstructured environment such as an operating
system, but it would result in a lot of overhead to pack and unpack data structures for
a pure-Python system, and doesn't leverage the power of the language environment. The
trouble is, if bactries are allowed to return arbitrary objects, you will need to write
extensive wrapper code to get data from one command to the next.


## Conventions

To partially solve this problem, a series of _conventions_ will be provided. This mainly
involves wherever possible using primitives, lists of primitives, or dictionaries of
primitives only, providing convenience classes which provide nicer REPL representations,
and utilities for quickly converting common data types.
