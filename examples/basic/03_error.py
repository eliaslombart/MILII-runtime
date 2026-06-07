# file used for testing error functionality, this one raises several
# kinds of errors can you figure them out?

from milii import *

runtime = MiliiRuntime()

runtime.sigil(
    lambda _:  (-50, ""),
    sigil="."
)

runtime.sigil(
    simple_parser(end=" "),
    sigil="%",
    executable=True
)

runtime.run(
    ":verylongsequenceofcharacters .hi %anotherverylongsequenceofcharactersonlythistimeactuallyrelevant"
)