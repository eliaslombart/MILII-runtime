from typing import Any, Iterable, Callable, Protocol, runtime_checkable

@runtime_checkable
class StackInterface(Protocol):
    """
    An interface for custom `Stack` classes. Note that the class does not have to be stack-based.
    All that is required is a `.push` method, which takes a value as an argument.
    """
    def push(self, value: Any) -> None:
        ...


class Stack(StackInterface):
    """
    A Stack class.

    If multiple items are returned through popn and popall, they are returned as a list, where the first element was the lowest item.

    Pushall pushes the first element of the iterable first, so the first element is the bottommost element.
    If a type `None` is pushed, it is ignored instead.
    """

    class StackError(Exception):
        """Error class used by `Stack` for stack-specific problems."""

        def __init__(self, msg) -> None:
            super().__init__(msg)

    def __init__(self, *, data: Iterable = None) -> None:
        """create a new `Stack` class, type of `data` is a iterable"""
        self._stack = []

        if not (data is None):
            try:
                iter(data)
            except TypeError:
                raise TypeError(f"`data` should be iterable, not {type(data)}.")

            for v in data:
                self.push(v)

    def peek(self) -> Any:
        """return the top element of the stack"""
        if len(self._stack) == 0:
            raise self.StackError("cannot peek when Stack is empty.")

        return self._stack[-1]

    def pop(self) -> Any:
        """pops and returns the top of the stack"""
        if len(self._stack) == 0:
            raise self.StackError("cannot pop as Stack is empty.")

        return self._stack.pop(-1)

    def popn(self, number: int) -> tuple[Any, ...]:
        """pops and returns the top `n` items of the stack"""
        if not isinstance(number, int):
            raise self.StackError(f"`n` should be an integer, not {type(number)}")

        if number < 0:
            raise self.StackError(f"Cannot pop a negative number from a stack. Was given: {number}.")

        if len(self._stack) < number:
            raise self.StackError(f"Cannot pop {number} items from a stack with {len(self._stack)} items.")

        return tuple(
            self._stack.pop(-1)
            for _ in range(number)
        )[::-1]

    def popall(self) -> tuple[Any, ...]:
        """pops and returns all the items of the stack"""
        return self.popn(
            len(self._stack)
        )

    def push(self, v: Any) -> None:
        """pushes the value `v` onto the stack"""
        if not (v is None):
            self._stack.append(v)

    def pushall(self, v: Iterable[Any]) -> None:
        """pushes the values `v` onto the stack, `v` should be iterable"""
        for e in v:
            self.push(e)

    def __str__(self) -> str:
        return f"<bottom {self._stack} top>"

    def __repr__(self) -> str:
        return f"Stack(data={self._stack!r})"

class InterpreterRuntimeError(Exception):
    """
    Custom Exception class, used when a error occurs during interpretation.
    """

    def __init__(self, msg: str) -> None:
        super().__init__(msg)

_builtins = {}
_sigils = {}

def builtin(function: Callable = None, *, name: str = None) -> Callable:
    """
    Adds the callable `func` to the list of builtin functions. These are called when a executable sigilblock matches the name of one the callables. A function accepts one argument: the stack.
    Functions can return a value if they wish. If using the provided `Stack` class, `None` will be ignored
    The optional `name` parameter should be a string. It can overwrite `func.__name__`, or add that functionality
    completely.
    Can be used as a decorator, or just as a function:
    @builtin
    def func(data):...

    @builtin(name="+")
    def add(data):...

    lancallable(print, name="echo")
    """

    def decorator(f: Callable) -> Callable:
        fname = name or f.__name__

        if not isinstance(fname, str):
            raise TypeError(f"A renamed @builtin function name must be a String, not a {type(fname)}.")

        if fname in _builtins:
            raise NameError(f"`{fname}` is already in use in @builtin.")

        if not callable(f):
            raise TypeError(f"`func` must be callable, not {type(f)}.")

        _builtins[fname] = f
        return f

    if function is not None:
        return decorator(function)

    return decorator


