from milii import *

sigil(
    simpleparser(end=" ", cast=int),
    sigil="$"
)

sigil(
    simpleparser(end=" "),
    sigil=".",
    executable=True
)

@sigil(sigil='"')
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

@builtin
def echo(stack):
    print(stack.pop())

@builtin
def add(stack):
    a, b = stack.popn(2)
    return a + b

run(
    '$4 $5 .add .echo "Hello " "World!" .add .echo'
)