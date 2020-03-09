__all__ = ["aig2dfa"]

import aiger_bv as BV
from dfa import DFA

from aiger_dfa.utils import onehot


def aig2dfa(
        circ: BV.AIGBV,
        relabels=None,
        action_str='action',
        output_str='output',
        state_str='state',
) -> DFA:
    """
    Converts an aiger_bv.AIGBV circuit into a dfa.DFA object.

    The AIGBV circuit must have exactly 1 input, output, and latch
    which have names given by action_str, output_str, and state_str
    resp.

    relabels is dictionary with at least two entries, "inputs" and
    "outputs".

    - Each entry of relabels is a bidict that maps one-hot encoded
      tuples, e.g. (True, False, False), to dfa inputs/outputs.
    """

    assert len(circ.inputs) == 1
    assert len(circ.outputs) == 1
    assert len(circ.latches) == 1

    dummy_action = onehot(0, circ.imap[action_str].size)

    def run(state, action=None):
        if action is None:
            action = dummy_action
        elif relabels is not None:
            action = relabels['inputs'].inv[action]

        out, lout = circ({action_str: action}, latches={state_str: state})

        output = out[output_str]
        state2 = lout[state_str]

        output = output if relabels is None else relabels['outputs'][output]
        return output, state2

    if relabels is not None:
        inputs = relabels['inputs'].values()
        outputs = relabels['outputs'].values()
    else:
        imap, omap = circ.imap, circ.omap
        isize, osize = imap[action_str].size, omap[output_str].size
        inputs = {onehot(i, isize) for i in range(isize)}
        outputs = {onehot(i, osize) for i in range(osize)}

    return DFA(
        start=circ.latch2init[state_str],
        inputs=inputs,
        outputs=outputs,
        label=lambda s: run(s)[0],
        transition=lambda s, a: run(s, a)[1],
    )
