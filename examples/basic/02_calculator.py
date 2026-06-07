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

@runtime.builtin(name="+")
def add(s: Stack):
    a, b = s.popn(2)
    return a + b

@runtime.builtin(name="-")
def sub(s: Stack):
    a, b = s.popn(2)
    return a - b

@runtime.builtin(name="*")
def mul(s: Stack):
    a, b = s.popn(2)
    return a * b

@runtime.builtin(name="/")
def div(s: Stack):
    a, b = s.popn(2)
    return a / b

@runtime.builtin(name="%")
def mod(s: Stack):
    a, b = s.popn(2)
    return a % b

@runtime.builtin(name="**")
def power(s: Stack):
    a, b = s.popn(2)
    return a ** b

@runtime.builtin(name="print")
def echo(s: Stack):
    print(s.pop())

runtime.run(
    "$2 $3 .- .print"
)