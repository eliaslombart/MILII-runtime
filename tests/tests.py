from typing import Callable
from time import time

Test = Callable[[], None]

class TestFunction:
    def __init__(self, *, function: Test, active: bool, repeat: int) -> None:
        self.function: Test = function
        self.active: bool = active
        self.repeat: int = repeat

    def is_active(self) -> bool:
        return self.active

    def __bool__(self) -> bool:
        return self.active

    def matches(self, other: Test) -> bool:
        return self.function is other

    def __eq__(self, other: Test) -> bool:
        return self.function is other

    def run(self) -> None:
        for _ in range(self.repeat): self.function()

def _warmup_generator(duration: int) -> Test:
    def warmup() -> None:
        start = time()
        while time() - start < duration:
            ...

    return warmup

class TestEnv:
    def __init__(self, *, warmup: bool=False, warmup_time_seconds: int=15):
        self._tests = {}

        if warmup:
            self.add(
                _warmup_generator(warmup_time_seconds),
                active=True
            )

    def add(self, function: Test | None = None, *, active: bool = False, repeat: int = 1) -> Test | Callable[[Test], Test]:
        def decorator(func: Test) -> Test:
            self._tests[func] = TestFunction(function=func, active=active, repeat=repeat)
            return func

        if function is None:
            return decorator

        return decorator(function)

    def activate(self, function: Test):
        self._tests[function].active = True

    def run_tests(self) -> None:
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