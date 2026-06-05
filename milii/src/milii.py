from typing import Any, Iterable, Callable, Protocol, runtime_checkable

@runtime_checkable
class DataInterface(Protocol):
    """    Protocol for objects that can receive values via `.push()`."""
    def push(self, value: Any) -> None:
        ...

class Stack(DataInterface):
    """
    A Stack class.

    If multiple items are returned through popn and pop_all, they are returned as a list, where the first element was the lowest item.

    `push_all` pushes the first element of the iterable first, so the first element is the bottommost element.
    """

    class StackError(Exception):
        """Error class used by `Stack` for stack-specific problems."""

        def __init__(self, msg) -> None:
            super().__init__(msg)

    def __init__(self, *, data: Iterable[Any] | None = None) -> None:
        """Create a new Stack. `data`, if provided, must be iterable."""
        self._stack = []

        if data is not None:
            if not isinstance(data, Iterable):
                raise TypeError(f"`data` should be Iterable, not {type(data).__name__}.")

            for v in data:
                self.push(v)

    def peek(self) -> Any:
        """return the top element of the stack"""
        if len(self._stack) == 0:
            raise ValueError("cannot peek when Stack is empty.")

        return self._stack[-1]

    def pop(self) -> Any:
        """pops and returns the top of the stack"""
        if len(self._stack) == 0:
            raise self.StackError("cannot pop as Stack is empty.")

        return self._stack.pop(-1)

    def popn(self, number: int) -> tuple[Any, ...]:
        """pops and returns the top `number` items of the stack, in bottom-to-top order"""
        if not isinstance(number, int):
            raise TypeError(f"`number` should be int, not {type(number).__name__}")

        if number < 0:
            raise ValueError(f"cannot pop a negative number of items from a stack. Was given: {number}.")

        if len(self._stack) < number:
            raise self.StackError(f"cannot pop {number} items from a stack with {len(self._stack)} items.")

        return tuple(
            self._stack.pop(-1)
            for _ in range(number)
        )[::-1]

    def pop_all(self) -> tuple[Any, ...]:
        """pops and returns all the items of the stack, in bottom-to-top order"""
        return self.popn(
            len(self._stack)
        )

    def push(self, value: Any) -> None:
        """pushes `value` onto the stack"""
        self._stack.append(value)

    def push_all(self, values: Iterable[Any]) -> None:
        """pushes `values` onto the stack, `values` should be iterable"""
        for v in values:
            self.push(v)

    def __str__(self) -> str:
        return f"<bottom {self._stack} top>"

    def __repr__(self) -> str:
        return f"Stack(data={self._stack!r})"

class InterpreterRuntimeError(Exception):
    """
    Custom Exception class, used when an error occurs during interpretation.
    """

    def __init__(self, msg: str) -> None:
        super().__init__(msg)

_builtins: dict[str, Callable]              = {}
_sigils:   dict[str, tuple[Callable, bool]] = {}

def builtin(function: Callable | None = None, *, name: str | None = None) -> Callable[..., Any] | Callable[..., Callable[..., Any]]:
    """
    Register a callable as a builtin function. These are called when an executable sigil's value matches the name of one the callables.
    A function accepts one argument: the data-structure (by default a stack).
    Functions can return a value if they wish. `None` will be ignored, and should be pushed/added manually.
    The optional `name` parameter should be a string. It can overwrite `func.__name__`, or add that functionality
    completely.
    Can be used as a decorator, or just as a function:
    @builtin
    def func(data):...

    @builtin(name="+")
    def add(data):...

    builtin(print, name="echo")
    """

    def decorator(f: Callable[[DataInterface], Any]) -> Callable[[DataInterface], Any]:
        fname = name or f.__name__

        if not isinstance(fname, str):
            raise TypeError(f"A renamed @builtin function name must be a string, not a {type(fname).__name__}.")

        if fname in _builtins:
            raise NameError(f"`{fname}` is already in use in @builtin.")

        if not callable(f):
            raise TypeError(f"`func` must be callable, not {type(f).__name__}.")

        _builtins[fname] = f
        return f

    if function is not None:
        return decorator(function)

    return decorator

