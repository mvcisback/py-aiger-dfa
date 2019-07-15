from dfa import DFA

from aiger_dfa import dfa2aig


def test_dfa2aig():
    dfa1 = DFA(
        start=0,
        inputs={0, 1},
        label=lambda s: (s % 4) == 3,
        transition=lambda s, c: (s + c) % 4,
    )
    circ, relabels = dfa2aig(dfa1)
    simulator = circ.simulator()
    next(simulator)
    for i in range(5):
        out, _ = simulator.send({'action': 1})
        assert out['valid'] == (True,)
        label = relabels['outputs'][out['output'].index(True)]
        assert dfa1.label((0,)*i) == label

    for i in range(5):
        out, state = simulator.send({'action': 2})
        assert out['valid'] == (True,)
        label = relabels['outputs'][out['output'].index(True)]
        assert dfa1.label((1,)*i) == label
