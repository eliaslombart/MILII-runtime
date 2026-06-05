from milii import *

# used for saving variables
variables = {}

# simple class boilerplate
class Variable:
    def __init__(self, value):
        self.value = value

class GetVar:
    def __init__(self, value):
        self.value = value

# int parser
sigil(
    simple_parser(end=" ", cast=int),
    sigil="%"
)

# executables
sigil(
    simple_parser(end=" "),
    sigil=".",
    executable=True
)

# definitions
sigil(
    simple_parser(end=">", cast=Variable),
    sigil="<"
)

# getting the value of a variable
sigil(
    simple_parser(end=" ", cast=GetVar),
    sigil="$"
)

# command that assigns a value to a variable
@builtin
def let(stack):
    val, name = stack.popn(2)

    if not isinstance(name, Variable):
        stack.push_all([val, name])

    if isinstance(val, GetVar):
        val = variables[val.value]

    variables[name.value] = val

# prints a value, which might be a variable
@builtin
def echo(stack):
    val = stack.pop()

    if isinstance(val, GetVar):
        val = variables[val.value]

    print(val)

run(
    "%5 .echo %6 <int> .let $int .echo"
)