def sigil(parser: Callable = None, *, sigil: str, executable: bool = False) -> Callable:
    """
    Adds the sigilparser `parser` to the list of parsers. `parser` should be a callable.
    These parsers are called when the corresponding `sigil` is encountered in the code.
    The parser accepts a str, that starts at the sigil, for example:
    code = "Hello World!" .print 
    When the sigil '"' is encountered, the 'stringparser' is called with: <"Hello World!" .print >
    But when after that the sigil "." is encountered, its corresponding parser is called with <.print >

    The parser Should return a tuple: (value, index), where `value` is the value that is pushed to the stack.
    `index` is the relative index that corresponds to the last character that the parser consumes.

    `sigil` should be a string of length 1, that denotes the start of the block that should be parsed.
    The ending/closing character is handled by the sigilparser.

    `executable` is used to denote wether the returned `value` from the parser should be executed (or attempted to be).
    The <.print > from earlier could be an example of when you would use it. To enable, set it to True.
    If `executable` (remains) False, the returned `value` is instead pushed to the stack.

    `langsigil` can be used as both a decorator and a function:
    # simple integer parser.
    sigil(
       simpleparser(end=" ", cast=int),
       sigil="~"
    )

    @sigil(sigil="\"")
    def stringparser(code):...
    """

    def decorator(p: Callable) -> Callable:
        if not isinstance(sigil, str):
            raise TypeError(f"`sigil` must be a string of length 1, not a {type(sigil)}.")

        if len(sigil) != 1:
            raise ValueError(f"`sigil` must be a string of length 1, not {len(sigil)}.")

        if not callable(p):
            raise TypeError(f"`parser` must be callable or a function, not {type(p)}.")

        if sigil in _sigils:
            raise NameError(f"`{sigil}` is already in use as a sigil.")

        _sigils[sigil] = (p, executable)

        return p

    if parser is not None:
        return decorator(parser)

    return decorator


def isbuiltin(function: str) -> bool:
    """
    Returns wether the given function name is known to be executable.
    """
    return function in _builtins


def simpleparser(*, end: str, cast: Callable = lambda x: x) -> Callable[str, tuple[Any, int]]:
    """
    Very simple iterface for making a parser that ends at a character `end`.
    `cast` can be used to transform the resulting string into something usable.

    Example:
    # simple integer parser.
    langsigil(
       simpleparser(end=" ", cast=int),
       sigil="~"
    )
    """

    if not isinstance(end, str):
        raise TypeError(f"`end` must be a string of length 1, not {type(end)}")

    if len(end) != 1:
        raise ValueError(f"`end` must be of length 1, not {len(end)}")

    if not callable(cast):
        raise TypeError(f"`cast` must be a function/callable, not {type(cast)}.")

    def parser(code: str) -> tuple[Any, int]:
        index = 1
        buff = ""
        while index < len(code) and code[index] != end:
            buff += code[index]
            index += 1
        return cast(buff), index

    return parser


def _getbuiltin(f: str) -> Callable:
    if not isbuiltin(f):
        raise InterpreterRuntimeError(f"`{f}` is not a recognized builtin function.")

    return _builtins[f]


def run(code: str, *, stack: StackInterface = None) -> StackInterface:
    """
    `code` is the code that should be interpreted. It should be a String.
    `stack` is the stackobject that should be used. It should support `stack.push(<value>)`.
    If `stack` is omitted, a new stack will be created.

    For more info how the code is interpreted, see README.md.
    """

    if not isinstance(code, str):
        raise TypeError(f"`code` should be a string, not {code}.")

    if stack is None:
        stack = Stack()

    if not isinstance(stack, StackInterface):
        raise AttributeError(f"`stack` must be an instance of `StackInterface`, not {type(stack)}.")

    index = 0

    while index < len(code):

        # if the current character is a known sigil
        if code[index] in _sigils:

            # get the corresponding parser of the sigil and wether its result should be taken as
            # a function call
            parser, executable = _sigils[code[index]]

            # parse. v is the result, and i how many chars have been read/handled/should be skipped
            parser_res, index_offset = parser(code[index:])

            if not isinstance(index_offset, int):
                raise InterpreterRuntimeError(
                    f"Parser returned ({type(parser_res)}, {type(index_offset)}), expected: (Any, int).")

            index += index_offset

            if index < -1:
                raise InterpreterRuntimeError(
                    f"Parser returned {index_offset} as its index-offset, which caused the file pointer to be {index}, which is an illigal state.")

            if executable:
                # if the result should be executed, do so
                # by getting the corresponding function (if it exists)
                # and calling it with the stack
                stack.push(
                    _getbuiltin(parser_res)(stack)
                )
            else:
                # otherwise push it to the stack
                stack.push(parser_res)

        index += 1

    return stack
