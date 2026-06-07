# testfile used for testing error functionality, this one raises several
# kinds of errors can you figure them out?

from milii import *

runtime = MiliiRuntime()

runtime.sigil(
    lambda _: (-50, ""),
    sigil="."
)

runtime.run(
    ":bskrygihniuhfufdghvdbv .hi bkuonbubbdffbvkfbjkkj"
)