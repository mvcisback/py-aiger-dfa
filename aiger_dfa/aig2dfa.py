from __future__ import annotations

from itertools import product, repeat
from typing import Any, Union, Optional, Tuple, Mapping, Literal

import aiger
import aiger_bv as BV
from bidict import bidict
from dfa import DFA
from pyrsistent import pmap
from pyrsistent.typing import PMap


Kinds = Union[Literal['inputs'], Literal['outputs'], Literal['states']]
Encoding = Mapping[str, bidict]  # Bijective Mapping[str, bitvector]]
Encodings = Mapping[Kinds, Encoding]
State = Tuple[PMap[str, Any], PMap[str, Any]]  # (prev_output, latch_val).


def default_encoding(bmap, is_output=False):
    enc = {}
    flatten = (zip(repeat(k), range(1 << size)) for k, size in bmap.items())
    for elems in product(*flatten):
        decoded = pmap({
            k: tuple(BV.encode_int(bmap[k].size, v, signed=False))
            for k, v in elems
        })
        enc[decoded] = decoded
    return enc


def aig2dfa(
        circ: BV.AIGBV,
        relabels: Encodings = pmap(),
        initial_label: Optional[Any] = None,
        output_name = None
) -> DFA:
    """
    Converts an AIG circuit into a dfa.DFA object.

    Note that circuits are generally Mealy Machines
       - i.e., label depends on input & state.

    If the initial output is not included, the initial label is None.

    Relabels is an optional mapping with 'inputs' and 'outputs' keys.
     - 'inputs' indexes a mapping from dfa inputs to (pmap) aiger inputs.
     - 'outputs' indexes a mapping from (pmap) aiger outputs to dfa outputs.
        * If output_name is provided, that output will be used.
        * Else if only one output exists, that output will be used.
        * Else If more than one output exists and `output_name` isn't provided,
          then the output named 'output' will be used.
        * If none of those cases apply, a value error will be raised.
     - pmap = pyrsistent.pmap

    Returns:
      A returned DFA is the Moore machine encoding of this Mealy
      Machine. This means that the state includes the previous output.
    """
    if isinstance(circ, aiger.AIG):
        circ = BV.aig2aigbv(circ)

    # Determine which circuit output is the DFA's output.
    if output_name is None:
        if 'output' in circ.omap:
            output_name = 'output'
        elif len(circ.omap.keys()) != 1:
            raise ValueError("The provided circuit has ambiguous output.")
        else:
            output_name, *_ = circ.omap.keys()

    # Set default translations from binary to DFA inputs/outputs.
    if 'inputs' not in relabels:
        relabels = relabels.set('inputs', default_encoding(circ.imap))
    if 'outputs' not in relabels:
        omap = circ.omap.project([output_name])
        relabels = relabels.set('outputs', default_encoding(omap))

    def transition(state, action):
        action = relabels['inputs'][action]
        omap, lmap = circ(action, latches=state[1])
        output = relabels['outputs'][pmap({'output': omap[output_name]})]
        return output, pmap(lmap)

    outputs = set(relabels['outputs'].values())

    if initial_label is None:
        outputs.add(None)

    return DFA(
        start=(initial_label, pmap(circ.latch2init)),
        inputs=relabels['inputs'].keys(),
        outputs=outputs,
        label=lambda s: s[0],
        transition=transition,
    )


__all__ = ["aig2dfa", "State"]
