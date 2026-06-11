from milii import *
from tests import *

test = TestEnv()

@test.add
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

@test.add
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

# not creative enough for tests for Milii.run and simple_parser

if __name__ == "__main__":
    test.activate(test_builtin)
    test.activate(test_sigil)

    test.run_tests()