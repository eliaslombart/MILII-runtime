# MILII - a minimal interpreted language infrastructure

A minimal sigil-based interpreter framework for building toy languages and DSLs.

## In short

Parsing is delegated to user-defined sigils that can be registered before or during execution, allowing the language syntax and behavior to be extended dynamically. MILII does not come shipped with any built-in runtime functions, those should be defined and/or implemented by the user themselves.

## A quick example

```python
from milii import *

# define a milii runtime
runtime = MiliiRuntime()

# integer parser
runtime.sigil(
    simple_parser(end=" ", cast=int),
    sigil="%"
)

# command parser
runtime.sigil(
    simple_parser(end=" "),
    sigil=".",
    executable=True
)

# string parser
@runtime.sigil(sigil='"')
def stringparser(code):
    index = 1
    buffer = []
    while index < len(code):
        char = code[index]

        if char == code[0]:
            break

        if char == "\\" and index < len(code) -1:
            index += 1
            char = code[index]
            
        buffer.append(char)

        index += 1

    return "".join(buffer), index

runtime.sigil(
    stringparser,
    sigil="'"
)

# add function
@runtime.builtin()
def add(data):
    a, b = data.popn(2)
    return a + b

# print function
runtime.builtin(
    lambda data: print(data.pop()),
    name="echo"
)

# run
runtime.run(
    '%1 %2 .add .echo "\\"Hello " \'world!\\"\' .add .echo'
)
```

## Installation & more examples

To install the latest version:
```bash
pip install git+https://github.com/eliaslombart/MILII-runtime.git
```

If you want the entire source code/run some examples, you can clone the repository:
```shell
git clone https://github.com/eliaslombart/MILII-runtime.git
```

Fully-fledged examples can be found in the `examples` directory.

## Technical overview

MILII is best explained as a sigil-based language, although it can be argued to be a circumfix-based one. The reason for this architecture is that this avoids a tokenizing step. Instead, the parser can read character by character until it reaches a known sigil, at which point it dispatches the corresponding subparser. After the subparser is done, the main parser resumes where the subparser left off.
The user can define new sigils and functions (called builtins) before and during runtime. Several scopes are possible by using several MiliiRuntime instances.
A sigil can be marked as `executable`, which effectively communicates to the parser that it should at least attempt to execute the returned value as a command.
