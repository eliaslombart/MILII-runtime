from milii import Stack
from tests import TestEnv

benchmark = TestEnv(
    warmup=True,
    warmup_time_seconds=15
)

@benchmark.add(repeat=15)
def test_push_pop():
    stack = Stack()
    item_sz = 500_000

    for i in range(item_sz):
        stack.push(i)

    res = stack.pop_all()
    assert res == tuple(range(item_sz))

    stack.push_all(range(item_sz))

    res = []
    while len(stack) > 0:
        res.append(stack.pop())

    assert res == list(range(item_sz -1, -1, -1))

@benchmark.add(repeat=15)
def test_equality():
    test_sz = 500_000

    stack1 = Stack()
    stack2 = Stack()
    assert stack1 == stack2

    stack1 = Stack(data=range(test_sz))
    stack2 = Stack(data=range(test_sz))
    assert stack1 == stack2

    stack1.pop()
    assert stack1 != stack2

    stack1.push(-1)
    assert stack1 != stack2

if __name__ == '__main__':
    benchmark.activate(test_push_pop)
    benchmark.activate(test_equality)

    benchmark.run_tests()