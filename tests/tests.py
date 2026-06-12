from typing import Callable, Any
from time import time

Test = Callable[[], None]

def assert_error(function: Callable[[Any, ...], Any], args: tuple[Any], err: type[Exception] = Exception) -> None:
    """
    Function that takes a function `function`, and the positional arguments `args` to be tested.
    The function calls `function` with the arguments, and if the Exception `err` is not raised, the function will raise an AssertionError.
    """

    try:
        function(*args)
    except err:
        return

    raise AssertionError()

class TestFunction:
    """
    Dataclass used to hold information about registered test functions.
    It holds:
        - a reference to the test (TestFunction.function)
        - whether the test will be run (TestFunction.active)
        - how many times it is to be called (TestFunction.repeat)

    It has the following methods:
        - is_active()   returns whether the test is active
        - matches()     returns whether the registered test matches another one
        - run()         runs the test `TestFunction.repeat` times
    """
    def __init__(self, *, function: Test, active: bool, repeat: int) -> None:
        if not callable(function):
            raise TypeError(f"`function` must be callable, not {type(function).__name__}.")

        if not isinstance(active, bool):
            raise TypeError(f"`active` must be bool, not {type(active).__name__}.")

        if not isinstance(repeat, int):
            raise TypeError(f"`repeat` must be int, not {type(repeat).__name__}.")

        if repeat < 1:
            raise ValueError(f"`repeat` must be >= 1, not {repeat}.")

        self.function: Test = function
        self.active: bool = active
        self.repeat: int = repeat

    def is_active(self) -> bool:
        """returns whether the test is active"""
        return self.active

    def __bool__(self) -> bool:
        return self.active

    def matches(self, other: Test) -> bool:
        """returns whether the registered test matches the other test"""
        return self.function is other

    def __eq__(self, other: Test) -> bool:
        return self.function is other

    def run(self) -> None:
        """run the test `TestFunction.repeat` times"""
        if self.repeat < 0:
            raise ValueError(f"Cannot repeat a function {self.repeat} times.")

        for _ in range(self.repeat): self.function()

def warmup_generator(duration: int) -> Test:
    """Function that returns a warmup function that lasts `duration` seconds.`"""

    def warmup() -> None:
        start = time()
        while time() - start < duration:
            ...

    return warmup

class TestEnv:
    """
    Environment for running unit tests.
    New tests can be added using the `TestEnv.add` method. Tests may be automatically activated, and can be run a repeated number of times.
    Tests can be activated or deactivated using the `TestEnv.activate` and `TestEnv.deactivate` methods.
    """

    def __init__(self, *, warmup: bool=False, warmup_time_seconds: int=15):
        self._tests = {}

        if warmup:
            self.add(
                warmup_generator(warmup_time_seconds),
                active=True
            )

    def add(self, function: Test | None = None, *, active: bool = False, repeat: int = 1) -> Test | Callable[[Test], Test]:
        """adds a test function to the environment"""
        def decorator(func: Test) -> Test:
            self._tests[func] = TestFunction(function=func, active=active, repeat=repeat)
            return func

        if function is None:
            return decorator

        return decorator(function)

    def activate(self, function: Test):
        """activate a test function"""
        self._tests[function].active = True

    def deactivate(self, function: Test):
        """deactivates a test function"""
        self._tests[function].active = False

    def run_tests(self) -> None:
        """runs all tests"""

        for test in self._tests.values():
            if test.is_active():
                print(f"Test {test.function.__name__}: ", end="")
                t0 = time()
                test.run()
                t1 = time()
                print(f"{t1 - t0:.2f}s", end="")

                if test.repeat > 1:
                    print(f" -> {(t1 - t0)/test.repeat:.2f}s/test ({test.repeat})")
                else:
                    print()