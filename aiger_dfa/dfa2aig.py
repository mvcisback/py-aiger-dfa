__all__ = ["dfa2aig"]

import aiger_bv
import aiger_bv as BV
import aiger_ptltl as PLTL
from bidict import bidict
from dfa import dfa2dict, DFA
from pyrsistent import pmap

from aiger_dfa.utils import onehot


def dfa2aig(dfa: DFA):
    """
    Takes a dfa.DFA object and returns a tuple of:

    1. An aiger_bv.AIGBV circuit modeling the DFA's labeling and
       transitions.  This circuit has 1 input, 2 outputs, and 1 latch
       called "action", 'prev_output', "output", "prev_state" and "state" respectively.

    2. A dictionary with at three entries, "inputs", "outputs", and
    "states".

      - Each entry is a nested dictionary.
      - The first dictionary maps input/output/state names
        to encodings.
      - The encoding dictionary is mapping to/from dfa inputs,
        outputs, states and the corresponding aiger inputs, outputs,
        latches.

    3. An aiger_bv.AIGBV circuit which monitors is all inputs are
       valid, e.g., one_hot encoded.
    """
    in2bv, out2bv, state2bv = create_bv_maps(dfa)
    dfa_dict, _ = dfa2dict(dfa)

    action = BV.uatom(len(dfa.inputs), 'action')
    state = BV.uatom(len(dfa.states()), 'state')
    next_state = BV.uatom(len(dfa.states()), 'next_state')

    circ = transition_circ(dfa_dict, state2bv, in2bv, action, state)
    circ |= out_circ(dfa_dict, state2bv, out2bv, state, 'prev_output')
    start = state2bv[dfa.start]

    circ = circ.loopback({
        "input": "state",
        "output": "next_state",
        "init": start,
        "keep_output": True,
    })
    circ >>= out_circ(dfa_dict, state2bv, out2bv, next_state, 'output')

    relabels = {
        'inputs': {k: pmap({'action': v}) for k, v in in2bv.items()},
        'outputs': {pmap({'output': v}): k for k, v in out2bv.items()},
        'states': {k: pmap({'state': v}) for k, v in state2bv.items()},
    }

    return circ, relabels, valid_circ(action)


def out_circ(dfa_dict, s2bv, o2bv, state, output):
    state2label = {
        BV.decode_int(s2bv[s], False): BV.decode_int(o2bv[l], False)
        for s, (l, _) in dfa_dict.items()
    }
    tbl = BV.lookup(
        input=state.output,
        inlen=state.size,
        in_signed=False,
        output=output,
        outlen=len(o2bv),            # One hot encoding.
        out_signed=False,

        mapping=state2label,
    )
    return state.aigbv >> tbl


def transition_circ(dfa_dict, s2bv, a2bv, action, state):
    state_action = state.concat(action)

    flattened = {}
    n_states = len(dfa_dict)
    for start, (_, mapping) in dfa_dict.items():
        start = BV.decode_int(s2bv[start], False)
        for action, end in mapping.items():
            end = BV.decode_int(s2bv[end], False)
            action = BV.decode_int(a2bv[action], False)

            flattened[start | (action << n_states)] = end

    tbl = BV.lookup(
        input=state_action.output,
        inlen=state_action.size,
        in_signed=False,

        output="next_state",
        outlen=state.size,             # output: next state
        out_signed=False,

        mapping=flattened,
    )
    return state_action.aigbv >> tbl


def is_1hot(x):
    x = aiger_bv.SignedBVExpr(x.aigbv)
    test = (x != 0) & ((x & (x - 1)) == 0)
    return test.aigbv['o', {test.output: 'valid'}]


def valid_circ(action):
    hist_valid = PLTL.atom('valid').historically().with_output('valid')
    hist_valid = aiger_bv.aig2aigbv(hist_valid.aig)

    return is_1hot(action) >> hist_valid


def _sym2bv(syms):
    size = len(syms)
    return bidict({sym: onehot(i, size) for i, sym in enumerate(syms)})


def create_bv_maps(dfa):
    return map(_sym2bv, [dfa.inputs, dfa.outputs, dfa.states()])
