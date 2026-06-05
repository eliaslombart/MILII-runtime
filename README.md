# MILII - a minimal interpreted language infrastructure

## In short

MILII is a (interpreted) language infrastructure, meant to be used to create simple toy languages, or automate specific niche workflows.
That does not mean that it can't be used for other purposes though.
It is important to note that MILII only handles syntax, not the actual implementation of whatever uses it.

## Installation & examples

To install, simply clone the repository and `import` into your python project.

```sh
git clone https://github.com/eliaslombart/MILII-runtime.git
```

```python
import milii/src/milii
```

Examples can be found in the `examples` directory.

## Technical overview

MILII is explained as a sigil-based language, although it can be argued to be a circumfix-based one. The reason for this architecture is that this foregoes actual tokenizing. Instead, the parser can read character by character until it reaches a known sigil, at which point it dispatches the according subparser. After the subparser is done, the main parser resumes where the subparser left off.
The user can define new sigils and functions (called builtins) before and during runtime, both are global, as there is no local-scope.
A sigil can be marked as `executable`, which effectively communicates to the parser that it should at least attempt to execute the returned value as a command.
