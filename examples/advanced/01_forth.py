# this file contain a (limited) implementation of the forth programming language.
# the code might not be the prettiest, but it is a proof of concept after all

# there might be many bugs as well, but this is more of a proof of concept, rather
# than making something that is actually useful/stable

import string
from milii import *

rt = MiliiRuntime()
command_chars = ".+-*/<" + string.ascii_uppercase
run_now = [True]

# determines if code should be run now
def can_run():
    return run_now[-1]

# helper function to allow multiple sigils for the same parser
def multi_parser(sigils, parser, executable=False):
    for sigil in sigils:
        rt.sigil(parser, sigil=sigil, executable=executable)

# function that adds new functions
def add_function(code):
    code = code.split(" ")

    name = code[1]
    code = " ".join(code[2:])

    def function_scope_run(stack):
        sub_rt = MiliiRuntime(rt)
        sub_rt.run(code, data=stack)

    rt.builtin(function_scope_run, name=name)

# integer parser
def integer_parser(code):
    index = 0
    buff = []

    for char in code:
        if char not in "0123456789":
            break

        buff.append(char)
        index += 1

    if not can_run():
        return None, index

    return int("".join(buff)), index

# command/syntax parser
def command_parser(code):
    index = 0
    buff = []
    for char in code:
        if char not in command_chars + "0123456789":
            break
        buff.append(char)
        index += 1

    return "".join(buff), index

# parser for functions:
rt.sigil(
    simple_parser(end=";", cast=add_function),
    sigil=":"
)

multi_parser(command_chars, command_parser, executable=True)
multi_parser("0123456789", integer_parser)

def conditional_builtin(function = None):
    def decorator(func):
        def wrapper(data):
            if can_run():
                return func(data)
        return wrapper

    if function is None:
        return decorator

    return decorator(function)

@rt.builtin(name="+")
@conditional_builtin
def add(stack):
    a, b = stack.popn(2)
    return a + b

@rt.builtin(name="-")
@conditional_builtin
def sub(stack):
    a, b = stack.popn(2)
    return a - b

@rt.builtin(name="*")
@conditional_builtin
def mul(stack):
    a, b = stack.popn(2)
    return a * b

@rt.builtin(name="/")
@conditional_builtin
def div(stack):
    a, b = stack.popn(2)
    return a / b

@rt.builtin(name="MAX")
@conditional_builtin
def MAX(stack):
    a, b = stack.popn(2)
    return max(a, b)

@rt.builtin(name="<")
@conditional_builtin
def lt(stack):
    a, b = stack.popn(2)
    return a < b

@rt.builtin(name="IF")
@conditional_builtin
def IF(stack):
    a = stack.pop()
    if not a:
        run_now.append(False)
    else:
        run_now.append(True)

@rt.builtin(name="ELSE")
def ELSE(stack):
    run_now[-1] = not run_now[-1]

@rt.builtin(name="THEN")
def THEN(stack):
    run_now.pop(-1)

@rt.builtin(name=".")
@conditional_builtin
def printer(stack):
    print(stack.pop())

@rt.builtin(name="DUP")
@conditional_builtin
def dup(stack):
    x = stack.pop()
    stack.push_all([x, x])

@rt.builtin(name="DROP")
@conditional_builtin
def drop(stack):
    stack.pop()

# the example from the wiki: https://en.wikipedia.org/wiki/Forth_(programming_language)#Overview
rt.run(
    ": FLOOR5 DUP 6 < IF DROP 5 ELSE 1 - THEN ; 4 FLOOR5 . 7 FLOOR5 ."
)
