# py-aiger-dfa
Python library for converting between AIG circuits and DFAs.

[![Build Status](https://cloud.drone.io/api/badges/mvcisback/py-aiger-dfa/status.svg)](https://cloud.drone.io/mvcisback/py-aiger-dfa)
[![Docs](https://img.shields.io/badge/API-link-color)](https://mvcisback.github.io/py-aiger-dfa)
[![codecov](https://codecov.io/gh/mvcisback/py-aiger-dfa/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/py-aiger-dfa)
[![PyPI version](https://badge.fury.io/py/py-aiger-dfa.svg)](https://badge.fury.io/py/py-aiger-dfa)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->
**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
    - [DFA to AIG](#dfa-to-aig)
    - [AIG to DFA](#aig-to-dfa)

<!-- markdown-toc end -->


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
from aiger_dfa import dfa2aig

my_dfa = DFA(
    start=0,
    inputs={0, 1},
    label=lambda s: (s % 4) == 3,
    transition=lambda s, c: (s + c) % 4,
)
my_aig, relabels, valid = dfa2aig(my_dfa)
```

Now `circ` is an `AIG` and `relabels` is a mapping from the inputs,
states, and outputs of `my_dfa` to their **1-hot** encoded
counterparts in `my_aig`.

`relabels` has the following schema:

```python
relabels = {
    'inputs': .. , # Bidict from 1-hot encoded tuple to dfa input.
    'outputs': .. , # Bidict from 1-hot encoded tuple to dfa output.
    'states': .. , # Bidict from 1-hot encoded tuple to dfa state.
}
```

where `bidict` refers to https://bidict.readthedocs.io/en/master/.
Finally, `valid` is another aiger circuit which tests if all inputs
are 1-hot encoded.

## AIG to DFA

The inverse of `dfa2aig` is `aig2dfa`. Using the same example.

```python
from aiger_dfa import aig2dfa

my_dfa2 = aig2dfa(my_aig, relabels=relabels)

assert my_dfa2.label((1,0,0,1,1,0)) == my_dfa.label((1,0,0,1,1,0))
```
