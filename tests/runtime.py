from runtime import *
from tests import *

tests = TestEnv()

@tests.add
def test_builtin():
    rt = MiliiRuntime()

    @rt.builtin
    def test(): ...

    assert_error(
        rt.builtin,
        (test,),
        NameError
    )

    assert rt.is_builtin("test")

@tests.add
def test_sigil():
    rt = MiliiRuntime()

    @rt.sigil(sigil=".")
    def test(): ...

    try:
        rt.sigil(test, sigil=".")
    except NameError:
        pass
    else:
        raise AssertionError()

@tests.add
def test_simple_parser():
    parser = simple_parser(end=" ")

    # since parsers are supposed to be sigil-based, the '%' is skipped by simple parser
    # simple-parser does not raise an error here as the `end`-parameter is more of a seperator that
    # a hard ending
    assert parser("%Hello!") == ("Hello!", 7)
    assert parser("%Hello %World!") == ("Hello", 6)

    try: simple_parser(end=0)
    except TypeError: ...
    else: raise AssertionError()

    try: simple_parser(end="  ")
    except ValueError: ...
    else: raise AssertionError()

    try: simple_parser(end="")
    except ValueError: ...
    else: raise AssertionError()

    try: simple_parser(end=" ", cast="")
    except TypeError: ...
    else: raise AssertionError()

@tests.add
def test_runtime():
    # short test, could probably do with some checking of faulty parameters (but it should be fine)

    rt = MiliiRuntime()

    rt.sigil(
        simple_parser(end=" "),
        sigil=".",
        executable=True
    )

    @rt.builtin(name="test")
    def test(_): return 25

    assert rt.run(".test ").pop() == 25

if __name__ == "__main__":
    tests.activate(test_builtin)
    tests.activate(test_sigil)
    tests.activate(test_simple_parser)
    tests.activate(test_runtime)

    tests.run_tests()