def sigil(parser: Callable | None = None, *, sigil: str, executable: bool = False) -> Callable[..., Any] | Callable[..., Callable[..., Any]]:
    """
    Register a parser for a sigil character. `parser` should be a callable.
    These parsers are called when the corresponding `sigil` is encountered in the code.
    The parser accepts a str, that starts at the sigil, for example:
    code = "Hello World!" .print 
    When the sigil '"' is encountered, the 'stringparser' is called with: <"Hello World!" .print >
    But when after that the sigil "." is encountered, its corresponding parser is called with <.print >

    The parser Should return a tuple: (value, index), where `value` is the value that is pushed to the stack.
    `index` is the relative index that corresponds to the last character that the parser consumes.

    `sigil` should be a string of length 1, that denotes the start of the block that should be parsed.
    The ending/closing character is handled by the sigil-parser.

    `executable` is used to denote whether the returned `value` from the parser should be executed (or attempted to be).
    The <.print > from earlier could be an example of when you would use it. To enable, set it to True.
    If `executable` (remains) False, the returned `value` is instead pushed to the stack.

    `sigil` can be used as both a decorator and a function:
    # simple integer parser.
    sigil(
       simple_parser(end=" ", cast=int),
       sigil="~"
    )

    @sigil(sigil="\"")
    def stringparser(code):...
    """

    def decorator(p: Callable) -> Callable:
        if not isinstance(sigil, str):
            raise TypeError(f"`sigil` must be a string of length 1, not a {type(sigil).__name__}.")

        if len(sigil) != 1:
            raise ValueError(f"`sigil` must be a string of length 1, not {len(sigil)}.")

        if not callable(p):
            raise TypeError(f"`parser` must be callable or a function, not {type(p).__name__}.")

        if sigil in _sigils:
            raise NameError(f"`{sigil}` is already in use as a sigil.")

        _sigils[sigil] = (p, executable)

        return p

    if parser is not None:
        return decorator(parser)

    return decorator

def is_builtin(function: str) -> bool:
    """
    Returns whether the given function name is known to be executable.
    """
    return function in _builtins

def simple_parser(*, end: str, cast: Callable = lambda x: x) -> Callable[[str], tuple[Any, int]]:
    """
    Very simple interface for making a parser that ends at a character `end`.
    `cast` is applied to the parsed substring before it is returned.

    Example:
    # simple integer parser.
    sigil(
       simple_parser(end=" ", cast=int),
       sigil="~"
    )
    """

    if not isinstance(end, str):
        raise TypeError(f"`end` must be a string of length 1, not {type(end).__name__}")

    if len(end) != 1:
        raise ValueError(f"`end` must be of length 1, not {len(end)}")

    if not callable(cast):
        raise TypeError(f"`cast` must be a function/callable, not {type(cast).__name__}.")

    def parser(code: str) -> tuple[Any, int]:
        index = 1
        buff = ""
        while index < len(code) and code[index] != end:
            buff += code[index]
            index += 1
        return cast(buff), index

    return parser

def _get_builtin(f: str) -> Callable:
    if not is_builtin(f):
        raise InterpreterRuntimeError(f"`{f}` is not a recognized builtin function.")

    return _builtins[f]

def run(code: str, *, data: DataInterface | None = None) -> DataInterface:
    """
    `code` is the code that should be interpreted. It should be a string.
    `data` is the stack object that should be used. It should support `data.push(<value>)`.
    If `data` is omitted, a stack structure is used.

    For more info how the code is interpreted, see README.md.
    """

    if not isinstance(code, str):
        raise TypeError(f"`code` should be a string, not {code}.")

    if data is None:
        data = Stack()

    if not isinstance(data, DataInterface):
        raise TypeError(f"`stack` must be an instance of `StackInterface`, not {type(data).__name__}.")

    index = 0

    while index < len(code):

        # if the current character is a known sigil
        if code[index] in _sigils:

            # get the corresponding parser of the sigil and whether its result should be taken as
            # a function call
            parser, executable = _sigils[code[index]]

            # parse. v is the result, and i how many chars have been read/handled/should be skipped
            parser_res, index_offset = parser(code[index:])

            if not isinstance(index_offset, int):
                raise InterpreterRuntimeError(
                    f"parser returned ({type(parser_res).__name__}, {type(index_offset).__name__}), expected: (Any, int).")

            index += index_offset

            if index < -1:
                raise InterpreterRuntimeError(
                    f"parser returned {index_offset} as its index-offset, which caused the file pointer to be {index}, which is an illegal state.")

            if executable:
                # if the result should be executed, do so
                # by getting the corresponding function (if it exists)
                # and calling it with `data`
                # if it doesn't return None, push the value
                res = _get_builtin(parser_res)(data)
                if res is not None:
                    data.push(res)
            else:
                # otherwise push it to `data`
                data.push(parser_res)

        index += 1

    return data
