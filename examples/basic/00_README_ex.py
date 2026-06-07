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