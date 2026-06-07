from milii import *

runtime = MiliiRuntime()

runtime.sigil(
    simple_parser(end=" ", cast=int),
    sigil="$"
)

runtime.sigil(
    simple_parser(end=" "),
    sigil=".",
    executable=True
)

@runtime.sigil(sigil='"')
def string_parser(code):
    index = 1
    buffer = ""

    while index < len(code):
        if code[index] == '"':
            break

        if code[index] == "\\":
            index += 1

        if index >= len(code):
            break

        buffer += code[index]

        index += 1

    return buffer, index

@runtime.builtin
def echo(stack):
    print(stack.pop())

@runtime.builtin
def add(stack):
    a, b = stack.popn(2)
    return a + b

runtime.run(
    '$4 $5 .add .echo "Hello " "World!" .add .echo'
)