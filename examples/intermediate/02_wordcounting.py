# toy example that demonstrates a more "realistic" implementation
# in reality, a lot more error handling should be done, but I don't believe it's
# important enough, as it would clutter the code

from milii import *

rt = MiliiRuntime()

# command parser
rt.sigil(
    simple_parser(end=" "),
    sigil=".",
    executable=True
)

# integer parser
rt.sigil(
    simple_parser(end=" ", cast=int),
    sigil="$"
)

# string parser
@rt.sigil(sigil='"')
def stringparser(code):
    index = 1
    buff = []

    while index < len(code):
        char = code[index]
        if char == '"':
            break

        if char == "\\" and index < len(code) -1:
            index += 1
            char = code[index]

        buff.append(char)
        index += 1

    return "".join(buff), index

@rt.builtin(name="open")
def fileopen(data):
    fname = data.pop()

    data.push(
        open(fname).read()
    )

@rt.builtin
def dup(data):
    x = data.pop()
    data.push_all([x, x])

rt.builtin(lambda data: print(data.pop()), name="print")

@rt.builtin
def count_symbols(data):
    symbols = {}

    for char in data.pop():
        if char not in symbols:
            symbols[char] = 0

        symbols[char] += 1

    data.push(tuple(symbols.items()))

@rt.builtin(name="filter")
def filter_most_common(data):
    data, number = data.popn(2)

    return ", ".join(str(elem) for elem in sorted(data, key=lambda x: x[1], reverse=True)[:number])

@rt.builtin
def add(data):
    a, b = data.popn(2)
    return a + b

@rt.builtin
def rev(data):
    a, b = data.popn(2)
    data.push(b)
    data.push(a)

rt.run(
    '"./02_wordcounting.py" .dup "Most common symbols in " .rev .add ":" .add .print .open .count_symbols $5 .filter .print'
)