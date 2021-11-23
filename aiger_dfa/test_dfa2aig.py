from dfa import DFA, dict2dfa
from pyrsistent import pmap

from aiger_dfa import dfa2aig


def test_dfa2aig():
    dfa1 = DFA(
        start=0,
        inputs={0, 1},
        label=lambda s: (s % 4) == 3,
        transition=lambda s, c: (s + c) % 4,
    )
    circ, relabels, valid = dfa2aig(dfa1)
    simulator = circ.simulator()
    vsimulator = valid.simulator()
    next(simulator)
    next(vsimulator)

    in2bv = relabels['inputs']

    def step(action):
        action_bv = in2bv[action]

        vout, _ = vsimulator.send(action_bv)
        is_valid = vout['valid'][0]

        out, lout = simulator.send(action_bv)
        label = relabels['outputs'][pmap({'output': out['prev_output']})]
        return label, is_valid, lout['state']

    prev_state = circ.latch2init['state']
    for i in range(5):
        label, valid, state = step(0)
        assert valid
        assert state == prev_state
        assert dfa1.label((0,)*i) == label

    for i in range(5):
        label, valid, state = step(1)
        assert valid
        assert dfa1.label((1,)*i) == label

    # One invalid input should invalidate the run.

    vout, _ = vsimulator.send({'action': 0b11})
    assert not vout['valid'][0]

    for i in range(5):
        _, valid, _ = step(0)
        assert not valid


