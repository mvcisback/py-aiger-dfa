from __future__ import annotations

from itertools import product, repeat
from typing import Any, Union, Optional, Tuple, Mapping, Literal

import aiger_bv as BV
from bidict import bidict
from dfa import DFA
from pyrsistent import pmap
from pyrsistent.typing import PMap


Kinds = Union[Literal['inputs'], Literal['outputs'], Literal['states']]
Encoding = Mapping[str, bidict]  # Bijective Mapping[str, bitvector]]
Encodings = Mapping[Kinds, Encoding]
State = Tuple[PMap[str, Any], PMap[str, Any]]  # (prev_output, latch_val).


def alphabet(enc: Encoding, add_None=False):
    flatten = (zip(repeat(k), v.keys()) for k, v in enc.items())
    yield from map(pmap, product(*flatten))

    if add_None:
        yield None


def default_encoding(bundle_map):
    enc = {}
    for name, size in bundle_map:
        enc[name] = {i: i for i in range(1 << size)}
    return enc


def aig2dfa(
        circ: BV.AIGBV,
        relabels: Encodings = pmap(),
        initial_label: Optional[Any] = None,
) -> DFA:
    """
    Converts an AIG circuit into a dfa.DFA object.

    Note that circuits are generally Mealy Machines
       - i.e., label depends on input & state.

    The returned DFA is the Moore machine encoding of this Mealy
    Machine. This means that the state includes the previous output.

    If the initial output is not included, the initial label is None.
    """
    if 'inputs' not in relabels:
        relabels = relabels.set('inputs', default_encoding(circ.imap))
    if 'outputs' not in relabels:
        relabels = relabels.set('outputs', default_encoding(circ.omap))

    def transition(state, action):
        action = {k: relabels['inputs'][k][v] for k, v in action.items()}
        omap, lmap = circ(action, latches=state[1])
        omap = {k: relabels['outputs'][k].inv[v] for k, v in omap.items()}
        return pmap(omap), pmap(lmap)

    return DFA(
        start=(initial_label, pmap(circ.latch2init)),
        inputs=alphabet(relabels['inputs']),
        outputs=alphabet(relabels['outputs'], add_None=initial_label is None),
        label=lambda s: s[0],
        transition=transition,
    )


__all__ = ["aig2dfa", "State"]
