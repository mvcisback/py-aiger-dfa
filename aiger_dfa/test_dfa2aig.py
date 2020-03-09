from dfa import DFA

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

    in2bv = relabels['inputs'].inv

    def step(action):
        action_bv = in2bv[action]

        vout, _ = vsimulator.send({'action': action_bv})
        is_valid = vout['valid'][0]

        out, lout = simulator.send({'action': action_bv})
        label = relabels['outputs'][out['output']]
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

    vout, _ = vsimulator.send({'action': (True, True)})
    assert not vout['valid'][0]

    for i in range(5):
        _, valid, _ = step(0)
        assert not valid
