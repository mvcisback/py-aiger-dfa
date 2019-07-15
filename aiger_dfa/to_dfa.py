from collections import defaultdict

import aigerbv
from bidict import bidict
from dfa import dfa2dict


def _masks2circ(io_list, in2idx, out2idx, ins):
    inv_map = defaultdict(lambda: 0)
    for in_idx, out_idx in io_list:
        inv_map[out_idx] |= (1 << in_idx)

    wordlen = len(out2idx)
    zero = aigerbv.atom(wordlen, 0, signed=False)
    result = zero
    for idx, mask in inv_map.items():
        test = (ins & mask) != 0
        _res = aigerbv.atom(wordlen, 1 << idx, signed=False)
        result |= aigerbv.ite(test, _res, zero)

    return result


def out_circ(dfa_dict, state2idx, out2idx, states):
    so_idxes = [(s, o) for s, (o, _) in dfa_dict.items()]
    result = _masks2circ(
        io_list=so_idxes, in2idx=state2idx, out2idx=out2idx, ins=states
    )
    return result.aigbv['o', {result.output: 'output'}]


def transition_circ(dfa_dict, state2idx, in2idx, inputs, states):
    inv_dyn = dict()
    for state, (_, in2state) in dfa_dict.items():
        _res = _masks2circ(
            io_list=in2state.items(), ins=inputs,
            in2idx=in2idx, out2idx=state2idx
        )
        inv_dyn[state2idx[state]] = _res

    wordlen = len(state2idx)
    zero = aigerbv.atom(wordlen, 0, signed=False)
    result = zero
    for state_idx, res in inv_dyn.items():
        test = states == (1 << state_idx)
        result |= aigerbv.ite(test, res, zero)

    return result.aigbv['o', {result.output: 'next_state'}]


def create_idx_maps(dfa):
    elem_lists = [dfa.inputs, dfa.outputs, dfa.states()]
    return [bidict(enumerate(xs)).inv for xs in elem_lists]


def is_1hot(x):
    x = aigerbv.SignedBVExpr(x.aigbv)
    test = (x != 0) & ((x & (x - 1)) == 0)
    return test.aigbv['o', {test.output: 'valid'}]


def dfa2aig(dfa):
    in2idx, out2idx, state2idx = create_idx_maps(dfa)
    dfa_dict, _ = dfa2dict(dfa)

    actions = aigerbv.atom(len(in2idx), 'action', signed=False)
    states = aigerbv.atom(len(state2idx), 'state', signed=False)

    circ = is_1hot(actions) \
        | out_circ(dfa_dict, state2idx, out2idx, states) \
        | transition_circ(dfa_dict, state2idx, in2idx, actions, states)

    start = 1 << state2idx[dfa.start]
    circ = circ.feedback(["state"], ["next_state"], initials=[start])

    relabels = {
        'inputs': in2idx.inv, 'outputs': out2idx.inv, 'states': state2idx.inv
    }
    return circ, relabels
