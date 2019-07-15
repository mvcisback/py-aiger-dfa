# py-aiger-dfa
Python library for converting between AIG circuits and DFAs.

# Installation

If you just need to use `aiger_dfa`, you can just run:

`$ pip install py-aiger-dfa`

For developers, note that this project uses the
[poetry](https://poetry.eustace.io/) python package/dependency
management tool. Please familarize yourself with it and then
run:

`$ poetry install`

# Usage

The main entry points for using this library are the `dfa2aig` and
`aig2dfa` functions. DFAs are represented using the
[dfa](https://github.com/mvcisback/dfa) package. Familiarity with the
`dfa`, `py-aiger`, and `py-aiger-bv` packages is assumed.


## DFA to AIG

An example of going from a `DFA` to an `AIG` object
is shown below.

```python
from dfa import DFA
from aiger_dfa import aig2dfa, dfa2aig

my_dfa = DFA(
    start=0,
    inputs={0, 1},
    label=lambda s: (s % 4) == 3,
    transition=lambda s, c: (s + c) % 4,
)
my_aig, relabels = dfa2aig(my_dfa)
```

Now `circ` is an `AIG` and `relabels` is a mapping from the inputs,
states, and outputs of `my_dfa` to their **1-hot** encoded
counterparts in `my_aig`.

## AIG to DFA

TODO
