from milii import *

sigil(
    simple_parser(end=" ", cast=int),
    sigil="$"
)

sigil(
    simple_parser(end=" "),
    sigil=".",
    executable=True
)

@builtin(name="+")
def add(s: Stack):
    a, b = s.popn(2)
    return a + b

@builtin(name="-")
def sub(s: Stack):
    a, b = s.popn(2)
    return a - b

@builtin(name="*")
def mul(s: Stack):
    a, b = s.popn(2)
    return a * b

@builtin(name="/")
def div(s: Stack):
    a, b = s.popn(2)
    return a / b

@builtin(name="%")
def mod(s: Stack):
    a, b = s.popn(2)
    return a % b

@builtin(name="**")
def power(s: Stack):
    a, b = s.popn(2)
    return a ** b

@builtin(name="print")
def echo(s: Stack):
    print(s.pop())

run(
    "$2 $3 .- .print"
)