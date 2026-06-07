# MILII - a minimal interpreted language infrastructure

A minimal sigil-based interpreter framework for building toy languages and DSLs.

## In short

Parsing is delegated to user-defined sigils that can be registered before or during execution, allowing the language syntax and behavior to be extended dynamically. MILII does not come shipped with any built-in runtime functions, those should be defined and/or implemented by the user themselves.

## A quick example

```python
from milii import *

# integer parser
sigil(
    simple_parser(end=" ", cast=int),
    sigil="%"
)

# command parser
sigil(
    simple_parser(end=" "),
    sigil=".",
    executable=True
)

# string parser
@sigil(sigil='"')
def stringparser(code):
    index = 1
    buffer = ""
    while index < len(code):
        char = code[index]

        if char in '"\'':
            break

        if char == "\\" and index < len(code) -1:
            index += 1
            char = code[index]
            
        buffer += code[index]

        index += 1

    return buffer, index + 1

sigil(
    stringparser,
    sigil="'"
)

# add function
@builtin()
def add(data):
    a, b = data.popn(2)
    return a + b

# print function
builtin(
    lambda data: print(data.pop()),
    name="echo"
)

# run
run(
    '%1 %2 .add .echo "Hello " \'world!"\' .add .echo'
)
```

## Installation & more examples

To install, simply clone the repository, move `milii.py` to your project and import it.

```shell
git clone https://github.com/eliaslombart/MILII-runtime.git
```

Fully-fledged examples can be found in the `examples` directory.

## Technical overview

MILII is explained as a sigil-based language, although it can be argued to be a circumfix-based one. The reason for this architecture is that this avoids a tokennizing step. Instead, the parser can read character by character until it reaches a known sigil, at which point it dispatches the corresponding subparser. After the subparser is done, the main parser resumes where the subparser left off.
The user can define new sigils and functions (called builtins) before and during runtime, both are global, as there is no local-scope.
A sigil can be marked as `executable`, which effectively communicates to the parser that it should at least attempt to execute the returned value as a command.
